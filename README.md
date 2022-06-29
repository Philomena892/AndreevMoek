# AndreevMoek Plan merging project

Internship at University of Potsdam about MAPF (multi-agent path finding) with ASP and the asprilo framework.

## Examples

This directory contains example instances to test code.

## Images

Contains images of examples to be used in README files.

## Our solutions

In the folder `CBS` a version of the CBS - short for Constraint Based Search - algorithm can be found. To use our CBS first install asprilo and the asprilo visualizer (https://github.com/potassco/asprilo-seminar)

# Usage of our CBS implementation:
```
usage: node.py [-h] [-b] low_level input

positional arguments:
  low_level        ASP file with low level search
  input            ASP file containing robot plans

optional arguments:
  -h, --help       show this help message and exit
  -b, --benchmark  output benchmarked values to the command line
```  
For `low_level` either use `lowlevel.lp` or `lowlevel_greedy.lp` from the CBS folder. The first file will find an optimal solution whereas the second one is a greedy implementation. It gives a suboptimal solution but is considerably faster.

The benchmark mode will output the running time, the amount of nodes explored and the depth of the solution in the search tree.
  


First attempts:

`twoRobotsNaive.lp` contains a solution to the instance `simple_cross.lp` where there is a single vertex conflict. The conflict is solved by letting one robot wait for a single time step. 

`solve-multiple-vertexConflicts-M.lp` is a work in progress. It builds upon twoRobotsNaive.lp and is designed to solve multiple vertex conflicts between two robots. Thus it aims at the problem instance `double_cross.lp`.
