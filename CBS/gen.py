from random import randint
from os import path
import argparse

# creates inits of the instance as string
def make_instance(size, numRobots, cooShelfs, cooRobs):

    string = ""

    for x in range(1, size+1):
        for y in range(1, size+1):
            string += f"init(object(node,{x*y}),value(at,({x},{y}))). "
                
    print(f"cooShelfs: {cooShelfs}")
    print(f"cooRobs: {cooRobs}")

    for n in range(1,numRobots+1):
        string += f"init(object(robot,{n}),value(at,{cooRobs.pop()})). "
        string += f"init(object(shelf,{n}),value(at,{cooShelfs.pop()})). "

    return string

# generates random coordinates for robots and shelves
# a robot may not be generated on the shelf it needs to reach
def genCoo(size, numRobots):
    
    cooRobs = []
    cooShelfs = []
    
    for n in range(numRobots):
        r = (randint(1,size), randint(1,size))
        s = (randint(1,size), randint(1,size))
        while (r == s) or (r in cooRobs) or (s in cooShelfs):
            r = (randint(1,size), randint(1,size))
            s = (randint(1,size), randint(1,size))
        if r != s:
            cooRobs.append(r)
            cooShelfs.append(s)

    return cooShelfs, cooRobs

# generate the occurs for each robot
# returns string that can be used for asprilo visualizer
def make_paths(size, numRobots):

    cooShelfs, cooRobs = genCoo(size, numRobots)

    moves = []
    for i in range(numRobots):
        print(f"{i}. robot")
        moves.insert(0, [])
        r = cooRobs[i]
        s = cooShelfs[i]
        while r != s:
            print(f"r: {r}")
            print(f"s: {s}")
            if r[0] < s[0]:
                print("hello")
                moves[0].append((1,0))
                r = (r[0]+1,r[1])
                continue
            elif r[0] > s[0]:
                print("hello1")
                moves[0].append((-1,0))
                r = (r[0]-1,r[1])
                continue
            elif r[1] < s[1]:
                print("hello2")
                moves[0].append((0,1))
                r = (r[0],r[1]+1)
                continue
            elif r[1] > s[1]:
                print("hello3")
                moves[0].append((0,-1))
                r = (r[0],r[1]-1)
    
    instance = make_instance(size, numRobots, cooShelfs, cooRobs)
    print(f"moves: {moves}")
    for i in range(1, len(moves)+1):                # i are indexes of list of all moves of each robot
        for j in range(1,len(moves[i-1])+1):        # j are indexes of each move of the robot
            instance += f"occurs(object(robot,{i}),action(move,{moves[i-1][j-1]}),{j-1}). "
    
    return instance

def main(raw_args=None):

    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--size", type=int, required=True, help="size of generated instance (square shaped)")
    parser.add_argument("-n","--robots", type=int, required=True, help="the amount of robots randomly placed on the instance")
    parser.add_argument("output", help="the robot plans are saved in this file")
    args = parser.parse_args(raw_args)

    string = make_paths(args.size, args.robots)
    
    mode = "w" if path.exists(args.output) else "a"

    with open(args.output, mode, encoding='utf-8') as f:
        f.write(string)

    return

if __name__ == "__main__":
    main()
