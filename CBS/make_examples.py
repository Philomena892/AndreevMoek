import os
import sys
import clingo
import random


def read_file(file_name):
    try:
        with open(file_name) as file_object:
            lines = file_object.readlines()
    except FileNotFoundError:
        sys.exit(f"The file {file_name} could not be found.")
    
    # to get rid of comments included by asprilo generator
    if file_name != "first_iteration.lp":
        lines = lines[23:]

    file_string = ''
    for line in lines: 
        file_string += line.rstrip()
        file_string += " " 
    return file_string


# for each size and density always generate three random examples
SIZE = [5, 8, 16, 24]
DENSITY = [0.2, 0.3, 0.4, 0.5]
FIRST_ITERATION = read_file("first_iteration.lp")
SEED = "123456789"


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
            os.system(f"gen -x {size} -y {size} -r {numRobots} -s {numRobots} -d {folder} --random --seed={''.join(random.sample(SEED,9))} > /dev/null 2>&1")
            print("Example generated.")
            # rename file to ex[i].lp, so it is not overwritten in next iteration 
            arr = os.listdir(f"./{folder}")
            print(f"arr: {arr}")
            os.system(f"mv {folder}/{arr[0]} {file}")

            # solve generated example with first_iteration.lp
            ctl = clingo.Control()
            read = read_file(file)
            ctl.add("base", [], FIRST_ITERATION + read)
            print(FIRST_ITERATION)
            print(read)
            print("Successfully added")
            
            ctl.ground([("base", [])])
            print("Done with grounding.")
            with ctl.solve(yield_=True) as handle:
                model = None
                my_iter = iter(handle)
                for model in my_iter:
                    pass
                print("Found paths.")
                # format the model to asprilo format (point after each atom)
                string = ""
                for elem in list(model.symbols(shown=True)):
                    string += str(elem) + ". "

                # save the paths back into the file
                with open(file, "w") as f:
                    f.write(string)
                
