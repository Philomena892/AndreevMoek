# # run all examples from benchmark_examples
# # with a timelimit of 5 min for each example

import os
import signal
from socket import timeout
import csv
import argparse
from node import main as run
from node_greedy import main as grun
import sys

class TimeOutException(Exception):
    def __init__(self, message='Aborted execution'):
        # Call the base class constructor with the parameters it needs
        super(TimeOutException, self).__init__(message)


parser = argparse.ArgumentParser()
parser.add_argument("-g","--greedy", help="enable when you want to test the greedy implementation", action="store_true")
parser.add_argument('directory', nargs='?', type=str, default="./benchmark_examples/", help="By default runs tests on directory '.benchmark_examples/'. Specify a different name here, if you want to benchmark a different directory")
args = parser.parse_args()




if not os.path.isdir(args.directory):
    sys.exit(f"{args.directory} is not a directory")

path = os.path.join(args.directory, "targetdirectory")
print(type(path))

problems = []
for path, subdirs, files in os.walk(args.directory):
    for name in files:
        problems.append(os.path.join(path, name))


print(problems) # contains all filenames in this and subdirectories
problems.sort()


# Register a handler for the timeout
def handler(signum, frame):
    raise TimeOutException()
    
           
# Register the signal function handler
def main():
    

    output = "benchmark_results.csv"

    for file in problems:

        stats = file.split("/")
        print(stats)
        
        size = int(stats[2][-1])
        density = int(stats[3][-2])
        num = int(stats[4].split(".")[0].split("x")[1])

        if size < 8: continue
        if size == 8 and density < 4: continue
        if size == 8 and density == 4 and num not in [8,9]: continue

        signal.signal(signal.SIGALRM, handler)
        # timeout after 5 min
        signal.alarm(5*60)

        try:

            # horizon is size*2
            if args.greedy:
                grun(["-b","-g",f"-hz={size*2}",f"{file}",f"{output}"])
            else:
                run(["-b",f"-hz={size*2}",f"{file}",f"{output}"])
            print(f"{file} successfully run.")

        except TimeOutException as exc: 
        
            print(exc)
            print(f"failed to complete testing on {file}")
            with open(output, 'a', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([f'{file}'])                

        signal.alarm(0) # cancel timer if function returns before timeout

if __name__ == "__main__":
    main()
