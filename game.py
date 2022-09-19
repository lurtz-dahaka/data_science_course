'''Game Guess the number'''

import numpy as np

number = np.random.randint(1, 100) # memorizing the number

# number of attempts
count = 0

while True:
    count+=1
    predict_number = int(input('Guess the number from 1 to 100: '))
    
    if predict_number > number:
        print('The number is smaller')
        
    elif predict_number < number:
        print('The number is bigger')
        
    else:
        print(f"Congratulations! You've guessed the number for {count} tries, it is = {number}")
        break # end of the game