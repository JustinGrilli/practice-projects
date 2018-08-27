
import random

some_list = ['Justin', 'Stan', 'Ryan', 'Dan', 'Joey']
numbers = [4, 5, 6, 7, 8]

for item in some_list:
    print item + ' is friends with ' + str(random.choice(some_list)) + '.'