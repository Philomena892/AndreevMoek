# # run all examples from benchmark_examples
# # with a timelimit of 5 min for each example

import os
import signal

problems = []
root = "./benchmark_examples/"
path = os.path.join(root, "targetdirectory")

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

    os.system(f"python node.py -b {problem} {output} > /dev/null 2>&1")
    print(f"{problem} successfully run.")
    return
    
           
# Register the signal function handler
def main():
    

    output = "benchmark_results.csv"

    for file in problems:

        signal.signal(signal.SIGALRM, handler)
        # timeout after 5 min
        signal.alarm(5 * 60)

        try:
            run_example(file, output)
        except Exception as exc: 
            print(exc)
            print(f"failed to complete testing on {file}")
        
        signal.alarm(0) # cancel timer if function returns before timeout

if __name__ == "__main__":
    main()
