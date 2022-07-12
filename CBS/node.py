from ast import arg
import pathlib
from queue import PriorityQueue
from time import perf_counter
import clingo
import os.path
import argparse
from clingo.symbol import Function
import sys
import csv

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
        self.depth = 0

# TODO think about how to make this more efficient

def make_string(list):
    string = ""
    for elem in list:
        if elem.name == "first_conflict":
            print("first conflict found")
            continue
        if elem.name == "cost":
            string += "old_" + str(elem) + ". "
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
            my_iter = iter(handle)
            model = None
            for model in my_iter:
                pass
            if model != None:
                new_problem = list(model.symbols(shown=True))
            else:
                print("model is None")
                raise StopIteration
        except StopIteration:
            raise
    return new_problem

def get_children(parent, first_conflict, conflict_index, low_level, shows):
    # make constraint(Robot,Coordinates,Timestep) 
    # first_conflict has format first_conflict(Robot1, Robot2, Coordinates1, Coordinates2, Timestep)
    left_constraint = Function("constraint", [first_conflict[0], first_conflict[2], first_conflict[4]], True)
    right_constraint = Function("constraint", [first_conflict[1], first_conflict[3], first_conflict[4]], True)
    
    # shows if a child (and which) hit a StopIteration Exception
    # 0 -> no problem
    # 1 -> problem with left child
    # 2 -> problem with right child
    # 3 -> problem with both
    error_num = 0
    
    problem = make_string(parent.problem)

    #left child
    left_child = Node()
    left_child.constraints = parent.constraints.copy()
    left_child.constraints.append(left_constraint)
    left_child.depth = parent.depth + 1


    lconstraints = make_string(left_child.constraints)
    try:
        left_child.problem = make_problem(problem + lconstraints + low_level + shows)
        left_child.cost = left_child.problem[conflict_index-1].arguments[0]
    except StopIteration:
        error_num = 1

    #right child
    right_child = Node()
    right_child.constraints = parent.constraints.copy()
    right_child.constraints.append(right_constraint)
    right_child.depth = parent.depth + 1

    rconstraints = make_string(right_child.constraints)
    try:
        right_child.problem = make_problem(problem + rconstraints + low_level + shows)
        right_child.cost = right_child.problem[conflict_index-1].arguments[0]
    except StopIteration:
        if error_num == 1: error_num = 3
        else: error_num = 2
    
    print(f"left constraints: {lconstraints} \n right constraints: {rconstraints}")

    return left_child, right_child, error_num

def read_file(file_name):
    try:
        with open(file_name) as file_object:
            lines = file_object.readlines()
    except FileNotFoundError:
        sys.exit(f"The file {file_name} could not be found.")
    file_string = ''
    for line in lines: 
        file_string += line.rstrip() 
        file_string += " " 
    return file_string

def benchmark(name, current, node_counter, timer, last_move=0, move_sum=0):

    print("\n---BENCHMARK----------------------------------") 
    runtime = perf_counter() - timer          
    print(f"running time: {runtime:0.4f}")
    print(f"amount of nodes explored: {node_counter}")
    print(f"length of path through the tree: {current.depth}")
    last_move = 0
    move_sum = 0
    for elem in current.problem:
        if elem.name == "occurs":
            if elem.arguments[2].number > last_move: # find the time of the last move
                last_move = elem.arguments[2].number
            move_sum += 1
    print(f"timesteps taken until completion of problem: {last_move}")
    print(f"amount of moves made in total: {move_sum}\n")
    return [name, runtime, node_counter, current.depth, last_move, move_sum]


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="ASP file containing robot plans")
    parser.add_argument("-b","--benchmark", help="output benchmarked values to the command line", action="store_true")
    parser.add_argument("-g","--greedy", help="enable when you want to use a faster but suboptimal greedy search", action="store_true")
    parser.add_argument('benchmark_file', nargs='?', type=str, default="bm_output.csv", help="By default benchmarked values are saved in bm_output.csv. Specify a file here, if you want to append them to it instead.")
    args = parser.parse_args()

    node_counter = 1
    if args.benchmark:
        timer = perf_counter()
    
    # read input file with problem
    problem_file = read_file(args.input)
    
    # read low level search implementation
    lowlevel = "lowlevel.lp"
    if args.greedy:
        lowlevel = "lowlevel_greedy.lp"
    else:
        # add the cost of root
        problem_file += " cost(0)."

    asp_file = read_file(lowlevel)

    shows = '''#show. 
               #show occurs(object(robot,R), action(move,D), T) : move(R,D,T). 
               #show occurs(object(robot,R), action(move,D), T) :    oldmove(R,D,T), not newConstraint(R).
               #show first_conflict(R,S,C,C',T) : first_conflict(R,S,C,C',T).
               #show cost/1.
               #show init/2.'''

    # initialize root node + construct model for it
    root = Node()
    root.depth = 0

    root.problem = make_problem(asp_file + problem_file + shows)


    for i in range(len(root.problem)):
            if root.problem[i].name == "first_conflict":
                conflict_index = i
                break

    # total number of moves
    root.cost = 0

    # make priority queue
    queue = PriorityQueue()
    queue.put(PrioritizedItem(root.cost, root))

    while queue.empty() == False:
        current = queue.get().item
        node_counter += 1

        # check whether there is a first conflict
        print(f"\n\ncurrent.problem: {make_string(current.problem)}\n\n")
        print(f"cost of current.problem: {current.cost}")
        print(f"conflict_index: {conflict_index}")
        first_conflict = (list(current.problem))[conflict_index]
        print("first_conflict: " + str(first_conflict))
        if first_conflict.name != "first_conflict":
            print("no first_conflict found")

            if args.benchmark:
                if args.benchmark_file == "bm_output.csv":
                    mode = 'w' if os.path.exists("bm_output.csv") else 'a'
                else:
                    mode = 'a'
                
                if os.path.exists(args.benchmark_file): new_file = False
                else: new_file = True

                with open(args.benchmark_file, mode, encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    if new_file:
                        writer.writerow(['name', 'time', '#nodes', 'pathlength', 'horizon', '#moves'])
                    writer.writerow(benchmark(args.input, current, node_counter, timer))
                
            
            # write to output file
            mode = 'w' if os.path.exists("output.lp") else 'a'
            with open("output.lp", mode, encoding='utf-8') as file:
                for elem in current.problem:
                    file.write(str(elem) + ". ")

            return True
        l_child, r_child, num = get_children(current, first_conflict.arguments, conflict_index, asp_file, shows)

        if num == 3: break
        if num != 1:
            queue.put(PrioritizedItem(l_child.cost, l_child))
        if num != 2:
            queue.put(PrioritizedItem(r_child.cost, r_child))
    
    print("\nNo solution found!")
    if args.benchmark:
        benchmark(current, node_counter, timer)

if __name__ == "__main__":
    main()

print("We made it!")
