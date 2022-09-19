'''Game Guess the number
Computer memorizes and guesses itself'''

from itertools import count
import numpy as np

def random_predict(number:int=1) -> int:
    """ Randomly guessing the number

    Args:
        number (int, optional): Guessed number. Defaults to 1.

    Returns:
        int: Number of tries
    """
    count = 0
    
    while True:
        count+=1
        predict_number = np.random.randint(1, 101) # guessed number
        if number == predict_number:
            break # leave the cycle if guess is correct
    
    return(count)

def score_game(random_predict) -> int:
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
        count_ls.append(random_predict(number))
    
    score = int(np.mean(count_ls))
    print(f'Your algorithm guesses the number in average within {score} tries')
    return(score)
        
if __name__ == '__main__':
    # RUN
    score_game(random_predict)