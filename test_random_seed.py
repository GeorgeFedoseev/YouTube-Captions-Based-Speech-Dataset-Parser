import random
SEED = 448

myList = [ 'list', 'elements', 'go', 'here' ]
random.seed(SEED)
random.shuffle(myList)

print myList