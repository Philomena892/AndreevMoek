#include "input.lp".

#const horizon=15.
time(1..horizon).

direction((X,Y)) :- X=-1..1, Y=-1..1, |X+Y|=1.
nextto((X,Y),(DX,DY),(X',Y')) :- direction((DX,DY)), position((X,Y)), position((X',Y')),
                                 (X,Y)=(X'-DX,Y'-DY), (X',Y')=(X+DX,Y+DY).

{ move(R,D,T) : direction(D) } 1 :- isRobot(R), time(T).

position(R,C,T) :- move(R,D,T), position(R,C',T-1),     nextto(C',D,C).
                :- move(R,D,T), position(R,C ,T-1), not nextto(C ,D,_).

:- position(shelf(S),C,0), position(robot(S),C',horizon), C!=C'.

position(R,C,T) :- position(R,C,T-1), not move(R,_,T), time(T).

1{lastmove(R,T) : time(T)}1 :- isRobot(R).
:- lastmove(R,T), move(R,_,T'), T'>T.

#minimize{T,R : lastmove(R,T)}.

#show.
#show init/2.
#show occurs(object(robot,R), action(move,D), T) : move(robot(R),D,T). 
