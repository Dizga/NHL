import math
import os
import pandas as pd

from src.data.load import NHLDataDownloader


def load_df_shots(year, filename: str = "") -> pd.DataFrame:
  """
  Load season data and transform to a DataFrame with shots and goals events.

  Args:
      year (int): The first year of the season to retrieve, i.e. for the 2016-17
                season you'd put in 2016
      filename (Optional[str]): Path + filename of the file to load or save data into.
  """

  version = 0.12

  filename = filename or f'data/shots_{year}_{version}.pkl'

  if os.path.isfile(filename):
    return pd.read_pickle(filename)
  
  season = NHLDataDownloader(year).load_processed_data()

  columns = ['Game_id',
          'Period',
          'Time',
          'Team',
          'Goal',
          'X',
          'Y',
          'Shooter',
          'Goalie',
          'Type',
          'Empty_net',
          'Strength']
  
  data = []

  print("Creating Dataframe...")
  
  for game_id, game in enumerate(season.regulars):
    for play in game.plays:
      if play.coordinates and (play.result.event == 'Goal' or play.result.event == 'Shot'):

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
        shot_type = play.result.secondaryType
        empty_net = play.result.emptyNet
        strength = play.result.strength
        data.append([id, periode, time, equipe, but, x, y, tireur, gardien, shot_type, empty_net, strength])
        
  df = pd.DataFrame(data, columns=columns)

  df.Empty_net = df.Empty_net.fillna(False)
  df.Strength = df.Strength.fillna('Even')

  # Get the opponant net position
  df['Avg'] = df.groupby(['Game_id', 'Period', 'Team'])['X'].transform('mean')
  def distance_x_from_net(row):
      x = row.X
      x_net = 89 if row.Avg > 0 else -89
      return abs(x_net-x)

  df['X_net'] = df.apply(distance_x_from_net, axis=1)
  df['Net_distance'] = df.apply(lambda row: math.dist([row.X_net, row.Y],[0, 0]), axis=1)
  df['Net_angle'] = df.apply(lambda row: math.degrees(math.atan2(abs(row.Y), row.X_net)), axis=1)
  df.drop('Avg', axis=1, inplace = True)

  df['Year'] = year

  df = df.infer_objects()

  df.to_pickle(filename)

  print("Done!")

  return df