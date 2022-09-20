'''Game Guess the number
Computer sets and guesses itself (in less than 20 attempts)'''

import numpy as np

def precise_predict(number:int=np.random.randint(1, 101)) -> int:
    """ Randomly guessing the number

    Args:
        number (int, optional): Guessed number. Defaults to 1.

    Returns:
        int: Number of tries
    """
    
    count = 0
    minimum = 1
    maximum = 100
    medium = round((minimum+maximum) // 2)
        
    while number != medium:
        count+=1       
        if number > medium:
            minimum = medium
        elif number < medium:
            maximum = medium
        else:
            break
        medium = round((minimum+maximum) // 2)
    
    return(count)

def score_game(precise_predict) -> int:
    """ The average number of tries until success (1000 attempts)

    Args:
        random_predict (_type_): Guessing function

    Returns:
        int: Average number of tries
    """
    count_ls = []
    np.random.seed(1) # fixing the seed
    random_array = np.random.randint(1, 101, size=(1000)) # guessed the list of numbers
    
    for number in random_array:
        count_ls.append(precise_predict(number))
    
    score = int(np.mean(count_ls))
    print(f'Your algorithm guesses the number in average within {score} tries')
    return(score)
        
# if __name__ == '__main__':
    # RUN
 #   score_game(precise_predict)
    
print(score_game(precise_predict))

