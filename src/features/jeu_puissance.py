'''
    Calculez quelques caractéristiques concernant la situation de jeu de puissance (power-play).

'''
import sys
import os

def get_seconds(time_str:str)-> int:
    
    # Split the time string 
    minutes, seconds = map(int, time_str.split(":"))
    # Calculate the time in seconds
    total_seconds = minutes * 60 + seconds
    #print(total_seconds)
    return total_seconds



# Détails des pénalités
# source usagé: https://github.com/dword4/hockey-info/blob/master/app.py
#
def detail_penality(season_data):
    penalty_plays = season_data['regulars'][0]['liveData']['plays']['penaltyPlays']
    print('penalty_plays: ',penalty_plays)
    all_penalties = []

    for play in penalty_plays:
        penalty_info = season_data['regulars'][0]['liveData']['plays']['allPlays'][play]
        # Trouver des données  
        penalty_team = penalty_info['team']['triCode']
        penalty_time = penalty_info['about']['periodTime']
        penalty_period = penalty_info['about']['period']
        penalty_description = penalty_info['result']['description']
        
        # Ajouter dans List pour retourner
        penalty_details = {
            'penalty_period':penalty_period,
            'penalty_team':penalty_team,
            'penalty_time':get_seconds(penalty_time),
            'penalty_description':penalty_description
            }
        all_penalties.append(penalty_details)

    print('all_penalties ',all_penalties)
    return all_penalties
        
# Définition des caractéristiques pour question 4.4
# Calculez quelques caractéristiques concernant la situation de jeu de puissance (power-play)
def get_jeu_puissance(season_data:list)->list:
    all_penalties = detail_penality(season_data)
    power_play_active = False  # Indique si un power-play est actif
    power_play_start_time = 0  # Temps de début du power-play en secondes
    friendly_skaters_on_ice = 5  # Nombre de patineurs non-gardiens amicaux sur la glace
    opposing_skaters_on_ice = 5  # Nombre de patineurs non-gardiens adverses sur la glace
    home = season_data['regulars'][0]['gameData']['teams']['home']['triCode']
    #print(home)
    #away = season_data['regulars'][0]['gameData']['teams']['away']['triCode']
    #print(away)
    # Parcourir toutes les pénalités
    for penalty in all_penalties:
        penalty_team = penalty['penalty_team']
        penalty_time = penalty['penalty_time']

        # Vérifier si une nouvelle pénalité a commencé
        if not power_play_active:
            power_play_active = True
            power_play_start_time = penalty_time
            if penalty_team == home:
                friendly_skaters_on_ice -= 1
            else:
                opposing_skaters_on_ice -= 1
        else:
            # Vérifier si la pénalité actuelle a expiré
            if penalty_time - power_play_start_time >= 120:
                power_play_active = False
                power_play_start_time = 0
                if penalty_team == home:
                    friendly_skaters_on_ice += 1
                else:
                    opposing_skaters_on_ice += 1
    return {
            'time_elapsed_power_play': power_play_start_time,
            'friendly_skaters_on_ice': friendly_skaters_on_ice,
            'opposing_skaters_on_ice': opposing_skaters_on_ice
        }
# Afficher les caractéristiques
#d = get_jeu_puissance(all_penalties)
#print(d['time_elapsed_power_play'])
#print(d['friendly_skaters_on_ice'])
#print(d['opposing_skaters_on_ice'])



def get_jeu_puissance1(all_penalties:list,all_home:list)->list:
    #all_penalties = detail_penality(season_data)
    power_play_active = False  # Indique si un power-play est actif
    power_play_start_time = 0  # Temps de début du power-play en secondes
    friendly_skaters_on_ice = 5  # Nombre de patineurs non-gardiens amicaux sur la glace
    opposing_skaters_on_ice = 5  # Nombre de patineurs non-gardiens adverses sur la glace
    #home = season_data['regulars'][0]['gameData']['teams']['home']['triCode']
    home = all_home
    #print(home)
    #away = season_data['regulars'][0]['gameData']['teams']['away']['triCode']
    #print(away)
    # Parcourir toutes les pénalités
    for penalty in all_penalties:
        penalty_team = penalty['penalty_team']
        penalty_time = penalty['penalty_time']

        # Vérifier si une nouvelle pénalité a commencé
        if not power_play_active:
            power_play_active = True
            power_play_start_time = penalty_time
            if penalty_team == home:
                friendly_skaters_on_ice -= 1
            else:
                opposing_skaters_on_ice -= 1
        else:
            # Vérifier si la pénalité actuelle a expiré
            if penalty_time - power_play_start_time >= 120:
                power_play_active = False
                power_play_start_time = 0
                if penalty_team == home:
                    friendly_skaters_on_ice += 1
                else:
                    opposing_skaters_on_ice += 1
    return {
            'time_elapsed_power_play': power_play_start_time,
            'friendly_skaters_on_ice': friendly_skaters_on_ice,
            'opposing_skaters_on_ice': opposing_skaters_on_ice
        }
# Afficher les caractéristiques
#d = get_jeu_puissance(all_penalties)
#print(d['time_elapsed_power_play'])
#print(d['friendly_skaters_on_ice'])
#print(d['opposing_skaters_on_ice'])

