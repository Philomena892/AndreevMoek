# # run all examples from benchmark_examples
# # with a timelimit of 5 min for each example

import os
import signal
import sys
from node import main as run

problems = []
root = "./benchmark_examples/"
path = os.path.join(root, "targetdirectory")
print(type(path))

for path, subdirs, files in os.walk(root):
    for name in files:
        problems.append(os.path.join(path, name))


print(problems) # contains all filenames in this and subdirectories


# Register a handler for the timeout
def handler(signum, frame):
    print("Aborted execution")
    raise Exception("timeout")
    

# This function *may* run for an indetermined time...
def run_example(problem, output):

    
    stats = problem.split("/")
    print(stats)
    
    size = int(stats[2][-1])
    print(size)

    # horizon is size*2
    # > /dev/null 2>&1 to get no output
    os.system(f"python node.py -b -hz {size*2} {problem} {output}")
    print(f"{problem} successfully run.")
    return
    
           
# Register the signal function handler
def main():
    

    output = "benchmark_results.csv"

    for file in problems:

        signal.signal(signal.SIGALRM, handler)
        # timeout after 3 min
        signal.alarm(3*60)

        stats = file.split("/")
        print(stats)
        
        size = int(stats[2][-1])
        print(size)
        
        try:

            # horizon is size*2
            run(["-b",f"-hz={size*2}",f"{file}",f"{output}"])
            print(f"{file} successfully run.")

        except Exception as exc: 
        
            print(exc)
            print(f"failed to complete testing on {file}")
        
        signal.alarm(0) # cancel timer if function returns before timeout

if __name__ == "__main__":
    main()
