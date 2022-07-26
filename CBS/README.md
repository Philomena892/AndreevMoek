# Contents of this folder

### node.py
This file contains the high level search of our CBS implementation.
```
usage: node.py [-h] -hz HORIZON [-g] [-b] input [benchmark_file]

positional arguments:
  input                 ASP file containing robot plans
  benchmark_file        By default benchmarked values are saved in bm_output.csv.
                        Specify a file here, if you want to append them to it
                        instead.

optional arguments:
  -h, --help            show this help message and exit
  -hz HORIZON, --horizon HORIZON
                        maximum makespan the solution is allowed to have
  -g, --greedy          enable when you want to use a faster but suboptimal greedy
                        search
  -b, --benchmark       output benchmarked values to the command line

```
For more details, look at the top folder.

### lowlevel.lp
Contains the low-level search to CBS written in ASP.

### lowlevel_greedy.lp
Contains the low-level search to the greedy version of CBS. This minimizes the number of conflicts.

### gen.py
Generates single instances. The generated instances are square-shaped and random. A robot cannot be generated on its corresponding shelf.
```
usage: gen.py [-h] -s SIZE -n ROBOTS output

positional arguments:
  output                the robot plans are saved in this file

optional arguments:
  -h, --help            show this help message and exit
  -s SIZE, --size SIZE  size of generated instance (square shaped)
  -n ROBOTS, --robots ROBOTS
                        the amount of robots randomly placed on the instance
```

### make_examples.py
Run this file to generate multiple examples of different sizes and robot-densities. The problem files are created using our generator (`gen.py`) and contain the paths. 

### first_iteration.lp
Clingo generator of robot paths.

### benchmark.py
Run this to benchmark all files created by `make_examples.py`. The results will be saved in `benchmark_results.csv`.
