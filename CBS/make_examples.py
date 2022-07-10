import os
import sys
import clingo


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
SIZE = [8, 16, 24]
DENSITY = [0.1, 0.2, 0.3, 0.4, 0.5]
FIRST_ITERATION = read_file("first_iteration.lp")
SHOWS = '''#show.
        #show init/2.
        #show occurs(object(robot,R), action(move,D), T) : move(robot(R),D,T).''' 


os.system(f"mkdir benchmark_examples")
for size in SIZE:

    print(f"Currently working on size: {size}x{size}")
    dir = f"./benchmark_examples/size{size}x{size}"
    os.system(f"mkdir {dir}")

    for density in DENSITY:

        print(f"Working on examples with density {density}.")
        folder = f"{dir}/density{int(density * 100)}"
        os.system(f"mkdir {folder}")

        for i in range(1,4):

            print(f"Example Number {i}.")
    
            numRobots = int((size**2) * density)
            file = f"./{folder}/ex{i}.lp"
            
            # generate new example with appropriate sizes
            # take out > /dev/null 2>&1 to see output
            os.system(f"gen -x {size} -y {size} -r {numRobots} -s {numRobots} -d {folder} --random > /dev/null 2>&1")
            
            # rename file to ex[i].lp, so it is not overwritten in next iteration 
            arr = os.listdir(f"./{folder}")
            os.system(f"mv {folder}/{arr[0]} {file}")

            # solve generated example with first_iteration.lp
            ctl = clingo.Control()
            ctl.add("base", [], FIRST_ITERATION + SHOWS + read_file(file))
            
            ctl.ground([("base", [])])
            with ctl.solve(yield_=True) as handle:
                model = None
                my_iter = iter(handle)
                for model in my_iter:
                    pass
                
                # format the model to asprilo format (point after each atom)
                string = ""
                for elem in list(model.symbols(shown=True)):
                    string += str(elem) + ". "

                # save the paths back into the file
                with open(file, "w") as f:
                    f.write(string)

