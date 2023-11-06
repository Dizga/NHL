


def get_seconds(time_str:str)-> int:
    
    # Split the time string 
    minutes, seconds = map(int, time_str.split(":"))
    # Calculate the time in seconds
    total_seconds = minutes * 60 + seconds
    #print(total_seconds)
    return total_seconds



