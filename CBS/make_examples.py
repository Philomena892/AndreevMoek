import os
import sys
import clingo
import random
from gen import make_instance


def read_file(file_name):
    try:
        with open(file_name) as file_object:
            lines = file_object.readlines()
    except FileNotFoundError:
        sys.exit(f"The file {file_name} could not be found.")
    
    # to get rid of comments included by asprilo generator
    if file_name != "first_iteration_one_rob.lp":
        lines = lines[23:]

    file_string = ''
    for line in lines: 
        file_string += line.rstrip()
        file_string += " " 
    return file_string


# for each size and density always generate three random examples
SIZE = [5, 8, 16, 24]
DENSITY = [0.2, 0.3, 0.4, 0.5]
FIRST_ITERATION = read_file("first_iteration_one_rob.lp")
SHOWS = "#show. #show occurs(object(robot,R), action(move,D), T) : move(robot(R),D,T)."

os.system(f"mkdir benchmark_examples")
for size in SIZE:

    print(f"Currently working on size: {size}x{size}")
    dir = f"./benchmark_examples/size{size}x{size}"
    os.system(f"mkdir {dir}")

    for density in DENSITY:

        print(f"Working on examples with density {density}.")
        folder = f"{dir}/density{int(density * 100)}"
        os.system(f"mkdir {folder}")

        for i in range(1,2):

            print(f"Example Number {i}.")
    
            numRobots = int((size**2) * density)
            file = f"./{folder}/ex{i}.lp"
            
            # generate random new example with appropriate sizes
            # take out > /dev/null 2>&1 to see output
            moves = ""
            INITS = ""
            INITS = make_instance(size, numRobots)

            #os.system(f"gen -x {size} -y {size} -r {numRobots} -s {numRobots} -d {folder} --random --seed={''.join(random.sample(SEED,9))} --rand-freq 0.8 > /dev/null 2>&1")
            print("Example generated.")
            # rename file to ex[i].lp, so it is not overwritten in next iteration 

            # solve generated example with first_iteration_one_rob.lp for each robot once
            print(f"moves before loop: {moves}\n")
            print(f"numRobots: {numRobots}")

            for j in range(1, numRobots+1):
                print(f"j={j}")
                ctl = clingo.Control([f"-c rob={j}"])
                ctl.add("base", [], FIRST_ITERATION + INITS + SHOWS)         
                ctl.ground([("base", [])])

                with ctl.solve(yield_=True) as handle:
                    model = None
                    my_iter = iter(handle)
                    for model in my_iter:
                        pass
                    print(f"\n\nmodel: {model.symbols(terms=True)}")

                    # format the moves to asprilo format (point after each atom)
                    for elem in list(model.symbols(terms=True)):
                        moves += str(elem) + ". "
                    print(f"moves: {moves}")

                    # save the paths back into the file
                    with open(file, "a") as f:
                        f.write(INITS)
                        f.write(moves)                    
