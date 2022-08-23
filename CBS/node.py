from queue import PriorityQueue
from time import perf_counter
from turtle import left
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
    '''
    Wrapper class needed for priority queue 
    to only rank by cost and not by the node.
    '''
    priority: int
    item: Any=field(compare=False)

class Node():
    '''
    A node in a binary search tree used for the CBS algorithm.
    Attributes:
        constraints (list of clingo.symbol.Symbol):
                        list of constraints = coordinates a robot cannot be at at a certain time.
                        Has the format constraint(Robot,Coordinates,Timestep)
        problem (list of clingo.symbol.Symbol):
                        the model of the node
        cost (int):     value of the cost function for the current node
        depth (int):    depth of the node in search tree
    '''
    def __init__(self):
        self.constraints = []       # list of all constraints
        self.problem = ""           # list of symbols in model
        self.cost = 0
        self.depth = 0

def make_string(list):
    '''
    Converts a list of clingo symbols (clingo.symbol.Symbol)
    to a string.
    '''
    string = ""
    for elem in list:
        # do not keep first_conflict of last iteration
        if elem.name == "first_conflict":
            continue
        # change current cost to old_cost for next iteration
        if elem.name == "cost":
            string += "old_" + str(elem) + ". "
            continue
        # append current atom in string format
        string += str(elem) + ". "
    return string

def make_problem(input, horizon, root):
    '''
    Solves a problem using the clingo python API.
        Parameters:  
            input (str):    concatenated strings of the problem 
                            (including the instance and the asp file)
            horizon (int):  maximum makespan the solution is allowed to have
            root (bool):    if the problem is to be calculated for the root node,
                            the amount of conflicts will be calculated
                            
        Returns:
            new_problem (list of clingo.symbol.Symbol):
                            list of symbols that are in the model 
            init_conflict_num (int): 
                            amount of conflicts in the problem 
    '''
    init_conflict_num = 0
    new_problem = []

    ctl = clingo.Control([f"-c horizon={horizon}"])
    ctl.add("base", [], input)

    ctl.ground([("base", [])])
    with ctl.solve(yield_=True) as handle:
        try:
            # get the last model in the iterator because 
            # of the minimize statement
            my_iter = iter(handle)
            model = None
            for model in my_iter:
                pass
            if model != None:
                new_problem = list(model.symbols(shown=True))
                if root:
                    # save number of initial conflicts for benchmarking
                    for atom in list(model.symbols(atoms=True)):
                        if atom.name == "conflict":
                            init_conflict_num += 1
            else:
                print("model is None")
                raise StopIteration
        # no model was found = unsolvable
        except StopIteration:
            raise
    return new_problem, init_conflict_num

def get_children(parent, first_conflict, inits, low_level, shows, horizon):
    '''
    Creates and returns the two children of the passed node "parent".
    
        Parameters:
            parent (node):      a parent node
            first_conflict (list of clingo.symbol.Symbol): 
                                the atom "first_conflict" which has the format
                                first_conflict(Robot1, Robot2, Coordinates1, Coordinates2, Timestep)
            inits (str):        init atoms
            low_level (str):    low-level asp search file
            shows (str):        string of asp #show 
            horizon (int):      maximum makespan the solution is allowed to have
        
        Returns:
            left_child (node):  node that contains one added constraint compared to parent
            right_child (node): node that contains one added constraint compared to parent
            error_num (int):    shows if a child (and which) hit a StopIteration Exception
                        0 -> no problem
                        1 -> problem with left child
                        2 -> problem with right child
                        3 -> problem with both
    '''

    # make constraint(Robot,Coordinates,Timestep) 
    # first_conflict has format first_conflict(Robot1, Robot2, Coordinates1, Coordinates2, Timestep)
    left_constraint = Function("constraint", [first_conflict[0], first_conflict[2], first_conflict[4]], True)
    right_constraint = Function("constraint", [first_conflict[1], first_conflict[3], first_conflict[4]], True)
    
    error_num = 0
    
    problem = make_string(parent.problem)

    # initiate left child
    left_child = Node()
    left_child.constraints = parent.constraints.copy()
    left_child.constraints.append(left_constraint)
    left_child.depth = parent.depth + 1

    lconstraints = make_string(left_child.constraints)
    try:
        left_child.problem, _ = make_problem(inits + problem + lconstraints + low_level + shows, horizon, root=False)
        left_child.cost = left_child.problem[0].arguments[0]
    except StopIteration:
        error_num = 1

    # initiate right child
    right_child = Node()
    right_child.constraints = parent.constraints.copy()
    right_child.constraints.append(right_constraint)
    right_child.depth = parent.depth + 1

    rconstraints = make_string(right_child.constraints)
    try:
        right_child.problem, _ = make_problem(inits + problem + rconstraints + low_level + shows, horizon, root=False)
        right_child.cost = right_child.problem[0].arguments[0]
    except StopIteration:
        if error_num == 1: error_num = 3
        else: error_num = 2

    return left_child, right_child, error_num

def read_file(file_name):
    '''
    Reads a file within the same directory to a string.
    
        Parameters:      
            file_name (str): file name as string
    
        Returns:
            file_string (str): contents of the file saved in a string
    '''
    
    try:
        with open(file_name) as file_object:
            lines = file_object.readlines()
    except FileNotFoundError:
        sys.exit(f"The file {file_name} could not be found.")
    file_string = ''
    # add spaces and append into one string
    for line in lines: 
        file_string += line.rstrip() 
        file_string += " " 
    return file_string

def benchmark(name, current, node_counter, timer, conflict_num):
    '''
    Evaluates stats for benchmarking and prints the results.
    
        Parameters:
            name (str):             file name of the instance
            current (node):         node which contains solution
            node_counter (int):     amount of nodes that were dequeued so far
            timer (float):          starttime of program
            conflict_num (int):     number of conflicts in instance at beginning
        
        Returns: list consisting of
            name (str):             same as above
            runtime (float):        total runtime of program
            node_counter (int):     as was passed to the function
            current.depth (int):    depth of solution in search tree
            last_move (int):        timestep the last move was taken at = makespan
            move_sum (int):         counts every single move
            conflict_num (int):     number of conflicts in instance at beginning
    '''

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
    print(f"amount of moves made in total: {move_sum}")
    print(f"amount of conflicts in the instance: {conflict_num}\n")
    return [name, runtime, node_counter, current.depth, last_move, move_sum, conflict_num]


def main(raw_args=None):
    '''
    Runs CBS on the specified input file. 
    usage: node.py [-h] -hz HORIZON [-b] input [benchmark_file]
    positional arguments:
        input                 ASP file containing robot plans
        benchmark_file        By default benchmarked values are saved in bm_output.csv. Specify a file here, if you want to append them to it instead.
    optional arguments:
        -h, --help            show this help message and exit
        -hz HORIZON, --horizon HORIZON
                                maximum makespan the solution is allowed to have
        -b, --benchmark       save and output benchmarked values
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="ASP file containing robot plans")
    parser.add_argument("-hz","--horizon", type=int, required=True, help="maximum makespan the solution is allowed to have")
    parser.add_argument("-b","--benchmark", help="save and output benchmarked values", action="store_true")
    parser.add_argument('benchmark_file', nargs='?', type=str, default="bm_output.csv", help="By default benchmarked values are saved in bm_output.csv. Specify a file here, if you want to append them to it instead.")
    args = parser.parse_args(raw_args)
    print(f"vars(args): {vars(args)}")

    # save some values for the benchmarking
    node_counter = 1
    if args.benchmark:
        timer = perf_counter()
    
    # read input file with problem
    problem_file = read_file(args.input)
    
    # read low level search implementation
    lowlevel = "lowlevel.lp"
    # add the cost of root
    problem_file += " cost(0)."

    asp_file = read_file(lowlevel)

    shows = '''#show. 
               #show occurs(object(robot,R), action(move,D), T) : move(R,D,T). 
               #show occurs(object(robot,R), action(move,D), T) :    oldmove(R,D,T), not newConstraint(R).
               #show first_conflict(R,S,C,C',T) : first_conflict(R,S,C,C',T).
               #show cost/1.'''

    # initialize root node + construct model for it
    root = Node()
    root.depth = 0
    # save init atoms in extra string so they are not always reloaded
    inits = make_string(make_problem(problem_file + " #show. #show init/2.", args.horizon, root=False)[0])
    root.problem, conflict_num = make_problem(asp_file + problem_file + shows, args.horizon, root=True)

    # total number of moves
    root.cost = 0

    # make priority queue and enqueue root node
    queue = PriorityQueue()
    queue.put(PrioritizedItem(root.cost, root))

    while queue.empty() == False:
        current = queue.get().item
        node_counter += 1

        # check whether there is a first conflict
        first_conflict = (list(current.problem))[1]
        if first_conflict.name != "first_conflict":
            # solution was found
            print("no first_conflict found")

            if args.benchmark:
                # if a file for benchmark results is specified (args.benchmark_file != "bm_output.csv")
                # append to that file, otherwise overwrite bm_output.csv
                new_file = False if os.path.exists(args.benchmark_file) else True

                mode = 'a'
                if args.benchmark_file == "bm_output.csv" and not new_file:
                    mode = 'w'  

                with open(args.benchmark_file, mode, encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    if new_file or args.benchmark_file == "bm_output.csv":
                        writer.writerow(['file', 'time', '#nodes', 'pathlength', 'horizon', '#moves', 'init_conflicts'])
                    writer.writerow(benchmark(args.input, current, node_counter, timer, conflict_num))
                
            
            # write solution to output file
            mode = 'w' if os.path.exists("output.lp") else 'a'
            with open("output.lp", mode, encoding='utf-8') as file:
                file.write(inits)
                for elem in current.problem:
                    file.write(str(elem) + ". ")

            return True

        # create the children of the current node
        l_child, r_child, num = get_children(current, first_conflict.arguments, inits, asp_file, shows, args.horizon)

        # error handling + enqueuing the children
        if num == 3: continue
        if num != 1:
            queue.put(PrioritizedItem(l_child.cost, l_child))
        if num != 2:
            queue.put(PrioritizedItem(r_child.cost, r_child))
    
    # if no nodes left in queue
    print("\nNo solution found!")
    if args.benchmark:
        new_file = False if os.path.exists(args.benchmark_file) else True

        mode = 'a'
        if args.benchmark_file == "bm_output.csv" and not new_file:
            mode = 'w'  

        with open(args.benchmark_file, mode, encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            if new_file or args.benchmark_file == "bm_output.csv":
                writer.writerow(['file', 'time', '#nodes', 'pathlength', 'horizon', '#moves', 'init_conflicts'])
            writer.writerow(benchmark(args.input, current, node_counter, timer, conflict_num))

if __name__ == "__main__":
    main()
