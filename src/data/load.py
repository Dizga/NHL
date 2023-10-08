import math
import os
import pickle
import sys

import pandas as pd
from src.data import RequestNHL
from src import utils
from src.models import Season, Side

def playoff_code(id: int) -> int:
  """
  Return a playoff id {round}{matchup}{game} depending on an index
  https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md#game-ids
  i.e.    index 1 correspond to the playoff game 111
          index 2 correspond to the playoff game 112
          ...
          index 8 correspond to the playoff game 121
          etc.

  Args:
      id (int): index to convert
  """
  threshold = 0
  rest = id - 1
  for i in range(4):
    rest = rest - threshold
    threshold = 7 * 8 / 2 ** (i)
    if rest < threshold:
      matchup = int(rest / 7) + 1
      game = int(rest % 7) + 1
      round = i + 1
      return int(f"{round}{matchup}{game}")

def load_data(year:int, filename: str = "", samples: bool = False) -> object:
  """
  Load season data from file. If the file does not exists, the data is download and saved.
  Data includes regular and playoff games.

  Args:
      year (int): The first year of the season to retrieve, i.e. for the 2016-17
                season you'd put in 2016
      filename (Optional[str]): Path + filename of the file to load or save data into.

      samples (bool): if true, only a small portion of the data is downloaded, default false.
  """

  season_fullname = utils.season_full_name(year)

  default_filename = f'data/{season_fullname}.pkl'
  if samples:
    default_filename = f'data/{season_fullname}-samples.pkl'

  season_file = filename or default_filename

  if os.path.isfile(season_file):
    with open(season_file, 'rb') as file:
      data = pickle.load(file)
      print(f'Season {year} successfully loaded from file')
  else:

    r_games = []
    p_games = {}
    data = {}

    nb_regular_games = RequestNHL.nb_regular_games(season)
    nb_playoffs = 105
    if samples:
      nb_regular_games = 20
      nb_playoffs = 5

    print('Downloading:')
    for id in range(1, nb_regular_games + 1):
      game = RequestNHL.get_game(year, id)
      r_games.append(game)
      sys.stdout.write(f'\r Regulars: {id}/{nb_regular_games}')
      sys.stdout.flush()
    print()

    for id in range(1, nb_playoffs + 1):
      code = playoff_code(id)
      game = RequestNHL.get_game(year, code, regular=False)

      # Some not played game have no data (except a message)
      if 'message' in game:
        game['gamePk'] = int(code)

      p_games[code] = game
      sys.stdout.write(f'\r Playoffs: {id}/{nb_playoffs}')
      sys.stdout.flush()
    print()

    data = {"regulars":r_games, "playoffs":p_games}

    # Save season data to file
    with open(season_file, 'wb') as file:
      pickle.dump(data, file)
      print(f'Season {year} successfully saved to file')

  return data

def load_processed_data(year:int, filename: str = "", samples: bool = False) -> Season :
  """
  Load season data and parse the data into the Season model.

  Args:
      year (int): The first year of the season to retrieve, i.e. for the 2016-17
                season you'd put in 2016
      filename (Optional[str]): Path + filename of the file to load or save data into.

      samples (bool): if true, only a small portion of the data is downloaded, default false.
  """
  print('Processing data... (1-2 minutes)')
  season = Season.model_validate(load_data(year, filename, samples))
  print('Done!')
  return season


def load_df_shots(year:int, filename: str = "", season: Season = None) -> pd.DataFrame:
  """
  Load season data and transform to a DataFrame with shots and goals events.

  Args:
      year (int): The first year of the season to retrieve, i.e. for the 2016-17
                season you'd put in 2016
      filename (Optional[str]): Path + filename of the file to load or save data into.

      season (Season): (Optional) Season to convert to DataFrame
  """

  season_fullname = utils.season_full_name(year)
  filename = filename or f'data/shots_{season_fullname}.pkl'

  if not season:
    if os.path.isfile(filename):
      return pd.read_pickle(filename)
    season = load_processed_data(year)

  columns = ['Game Id',
           'Periode',
           'Temps écoulé',
           'Equipe',
           'Goal',
           'X',
           'Y',
           'X-opp',
           'Tireur',
           'Gardien',
           'Type',
           'Filet Vide',
           'Force',
           'Net distance']
  
  data = []

  print("Creating Dataframe...")
  
  for game_id, game in enumerate(season.regulars):
    for play in game.plays:
      if ( game.starting_side and
           play.coordinates   and
          (play.result.event == 'Goal' or play.result.event == 'Shot')):

        tireur = ""
        gardien = ""
        for player_event in play.players:
          if player_event.playerType == 'Scorer' or player_event.playerType == 'Shooter':
            tireur = player_event.player.fullName
          if player_event.playerType == 'Goalie':
            gardien = player_event.player.fullName

        periode = play.about.period
        time = play.about.periodTime.isoformat()[3:]
        id = game_id + 1
        equipe = play.team.triCode
        but = play.result.event == 'Goal'
        x = play.coordinates.x
        y = play.coordinates.y
        x_opp = -89 if play.get_opp_side() == Side.Left else 89
        shot_type = play.result.secondaryType
        empty_net = play.result.emptyNet
        strength = play.result.strength
        net_distance = math.dist([x, y],[x_opp, 0])
        data.append([id, periode, time, equipe, but, x, y, x_opp, tireur, gardien, shot_type, empty_net, strength, net_distance])
        
  df = pd.DataFrame(data, columns=columns)
  df = df.infer_objects()

  df.to_pickle(filename)

  print("Done!")

  return df