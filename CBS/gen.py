from random import randint
from os import path
import argparse

def make_instance(size, numRobots, cooShelfs, cooRobs):
    '''
    Creates inits of the instance.
        
        Parameters:
            size (int):     maximum range of the coordinates
            numRobots (int): 
                            number of robots to be created
            cooShelfs (list of tupels of int):
                            every element of the list represents 
                            the coordinates for a shelf
            cooRobs (list of tupels of int):
                            every element of the list represents
                            the coordinates for a robot
        
        Returns:
            string (str):   all init-atoms of the generated problem
    '''

    string = ""

    # create every node (field) in the grid
    for x in range(1, size+1):
        for y in range(1, size+1):
            string += f"init(object(node,{x*y}),value(at,({x},{y}))). "

    # create the initial position of every robot and shelf
    for n in range(1,numRobots+1):
        string += f"init(object(robot,{n}),value(at,{cooRobs[n-1]})). "
        string += f"init(object(shelf,{n}),value(at,{cooShelfs[n-1]})). "

    return string

def gen_coo(size, numRobots):
    '''
    Generates random coordinates for robots and shelves. A robot is 
    not allowed to be generated on the shelf it needs to reach.

        Parameters:
            size (int):     maximum range of the coordinates
            numRobots (int):
                            number of robots, and shelf, to be created

        Returns:
            cooShelfs (list of tupels of int):
                            every element of the list represents 
                            the coordinates for a shelf
            cooRobs (list of tupels of int):
                            every element of the list represents
                            the coordinates for a robot
    '''
    
    cooRobs = []
    cooShelfs = []
    
    for n in range(numRobots):
        r = (randint(1,size), randint(1,size))
        s = (randint(1,size), randint(1,size))
        # ensure robots and their shelfs don't have the same coordinates
        while (r == s) or (r in cooRobs) or (s in cooShelfs):
            r = (randint(1,size), randint(1,size))
            s = (randint(1,size), randint(1,size))
        if r != s:
            cooRobs.append(r)
            cooShelfs.append(s)

    return cooShelfs, cooRobs

def make_paths(cooShelfs, cooRobs):
    '''
    Generate the occurs for each robot.

        Parameters:
            cooShelfs (list of tupels of int):
                            every element of the list represents 
                            the coordinates for a shelf
            cooRobs (list of tupels of int):
                            every element of the list represents
                            the coordinates for a robot

        Returns:
            moves (list of lists of tupels of int)
                            all the movements of the initial plan,
                            which consists of direkt paths as orders
                            of coordinates
    '''

    moves = []
    for i in range(len(cooRobs)):
        moves.append([])
        # initialize r and s with the starting coordinates of the robot
        # and the shelf respectively
        r = cooRobs[i]
        s = cooShelfs[i]
        # if r == s happens, the robot will have reached its goal
        while r != s:
            # change the first coordinate of the robot to the one of
            # the shelf gradually via allowed movement
            if r[0] < s[0]:
                moves[-1].append((1,0))
                r = (r[0]+1,r[1])
                continue
            elif r[0] > s[0]:
                moves[-1].append((-1,0))
                r = (r[0]-1,r[1])
                continue
            # change the second coordinate of the robot to the one of
            # the shelf gradually via allowed movement
            elif r[1] < s[1]:
                moves[-1].append((0,1))
                r = (r[0],r[1]+1)
                continue
            elif r[1] > s[1]:
                moves[-1].append((0,-1))
                r = (r[0],r[1]-1)
    return moves

def to_asprilo_format(moves):
    '''
    Returnes a string that can be used by the asprilo visualizer.

        Parameters:
            moves (list of lists of tupels of int):    
                            all the movements of the initial plan
                            as orders of coordinates

        Returns:
            instance (str): all the movements of the initial plan as
                            in the format that asprilo uses
    '''

    instance = ""
    for i in range(1, len(moves)+1):                # i are indexes of list of all moves of each robot
        for j in range(1,len(moves[i-1])+1):        # j are indexes of each move of the robot
            instance += f"occurs(object(robot,{i}),action(move,{moves[i-1][j-1]}),{j-1}). "
    
    return instance

def main(raw_args=None):
    '''
    Creates a random instance, including an initial plan, with
    specified grid size and number of robots/shelfs. 
    
    usage: gen.py [-h] -s SIZE -n ROBOTS output

    positional arguments:
        output                  the robot plans are saved in this file

    optional arguments:
        -h, --help              show this help message and exit
        -s SIZE, --size SIZE    size of generated instance (square shaped)
        -n ROBOTS, --robots ROBOTS
                                the amount of robots randomly placed on the instance
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--size", type=int, required=True, help="size of generated instance (square shaped)")
    parser.add_argument("-n","--robots", type=int, required=True, help="the amount of robots randomly placed on the instance")
    parser.add_argument("output", help="the robot plans are saved in this file")
    args = parser.parse_args(raw_args)

    # generates the coordinates for the robots and shelfs
    cooShelves, cooRobs = gen_coo(args.size, args.robots)

    # creates the plan and converts it to the format asprilo uses
    string = make_instance(args.size, args.robots, cooShelves, cooRobs)
    string += to_asprilo_format(make_paths(cooShelves, cooRobs))
    
    mode = "w" if path.exists(args.output) else "a"

    # write solution to output file
    with open(args.output, mode, encoding='utf-8') as f:
        f.write(string)

    return

if __name__ == "__main__":
    main()
