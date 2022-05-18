# AndreevMoek Plan merging project

Internship at University of Potsdam about MAPF (multi-agent path finding) with ASP and the asprilo framework.

## Examples

This directory contains example instances to test code.

## Images

Contains images of examples to be used in README files.

## Our solutions

Our work so far can be found in the main directory.

`twoRobotsNaive.lp` contains a solution to the instance `simple_cross.lp` where there is a single vertex conflict. The conflict is solved by letting one robot wait for a single time step. 

`solve-multiple-vertexConflicts-M.lp` is a work in progress. It builds upon twoRobotsNaive.lp and is designed to solve multiple vertex conflicts between two robots. Thus it aims at the problem instance `double_cross.lp`.
