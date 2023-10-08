from datetime import datetime, time
from enum import Enum
from typing import Dict, Optional
import pandas as pd

from pydantic import BaseModel, field_validator, model_validator


class Side(Enum):
  Left = 0
  Right = 1

  def __add__(self, other):
    return other + self.value
  
  def __eq__(self, other):
    if type(other) == int:
      return other == self.value
    else:
       return other.value == self.value

class Team(BaseModel):
  id: int
  name: str
  triCode: str

class Player(BaseModel):
  id: int
  fullName: str

class PlayerEvent(BaseModel):
  player: Player
  playerType: str

class Coordinates(BaseModel):
  x: float = None
  y: float = None

class PlayDetails(BaseModel):
  eventIdx: int
  dateTime: datetime
  period: int # > 3 overtime
  periodTime: time
  periodTimeRemaining: time
  away_goals: int
  home_goals: int

  @model_validator(mode='before')
  def extract_goals(cls, values):
      goals = values.pop('goals', {})
      values['away_goals'] = goals.get('away')
      values['home_goals'] = goals.get('home')
      return values

  @field_validator('periodTime', mode='before')
  def period_time(cls, value):
      return datetime.strptime(value, "%M:%S").time()

  @field_validator('periodTimeRemaining', mode='before')
  def period_time_remaining(cls, value):
      return datetime.strptime(value, "%M:%S").time()

class PlayResult(BaseModel):
  event: str
  secondaryType: str = ''
  description: str = ''
  strength: str
  emptyNet: Optional[bool] = None

  @model_validator(mode='before')
  def extract_results(cls, values):
      strength = values.pop('strength', {})
      values['strength'] = strength.get('name', '')
      return values


class Play(BaseModel):
  coordinates: Optional[Coordinates]
  about: PlayDetails
  result: PlayResult
  team: Optional[Team] = None
  players: Optional[list[PlayerEvent]] = []
  parent: "Game" = None

  @field_validator('coordinates', mode='before')
  def coordinates(cls, value):
      if not value:
         return None
      return value

  def get_opp_side(self):

    starting_side = self.parent.starting_side
    if starting_side is None:
      return None
    is_home = self.parent.is_home_team(self.team.triCode)
    period = self.about.period

    return Side.Left if (starting_side + is_home + period) % 2 else Side.Right

class Game(BaseModel):
    plays: list[Play]
    home_team: Optional[Team] = None
    away_team: Optional[Team] = None
    starting_side: Side = None

    @model_validator(mode='before')
    def extract_plays_and_teams(cls, values):
        result = values.pop('liveData', {})
        plays = result.pop('plays', {})
        try:
          starting_side = result['linescore']['periods'][0]['home']['rinkSide']
          values['starting_side'] = Side.Left if starting_side == 'left' else Side.Right
        except:
          pass

        game_data = values.get('gameData', {})
        teams = game_data.pop('teams', {})
        values['plays'] = plays.get('allPlays', [])
        values['home_team'] = teams.get('home')
        values['away_team'] = teams.get('away')
        return values

    def __init__(self, **data):
        super().__init__(**data)
        for play in self.plays:
            play.parent = self

    def is_home_team(self, team: str):
      return self.home_team.triCode == team

    def to_df(self):
      columns = ['event idx', 'x', 'y', 'description']
      df = pd.DataFrame(columns=columns)
      for play in self.plays:
        idx = play.about.eventIdx
        x = play.coordinates.x if play.coordinates else None
        y = play.coordinates.y if play.coordinates else None
        description = play.result.description
        df = pd.concat([df, pd.DataFrame([[idx, x, y, description]], columns=columns)])
      return df.reset_index(drop=True)

class PlayOffGame(Game):
    round: int
    matchup: int
    game: int
    game_played: bool = True

    @model_validator(mode='before')
    def extract_playoff_info(cls, values):
        game_pk = values['gamePk']
        if 'message' in values or values['gameData']['status']['statusCode'] != '7':
          values['game_played'] = False
        values['round'] = game_pk // 10**2 % 10
        values['matchup'] = game_pk // 10**1 % 10
        values['game'] = game_pk // 10**0 % 10
        return values


class Season(BaseModel):
  regulars: list[Game]
  playoffs: Dict[int, PlayOffGame]

  def get_playoff(self, round = 1, matchup = 1, game = 1):
    return self.playoffs[f'{round}{matchup}{game}']