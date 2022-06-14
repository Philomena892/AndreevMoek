#include "../input.lp".

oldmove(R,D,T) :- occurs(object(robot, R), action(move, D), T).

%#const horizon=1.
time(1..horizon).

direction((X,Y)) :- X=-1..1, Y=-1..1, |X+Y|=1.

nextto((X,Y),(DX,DY),(X',Y')) :- direction((DX,DY)), position((X,Y)), position((X',Y')),
                                 (X,Y)=(X'-DX,Y'-DY), (X',Y')=(X+DX,Y+DY).

% positions of the robots in the former model
position(R,C,T) :- position(robot(R),C,T).
position(R,C,T) :- oldmove(R,D,T), position(R,C',T-1),     nextto(C',D,C).

position(R,C,T) :- position(R,C,T-1), not oldmove(R,_,T), robot(R), time(T).

newConstraint(0).

% single out the latest added constraint
newConstraint(R) :- position(R,C,T), constraint(R,C,T).

% generate new minimal route for robot R with newConstraint
{ move(R,D,T) : direction(D) } 1 :- time(T), newConstraint(R), robot(R).

#minimize{T : move(R,D,T)}.

% check for valid routes
newPosition(R,C,0) :- position(robot(R),C,0), newConstraint(R).
newPosition(R,C,T)  :- move(R,D,T), newPosition(R,C',T-1),     nextto(C',D,C).
                    :- move(R,D,T), newPosition(R,C ,T-1), not nextto(C ,D,_).

newPosition(R,C,T) :- newPosition(R,C,T-1), not move(R,_,T), time(T).
:- newPosition(R,C,T), constraint(R,C,T). 

% goal fullfilled
:- newPosition(R,C,horizon), position(R,C',horizon), C!=C'.

% calculate conflicts

% vertex conflicts
conflict(R,S,C,T) :- position(R,C,T), position(S,C,T), R<S, not newConstraint(R), not newConstraint(S), T>0.
conflict(R,S,C,T) :- newPosition(R,C,T), position(S,C,T), not newConstraint(S), T>0.

% edge conflicts
conflict(R,S,C,T) :- position(R,C,T), position(R,C',T-1), position(S,C',T), position(S,C,T-1), R<S, not newConstraint(R), not newConstraint(S), T>0.
conflict(R,S,C,T) :- newPosition(R,C,T), newPosition(R,C',T-1), position(S,C',T), position(S,C,T-1), R!=S, not newConstraint(S), T>0.

% first conflict
1{first_conflict(R,S,C,T) : conflict(R,S,C,T)}1 :- conflict(_,_,_,_).
#minimize{T : first_conflict(R,S,C,T)}.
%:- first_conflict(_,_,_,T), conflict(_,_,_,T'), T'<T. %mit Benchmark testen?

#show.
#show init/2.
#show occurs(object(robot,R), action(move,D),     T) :    move(R,D,T).
#show occurs(object(robot,R), action(move,D),     T) :    oldmove(R,D,T), not newConstraint(R).
#show conflict(R,S,C,T) : conflict(R,S,C,T).
#show first_conflict(R,S,C,T) : first_conflict(R,S,C,T).
