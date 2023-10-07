import os
import pickle
import sys
from src.data import RequestNHL
from src import utils

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

# Load or download all the regular and playoff games from the specified season
def load_data(season:int, filename: str = "", samples: bool = False) -> object:

  season_fullname = utils.season_full_name(season)

  season_file = filename or f'data/{season_fullname}.pkl'

  if os.path.isfile(season_file):
    with open(season_file, 'rb') as file:
      data = pickle.load(file)
      print(f'Season {season} successfully loaded from file')
  else:

    r_games = []
    p_games = {}
    data = {}

    nb_regular_games = RequestNHL.nb_regular_games(season)
    if samples:
      nb_regular_games = 20
      nb_playoffs = 5

    print('Downloading:')
    for id in range(1, nb_regular_games + 1):
      game = RequestNHL.get_game(season, id)
      r_games.append(game)
      sys.stdout.write(f'\r Regulars: {id}/{nb_regular_games}')
      sys.stdout.flush()
    print()

    for id in range(1, nb_playoffs + 1):
      code = playoff_code(id)
      game_id = f"0{code}"
      game = game = RequestNHL.get_game(season, id, regular=False)

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
      print(f'Season {season} successfully saved to file')

  return data