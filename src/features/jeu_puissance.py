


def get_seconds(time_str:str)-> int:
    
    # Split the time string 
    minutes, seconds = map(int, time_str.split(":"))
    # Calculate the time in seconds
    total_seconds = minutes * 60 + seconds
    #print(total_seconds)
    return total_seconds



# Détails des pénalités
def detail_penality(season_data):
    penalty_plays = season_data['regulars'][0]['liveData']['plays']['penaltyPlays']
    #print('penalty_plays: ',penalty_plays)
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
        #print(all_penalties)
        return all_penalties
        