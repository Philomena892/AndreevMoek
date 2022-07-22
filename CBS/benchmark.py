# # run all examples from benchmark_examples
# # with a timelimit of 5 min for each example

import os
import signal
from socket import timeout
import sys
from node import main as run

class TimeOutException(Exception):
    def __init__(self, message='Aborted execution'):
        # Call the base class constructor with the parameters it needs
        super(TimeOutException, self).__init__(message)


problems = []
root = "./benchmark_examples/"
path = os.path.join(root, "targetdirectory")
print(type(path))

for path, subdirs, files in os.walk(root):
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

        signal.signal(signal.SIGALRM, handler)
        # timeout after 5 min
        signal.alarm(5*60)

        try:

            # horizon is size*2
            run(["-b",f"-hz={size*2}",f"{file}",f"{output}"])
            print(f"{file} successfully run.")

        except TimeOutException as exc: 
        
            print(exc)
            print(f"failed to complete testing on {file}")
        
        signal.alarm(0) # cancel timer if function returns before timeout

if __name__ == "__main__":
    main()
