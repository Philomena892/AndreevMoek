'''
Creates a folder with example instances containing MIN_ROBOTS to 
MAX_ROBOTS robots. For example: The instance 3robs.lp consists of
2robs.lp with one added robot and its paths.
'''

import gen
from gen import make_instance, gen_coo, make_paths, to_asprilo_format
import os
import sys

# size of the example
SIZE = 7
# minimum and maximum amount of robots
MIN_ROBOTS = 2
MAX_ROBOTS = 19     # density 40 = 19 robots on size 7

DIR = "num_robots_benchmark"
os.system(f"mkdir {DIR}")

# create the example with MIN_ROBOTS robots
cooShelves, cooRobs = gen_coo(SIZE, MIN_ROBOTS)
inits = make_instance(SIZE, MIN_ROBOTS, cooShelves, cooRobs)
moves = to_asprilo_format(make_paths(cooShelves, cooRobs))

path = os.path.join(DIR, f"{MIN_ROBOTS}robs.lp")

with open(path, "a", encoding='utf-8') as f:
    f.write(inits + moves)

# create all other examples by adding one robot each time
for n in range(MIN_ROBOTS+1, MAX_ROBOTS+1):

    # generate one more distinct robot + shelf coordinates pair
    s, r = gen_coo(SIZE, 1)
    while (s in cooShelves) or (r in cooRobs):
        s, r = gen_coo(SIZE, 1)
    
    # append the inits for the new robot + shelf
    inits += f"init(object(robot,{n}),value(at,{r[0]})). "
    inits += f"init(object(shelf,{n}),value(at,{s[0]})). "

    # get the moves for the new robot
    new_paths = make_paths(s, r)[0]
    for i in range(len(new_paths)):
        moves += f"occurs(object(robot,{n}),action(move,{new_paths[i]}),{i}). "

    # write to file
    path = os.path.join(DIR, f"{n}robs.lp")

    with open(path, "a", encoding='utf-8') as f:
        f.write(inits + moves)
