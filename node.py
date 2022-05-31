from ctypes.wintypes import BOOL
from queue import PriorityQueue
import clingo

class Node():
    def __init__(self, constraints):
        # calculate from passed arguments
        self.constraints = constraints      # string
        self.problem = ""                  # Is string of program
        self.cost = 0
        self.model = None

        # is this really necessary???
        self.left_child = None
        self.right_child = None

# TODO think about how to make this more efficient

def get_children(parent, first_conflict):
    # make constraint(Robot,Coordinates,Timestep) 
    # first_conflict has format first_conflict(Robot1, Robot2, Coordinates, Timestep)
    left_constraint = "constraint(" + str(first_conflict[0]) + "," + str(first_conflict[2]) + "," + str(first_conflict[3]) + ")."
    right_constraint = "constraint(" + str(first_conflict[1]) + "," + str(first_conflict[2]) + "," + str(first_conflict[3]) + ")."
    
    left_child = Node(parent.constraints + left_constraint)
    right_child = Node(parent.constraints + right_constraint)

    left_child.problem = parent.problem + left_constraint
    right_child.problem = parent.problem + right_constraint

    ctl_l = clingo.Control()
    ctl_l.add("base", [], left_child.problem)
    ctl_l.ground([("base", [])])
    with ctl_l.solve(yield_=True) as handle:
        left_child.model = next(iter(handle))

    left_child.cost = len(list(left_child.model.symbols(terms=True))) - 1

    ctl_r = clingo.Control()
    ctl_r.add("base", [], right_child.problem)
    ctl_r.ground([("base", [])])
    with ctl_r.solve(yield_=True) as handle:
        right_child.model = next(iter(handle))

    right_child.cost = len(list(right_child.model.symbols(terms=True))) - 1
    
    return left_child, right_child


def main(self, input_file):
    
    # read input file and construct model for root node
    try:
        with open(input_file) as file_object:
            lines = file_object.readlines()
    except FileNotFoundError:
        print("The specified file could not be found.")
        return
    #global file_string ?
    file_string = ''
    for line in lines: 
        file_string += line.rstrip() 
        file_string += " "              # unnecessary, maybe make problem global variable?
    

    root = Node([])
    root.problem = file_string

    ctl = clingo.Control()
    ctl.add("base", [], file_string)
    ctl.ground([("base", [])])
    with ctl.solve(yield_=True) as handle:
        root.model = next(iter(handle))
    
    root.cost = len(list(root.model.symbols(terms=True))) - 1    # -1 for first_conflict

    # make priority queue
    queue = PriorityQueue()
    queue.put((root.cost, root))

    while queue:
        current = queue.get()

        # check whether there is a first conflict
        first_conflict = (current.model.symbols(terms=True))[0]
        if first_conflict.name != "first_conflict":
            print("no first_conflict found")
            print("model: " + str(current.model))
            return True
            # TODO write to file here

        l_child, r_child = get_children(current, first_conflict.arguments)
        queue.put((l_child.cost, l_child))
        queue.put((r_child.cost, r_child))

# TODO what happens when queue is empty?
# TODO check the solution somehow different than checking for first_conflict
