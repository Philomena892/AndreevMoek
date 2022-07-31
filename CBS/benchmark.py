import os
import signal
from socket import timeout
import csv
import argparse
from node import main as run
from node_greedy import main as grun
import sys


class TimeOutException(Exception):
    '''Define an exception to use for a timeout.'''
    def __init__(self, message='Aborted execution'):
        # Call the base class constructor with the parameters it needs
        super(TimeOutException, self).__init__(message)

def handler(signum, frame):
    '''Register a signal handler for a timeout.'''
    raise TimeOutException()
    
           
def main():

    '''
    Runs CBS or greedy-CBS on all examples from any folder 
    (but preferably benchmark_examples which is created by make_examples.py)
    but with a timelimit of 5 min for each example.
    If a different folder is chosen, the size has to be manually set in the code (line 63).
    Writes the results in a csv file "benchmark_results.csv".

    Comment:
    SIGALRM does not work under windows. To develop compatibility check this out: 
    https://stackoverflow.com/questions/8420422/python-windows-equivalent-of-sigalrm
    For now runs under windows without the timer.

    usage: benchmark.py [-h] [-g] [directory]

    positional arguments:
        directory     By default runs tests on directory '.benchmark_examples/'. Specify a different name here, if you want to benchmark a different directory

    optional arguments:
        -h, --help    show this help message and exit
        -g, --greedy  enable when you want to test the greedy implementation
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument("-g","--greedy", help="enable when you want to test the greedy implementation", action="store_true")
    parser.add_argument('directory', nargs='?', type=str, default="./benchmark_examples/", help="By default runs tests on directory '.benchmark_examples/'. Specify a different name here, if you want to benchmark a different directory")
    args = parser.parse_args()


    if not os.path.isdir(args.directory):
        sys.exit(f"{args.directory} is not a directory")

    path = args.directory

    # list of files to benchmark on
    problems = []
    for path, subdirs, files in os.walk(args.directory):
        for name in files:
            problems.append(os.path.join(path, name))

    problems.sort()
    
    output = "benchmark_results.csv"

    for file in problems:

        stats = file.split("/")
        
        # size has to be manually set if different dir than benchmark_examples
        if args.directory == "num_robots_benchmark":
            size = 7
        # size of example set from file name
        else: size = int(stats[2][-1])
       
        # density = int(stats[3][-2])
        # num = int(stats[4].split(".")[0].split("x")[1])

        if sys.platform != "win32":
            signal.signal(signal.SIGALRM, handler)
            # timeout after 5 min
            signal.alarm(5*60)

        try:
            # horizon is size*2
            if args.greedy:
                grun(["-b",f"-hz={size*2}",f"{file}",f"{output}"])
            else:
                run(["-b",f"-hz={size*2}",f"{file}",f"{output}"])
            print(f"{file} successfully run.")

        except TimeOutException as exc: 
        
            print(exc)
            print(f"failed to complete testing on {file}")
            with open(output, 'a', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([f'{file}'])                
        if sys.platform != "win32":
            signal.alarm(0) # cancel timer if function returns before timeout

if __name__ == "__main__":
    main()
