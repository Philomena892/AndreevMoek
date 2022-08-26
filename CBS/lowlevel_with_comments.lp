#include "input.lp".

% "time" is the range in which movement can happen ("horizon" is given by the highlevel-program)
time(1..horizon).

% difference/change of coordinates for allowed movement
direction((X,Y)) :- X=-1..1, Y=-1..1, |X+Y|=1.

% pairs of coordinates that can be reached in one timestep via movement including their respective direction
nextto((X,Y),(DX,DY),(X',Y')) :- direction((DX,DY)), position((X,Y)), position((X',Y')),
                                 (X,Y)=(X'-DX,Y'-DY), (X',Y')=(X+DX,Y+DY).

% translating occurs to oldmove (not necessarily performative, but practical)
oldmove(R,D,T) :- occurs(object(robot, R), action(move, D), T).

% "position" include the coordinates of every robot at every time in the plan of the predecessor
position(R,C,T) :- position(robot(R),C,T).
position(R,C,T) :- oldmove(R,D,T), position(R,C',T-1),     nextto(C',D,C).

position(R,C,T) :- position(R,C,T-1), not oldmove(R,_,T), robot(R), time(T).

% The last added "constraint", or rather the restricted robot, is determined by the "constraint" not already beeing avoided by the predecessor
newConstraint(R) :- position(R,C,T), constraint(R,C,T).

% new movement for the restricted robot is generated (maximum of one move at a time)
{ move(R,D,T) : direction(D) } 1 :- time(T), newConstraint(R).

% the time of the last movement of the restricted robot is determined by there not beeing a move at a later time
1{lastmove(T) : move(R,_,T)}1 :- newConstraint(R).
:- lastmove(T), move(R,_,T'), T'>T, newConstraint(R).

% number of moves of the restricted robot
moveCount(Z) :- Z=#count{T : move(R,D,T)}.

% these "#minimize"-statements ensure optimality of the plan
#minimize{Z : moveCount(Z)}.
#minimize{T : lastmove(T)}.

% the following 6 lines are only relevent (and otherwise expensive) if the cost is not calculated in the highlevel-program
    % same as "lastmove" with the same robot, but for the old plan
    1{oldlastmove(T) : oldmove(R,_,T)}1 :- newConstraint(R).
    :- oldlastmove(T), oldmove(R,_,T'), newConstraint(R), T'>T.

    % the cost in calculated
    cost(N+N'-N'') :- lastmove(N'), old_cost(N), oldlastmove(N'').

% same as "position", but for the new path of the restricted robot
newPosition(R,C,0) :- position(robot(R),C,0), newConstraint(R).
newPosition(R,C,T)  :- move(R,D,T), newPosition(R,C',T-1),     nextto(C',D,C).
                    :- move(R,D,T), newPosition(R,C ,T-1), not nextto(C ,D,_).

newPosition(R,C,T) :- newPosition(R,C,T-1), not move(R,_,T), time(T).

% the new path has to follow the constraints for the restricted robot
:- newPosition(R,C,T), constraint(R,C,T). 

% the last positions of the new and old path have to be the same to fullfill the goal-condition
:- newPosition(R,C,horizon), position(R,C',horizon), C!=C'.

% vertex conflicts are created, if two robots have the same position at the same time (doubled coordinates to make it consistent with edge-conflicts)
conflict(R,S,C,C,T) :- position(R,C,T), position(S,C,T), R!=S, not newConstraint(R), not newConstraint(S), T>0.
conflict(R,S,C,C,T) :- newPosition(R,C,T), position(S,C,T), R!=S, not newConstraint(S), T>0.

% edge conflicts are created, if two robots swap coordinates from one time to the next (coordinates correspond to the robots in the conflict: 1-3, 2-4)
conflict(R,S,C,C',T) :- position(R,C,T), position(R,C',T-1), position(S,C',T), position(S,C,T-1), R!=S, not newConstraint(R), not newConstraint(S), T>0.
conflict(R,S,C,C',T) :- newPosition(R,C,T), newPosition(R,C',T-1), position(S,C',T), position(S,C,T-1), R!=S, not newConstraint(S), T>0.

% a single "first_conflict" is picked from "conflict" with the condition, that there may be no "conflict" at a time before "first_conflict"
1{first_conflict(R,S,C,C',T) : conflict(R,S,C,C',T)}1 :- conflict(_,_,_,_,_).
:- first_conflict(_,_,_,_,T), conflict(_,_,_,_,T'), T'<T.
