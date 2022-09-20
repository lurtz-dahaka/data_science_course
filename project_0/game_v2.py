'''Game Guess the number
Computer sets and guesses itself (in less than 20 attempts)'''

from itertools import count
import numpy as np

def precise_predict(number:int=np.random.randint(1, 101)) -> int:
    """ Guessing the number precisely

    Args:
        number (int, optional): Randomly assigned number

    Returns:
        int: Number of attempts until guessing it right
    """
    
    count = 0 
    minimum = 1
    maximum = 100
    medium = round((minimum+maximum) // 2) # introducing the attempt number as medium between max and min
        
    while number != medium:
        count+=1       
        if number > medium:
            minimum = medium # limiting the minimum range 
        elif number < medium:
            maximum = medium # limiting the maximum range 
        else:
            break # Leaving the cycle as medium equals the number
        medium = round((minimum+maximum) // 2) # new medium shall be updated in acc. with new max and min
    
    return(count) # Number of attempts until guessing it right

def score_game(precise_predict) -> int:
    """ The average number of tries until success (1000 attempts)

    Args:
        precise_predict (_type_): Guessing function

    Returns:
        int: Average number of tries
    """
    count_ls = []
    np.random.seed(1) # fixing the seed
    random_array = np.random.randint(1, 101, size=(1000)) # guessed the list of numbers
    
    for number in random_array:
        # for each number we will add in the list a number of attempts to guess it right
        count_ls.append(precise_predict()) 
    
    score = int(np.mean(count_ls)) # an avearage value from all numbers from the list
    print(f'Your algorithm guesses the number in average within {score} tries')
    return(score) 

# RUN        
if __name__ == '__main__':
    score_game(precise_predict)


