def season_full_name(season: int or str):
  return season + str(int(season)+1) if type(season) == str else f'{season}{season+1}'