from ctypes.wintypes import BOOL
from queue import PriorityQueue
from time import perf_counter
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

def make_problem(input):
    new_problem = []
    ctl = clingo.Control()
    ctl.add("base", [], input)

    ctl.ground([("base", [])])
    with ctl.solve(yield_=True) as handle:
        try:
            model = next(iter(handle))
            new_problem = list(model.symbols(shown=True))
        except StopIteration:
            raise
    return new_problem

def get_children(parent, first_conflict, low_level, shows):
    # make constraint(Robot,Coordinates,Timestep) 
    # first_conflict has format first_conflict(Robot1, Robot2, Coordinates1, Coordinates2, Timestep)
    left_constraint = Function("constraint", [first_conflict[0], first_conflict[2], first_conflict[4]], True)
    right_constraint = Function("constraint", [first_conflict[1], first_conflict[3], first_conflict[4]], True)
    
    # shows if a child (and which) hit a StopIteration Exception
    # 0 -> no problem
    # 1 -> problem with left child
    # 2 -> problem with right child
    error_num = 0
    
    problem = make_string(parent.problem)

    #left child
    left_child = Node()
    left_child.constraints = parent.constraints.copy()
    left_child.constraints.append(left_constraint)

    lconstraints = make_string(left_child.constraints)
    try:
        left_child.problem = make_problem(problem + lconstraints + low_level + shows)
        left_child.cost = len(left_child.problem)
    except StopIteration:
        error_num = 1

    #right child
    right_child = Node()
    right_child.constraints = parent.constraints.copy()
    right_child.constraints.append(right_constraint)

    rconstraints = make_string(right_child.constraints)
    try:
        right_child.problem = make_problem(problem + rconstraints + low_level + shows)
        right_child.cost = len(right_child.problem)
    except StopIteration:
        error_num = 2
    
    print(f"left constraints: {lconstraints} \n right constraints: {rconstraints}")

    return left_child, right_child, error_num

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
    parser.add_argument("input", help="ASP file containing robot plans")
    parser.add_argument("-b","--benchmark", help="output benchmarked values to the command line", action="store_true")
       

    args = parser.parse_args()

    node_counter = 1
    if args.benchmark:
        timer = perf_counter()
    
    # read input file with problem
    problem_file = read_file(args.input)
    
    # read test.lp (low level search implementation)
    asp_file = read_file("test.lp")
             

    # initialize root node + construct model for it
    root = Node()
    root.problem = problem_file #nützlich?

    # ctl = clingo.Control()

    shows = '''#show. 
            #show occurs(object(robot,R), action(move,D),     T) : move(R,D,T). 
            #show occurs(object(robot,R), action(move,D),     T) :    oldmove(R,D,T), not newConstraint(R).
            #show first_conflict(R,S,C,C',T) : first_conflict(R,S,C,C',T).
            #show init/2.'''

    root.problem = make_problem(asp_file + problem_file + shows)

    # total number of moves
    root.cost = len(root.problem)
    
    for i in range(len(root.problem)):
        if root.problem[i].name == "first_conflict":
            conflict_index = i
            break

    # make priority queue
    queue = PriorityQueue()
    queue.put(PrioritizedItem(root.cost, root))

    while queue.empty() == False:
        current = queue.get().item
        node_counter += 1

        # check whether there is a first conflict
        print(f"\n\ncurrent.problem: {make_string(current.problem)}\n\n")
        print(f"len of current.problem: {len(current.problem)}")
        print(f"conflict_index: {conflict_index}")
        first_conflict = (list(current.problem))[conflict_index]
        print("first_conflict: " + str(first_conflict))
        if first_conflict.name != "first_conflict":
            print("no first_conflict found")

            if args.benchmark:
                print(f"\nrunning time: {perf_counter() - timer:0.4f}")
                print(f"amount of nodes explored: {node_counter}\n")
            
            # write to output file
            mode = 'w' if os.path.exists("output.lp") else 'a'
            with open("output.lp", mode, encoding='utf-8') as file:
                for elem in current.problem:
                    file.write(str(elem) + ". ")

            return True
        
        l_child, r_child, num = get_children(current, first_conflict.arguments, asp_file, shows)

        if num != 1:
            queue.put(PrioritizedItem(l_child.cost, l_child))
        if num != 2:
            queue.put(PrioritizedItem(r_child.cost, r_child))
        

# TODO what happens when queue is empty?
# TODO check the solution somehow different than checking for first_conflict


if __name__ == "__main__":
    main()

print("We made it!")
