import numpy as np


def normalize(arr, min_value=0, max_value=1):
    min_x = np.min(arr)
    max_x = np.max(arr)
    
    normalized = min_value + (arr - min_x) / (max_x - min_x) * (max_value - min_value)
    return normalized