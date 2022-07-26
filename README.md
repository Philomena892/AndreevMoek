# AndreevMoek Plan merging project

Internship at University of Potsdam about MAPF (multi-agent path finding) with ASP and the asprilo framework.

## Examples

This directory contains example instances to test code.

## Images

Contains images of examples to be used in README files.

## Our solutions

In the folder `CBS` a version of the CBS - short for Constraint Based Search - algorithm can be found. To use our CBS first install asprilo and the asprilo visualizer (https://github.com/potassco/asprilo-seminar)

### Our cost functions

lowlevel: sum of costs (the time of every move is added up and makes up the cost)

lowlevel_greedy: sum of conflicts (all the conflicts are counted  and make up the cost)

# Usage of our CBS implementation:
```
usage: node.py [-h] [-b] [-g] input [benchmark_file]

positional arguments:
  input            ASP file containing robot plans
  benchmark_file   By default benchmarked values are saved in bm_output.csv. Specify a file here,
                   if you want to append them to it instead.

optional arguments:
  -h, --help       show this help message and exit
  -b, --benchmark  output benchmarked values to the command line
  -g, --greedy     enable when you want to use a faster but suboptimal greedy search
```  
The CBS implementation will find an optimal solution whereas the -g flag enables a greedy implementation. It gives a suboptimal solution but is considerably faster.

The benchmark mode will output multiple values:
* the running time
* the amount of nodes explored 
* the depth of the solution in the search tree
* the amount of timesteps needed to solve the problem
* and the sum of all the steps taken by the robots

Additionally, benchmarked values are written into a .csv file. If no filename is specified, by default they are saved in `bm_output.csv`. This file gets overwritten if another example is run. If you want to append the benchmark output to a csv file, specify the filename at the end.  
