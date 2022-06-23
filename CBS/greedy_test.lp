#include "input.lp".

#const horizon=15.
time(1..horizon).

direction((X,Y)) :- X=-1..1, Y=-1..1, |X+Y|=1.

nextto((X,Y),(DX,DY),(X',Y')) :- direction((DX,DY)), position((X,Y)), position((X',Y')),
                                 (X,Y)=(X'-DX,Y'-DY), (X',Y')=(X+DX,Y+DY).

oldmove(R,D,T) :- occurs(object(robot, R), action(move, D), T).

position(R,C,T) :- position(robot(R),C,T).
position(R,C,T) :- oldmove(R,D,T), position(R,C',T-1),     nextto(C',D,C).

position(R,C,T) :- position(R,C,T-1), not oldmove(R,_,T), robot(R), time(T).

newConstraint(R) :- position(R,C,T), constraint(R,C,T).

{ move(R,D,T) : direction(D) } 1 :- time(T), newConstraint(R).

moveSum(Z) :- Z=#sum{T : move(R,D,T)}.
#minimize{Z : moveSum(Z)}.

newPosition(R,C,0) :- position(robot(R),C,0), newConstraint(R).
newPosition(R,C,T)  :- move(R,D,T), newPosition(R,C',T-1),     nextto(C',D,C).
                    :- move(R,D,T), newPosition(R,C ,T-1), not nextto(C ,D,_).

newPosition(R,C,T) :- newPosition(R,C,T-1), not move(R,_,T), time(T).
:- newPosition(R,C,T), constraint(R,C,T). 

:- newPosition(R,C,horizon), position(R,C',horizon), C!=C'.

conflict(R,S,C,C,T) :- position(R,C,T), position(S,C,T), R!=S, not newConstraint(R), not newConstraint(S), T>0.
conflict(R,S,C,C,T) :- newPosition(R,C,T), position(S,C,T), R!=S, not newConstraint(S), T>0.

conflict(R,S,C,C',T) :- position(R,C,T), position(R,C',T-1), position(S,C',T), position(S,C,T-1), R!=S, not newConstraint(R), not newConstraint(S), T>0.
conflict(R,S,C,C',T) :- newPosition(R,C,T), newPosition(R,C',T-1), position(S,C',T), position(S,C,T-1), R!=S, not newConstraint(S), T>0.

cost(Z) :- Z=#count{R,S,C,C',T : conflict(R,S,C,C',T)}.

1{first_conflict(R,S,C,C',T) : conflict(R,S,C,C',T)}1 :- conflict(_,_,_,_,_).
:- first_conflict(_,_,_,_,T), conflict(_,_,_,_,T'), T'<T.
