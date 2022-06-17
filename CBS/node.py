from ctypes.wintypes import BOOL
from queue import PriorityQueue
from typing import List
import clingo
from sys import argv
import os.path
import argparse
from clingo.symbol import Function
import heapq

from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any=field(compare=False)

class Node():
    def __init__(self):
        # calculate from passed arguments
        self.constraints = []      # list of all constraints
        self.problem = ""                   # string of model
        self.cost = 0

        # is this really necessary???
        self.left_child = None
        self.right_child = None

# TODO think about how to make this more efficient

def make_string(list):
    string = ""
    for elem in list:
        if elem.name == "first_conflict":
            print("first conflict found")
            continue
        string += str(elem) + ". "
    return string

def get_children(parent, first_conflict, shows):
    # make constraint(Robot,Coordinates,Timestep) 
    # first_conflict has format first_conflict(Robot1, Robot2, Coordinates, Timestep)
    left_constraint = Function("constraint", [first_conflict[0], first_conflict[2], first_conflict[3]], True)
    right_constraint = Function("constraint", [first_conflict[1], first_conflict[2], first_conflict[3]], True)
    
    left_child = Node()
    left_child.constraints = parent.constraints.copy()
    left_child.constraints.append(left_constraint)

    right_child = Node()
    right_child.constraints = parent.constraints.copy()
    right_child.constraints.append(right_constraint)

    problem = make_string(parent.problem)
    lconstraints = make_string(left_child.constraints)

    # left_child
    ctl_l = clingo.Control()
    ctl_l.add("base", [], problem)
    ctl_l.add("base", [], lconstraints)
    ctl_l.add("base", [], shows)

    ctl_l.ground([("base", [])])
    with ctl_l.solve(yield_=True) as handle:
        model = next(iter(handle))
        left_child.problem = list(model.symbols(shown=True))

        # total number of moves + some constant
        left_child.cost = len(list(model.symbols(shown=True)))

    rconstraints = make_string(right_child.constraints)

    # right_child
    ctl_r = clingo.Control()
    ctl_r.add("base", [], problem)
    ctl_r.add("base", [], rconstraints)
    ctl_r.add("base", [], shows)  
    
    ctl_r.ground([("base", [])])
    with ctl_l.solve(yield_=True) as handle:
        model = next(iter(handle))
        right_child.problem = list(model.symbols(shown=True))
        right_child.cost = len(list(model.symbols(shown=True)))
    
    return left_child, right_child

def read_file(file_name):
    try:
        with open(file_name) as file_object:
            lines = file_object.readlines()
    except FileNotFoundError:
        print(f"The file {file_name} could not be found.")
        return
    file_string = ''
    for line in lines: 
        file_string += line.rstrip() 
        file_string += " " 
    return file_string

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input', type=str, required=True, help="ASP file containing robot plans")

    

    args = parser.parse_args()

    # read input file with problem
    problem_file = read_file(args.input)
    
    # read test.lp (low level search implementation)
    asp_file = read_file("test.lp")
             

    # initialize root node + construct model for it
    root = Node()
    root.problem = problem_file

    ctl = clingo.Control()

    shows = '''#show. 
            #show occurs(object(robot,R), action(move,D),     T) : move(R,D,T). 
            #show occurs(object(robot,R), action(move,D),     T) :    oldmove(R,D,T), not newConstraint(R).
            #show first_conflict(R,S,C,T) : first_conflict(R,S,C,T).
            #show init/2.'''

    ctl.add("base", [], asp_file)
    ctl.add("base", [], problem_file)
    ctl.add("base", [], shows)

    ctl.ground([("base", [])])

    with ctl.solve(yield_=True) as handle:
        model = next(iter(handle))
        root.problem = list(model.symbols(shown=True))#(shown=True))

        # total number of moves
        root.cost = len(list(model.symbols(shown=True)))    # -1 for first_conflict
    
    for i in range(len(root.problem)):
        if root.problem[i].name == "first_conflict":
            conflict_index = i
            break

    # make priority queue
    queue = PriorityQueue()
    queue.put(PrioritizedItem(root.cost, root))

    while queue.empty() == False:
        current = queue.get().item

        # check whether there is a first conflict
        print(f"current.problem: {current.problem}")
        print(f"len of current.problem: {len(current.problem)}")
        print(f"conflict_index: {conflict_index}")
        first_conflict = (list(current.problem))[conflict_index]
        print("first_conflict: " + str(first_conflict))
        if first_conflict.name != "first_conflict":
            print("no first_conflict found")
            
            # write to output file
            mode = 'w' if os.path.exists("output.lp") else 'a'
            with open("output.lp", mode, encoding='utf-8') as file:
                for elem in current.problem:
                    file.write(str(elem) + ". ")

            return True
        
        l_child, r_child = get_children(current, first_conflict.arguments, shows)
        # print("l_child.constraints: " + str(l_child.constraints + "\n"))
        # print("l_child.problem: " + str(l_child.problem) + "\n")
        # print("l_child.cost: " + str(l_child.cost) + "\n")
        queue.put(PrioritizedItem(l_child.cost, l_child))
        queue.put(PrioritizedItem(r_child.cost, r_child))

# TODO what happens when queue is empty?
# TODO check the solution somehow different than checking for first_conflict


if __name__ == "__main__":
    main()

print("We made it!")
