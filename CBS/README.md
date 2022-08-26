# How to run our CBS or greedy-CBS implementation? 
Download node.py (for CBS) and node_greedy.py (for greedy-CBS) as well as their corresponding low-level searches: lowlevel.lp and lowlevel_greedy.lp.

* for CBS:

Execute `python node.py [-h] -hz HORIZON [-b] input [benchmark_file]` over the command-line. The HORIZON is the maximum amount of timesteps the solution is allowed to take. This should be set as low as possible so that it still allows a solution - the implementation will be faster this way. We recommend setting the horizon to lenght * width of the instance - generally this should be high enough. Then just specify the instance-file as input.

* for greedy-CBS use the same format


# Contents of this folder

### benchmarkResults and inc_benchmarkResults

These two folders contain test results in form of .csv files from benchmarking our implementations:

------benchmarkResults---------------------------------------------
The results in this folder are based on instances with different sizes (5x5, 6x6, 7x7, 8x8) and densities (20%, 25%, 30%, 35%, 40%).
------inc_benchmarkResults-----------------------------------------
These results are based on adding one robot after the other to an instance and each time benchmarking our implementations. The amount of robots starts with 2 robots and goes up to 19, which roughly corresponds to a 40% robot density on the 7x7 field. Since our greedy implementation is still performant enough for more robots, there are also test results with the amount of robots going up to 35 which corresponds to a 70% density.

### benchmark.py
'''
usage: benchmark.py [-h] [-g] [directory]

positional arguments:
  directory     By default runs tests on directory '.benchmark_examples/'. Specify a different name here, if you want
                to benchmark a different directory

optional arguments:
  -h, --help    show this help message and exit
  -g, --greedy  enable when you want to test the greedy implementation
'''
This program can be used - with some adjustments to the file format - to run node.py or node_greedy.py on a folder of problem instances. It is designed to run on instances produced by `make_examples.py` and saves the results in `benchmark_results.csv`.

### dataAnalysis.ipynb
Jupyter Notebook containing results of analyzing the benchmarking results.

### first_iteration.lp and first_iteration_one_rob.lp
Deprecated ASP programs that compute initial paths (containing conflicts) for all or only one robot.

### gen.py
Creates a random instance, including an initial plan, with specified grid size and number of robots/shelfs. The generated instances are square-shaped and a robot cannot be generated on its corresponding shelf.
'''  
usage: gen.py [-h] -s SIZE -n ROBOTS output
positional arguments:
    output                  the robot plans are saved in this file
optional arguments:
    -h, --help              show this help message and exit
    -s SIZE, --size SIZE    size of generated instance (square shaped)
    -n ROBOTS, --robots ROBOTS
                            the amount of robots randomly placed on the instance
'''

### lowlevel.lp, lowlevel_alternative.lp and lowlevel_greedy.lp
The low-level searches corresponding to the high-level python searches.

##### They utilize the following cost functions:

* **lowlevel/lowlevel_alternative:** sum of last movement (the time of each robots last move is added up and makes up the cost)
* **lowlevel_greedy:** sum of conflicts (all the conflicts are counted  and make up the cost)

### lowlevel_with_conflicts.lp

### make_examples.py 
Run this file to generate multiple examples of different sizes and robot-densities. The problem files are created using our generator (`gen.py`) and contain the paths. 

### make_inc_examples.py
Creates a folder with example instances containing MIN_ROBOTS to MAX_ROBOTS robots. For example: The instance 3robs.lp consists of
2robs.lp with one added robot and its paths.

### node.py, node_alternative.py and node_greedy.py
```
usage: node.py [-h] -hz HORIZON [-b] input [benchmark_file]
    positional arguments:
        input                 ASP file containing robot plans
        benchmark_file        By default benchmarked values are saved in bm_output.csv. Specify a file here, if you want to append them to it instead.
    optional arguments:
        -h, --help            show this help message and exit
        -hz HORIZON, --horizon HORIZON
                              maximum makespan the solution is allowed to have
        -b, --benchmark       save and output benchmarked values
```  
The node.py and node_alternative.py implementations will find an optimal solution. Meanwhile node_greedy.py gives a suboptimal solution but is considerably faster.

The benchmark mode will output multiple values:
* the running time
* the amount of nodes explored 
* the depth of the solution in the search tree
* the amount of timesteps needed to solve the problem
* the sum of all the steps taken by the robots
* and the amount of initial conflicts in the instance

Additionally, benchmarked values are written into a .csv file. If no filename is specified, by default they are saved in `bm_output.csv`. This file gets overwritten if another example is run. If you want to append the benchmark output to a csv file, specify the filename at the end.  
