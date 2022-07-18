#include "input.lp".

#const horizon=15.
time(1..horizon).

direction((X,Y)) :- X=-1..1, Y=-1..1, |X+Y|=1.
nextto((X,Y),(X',Y'),(X+X',Y+Y')) :- position((X,Y)), direction((X',Y')), position((X+X',Y+Y')).

{ move(robot(rob),D,T) : direction(D) } 1 :- time(T).

position(R,C,T) :- move(R,D,T), position(R,C',T-1),     nextto(C',D,C).
                :- move(R,D,T), position(R,C ,T-1), not nextto(C ,D,_).

position(R,C,T) :- position(R,C,T-1), not move(R,_,T), isRobot(R), time(T).

moveSum(Z) :- Z=#sum{T : move(R,D,T), robot(R)}.
#minimize{Z : moveSum(Z)}.

:- position(shelf(rob),C,0), position(robot(rob),C',horizon), C!=C'.

#show.
#show init/2.
#show occurs(object(robot,R), action(move,D), T) : move(robot(R),D,T). 
