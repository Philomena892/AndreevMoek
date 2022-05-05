#include "../input.lp".

%#const horizon=1.
time(1..horizon).

direction((X,Y)) :- X=-1..1, Y=-1..1, |X+Y|=1.
nextto((X,Y),(DX,DY),(X',Y')) :- direction((DX,DY)), position((X,Y)), position((X',Y')),
                                 (X,Y)=(X'-DX,Y'-DY), (X',Y')=(X+DX,Y+DY).

oldmove(R,D,T) :- occurs(object(robot, R), action(move, D), T).
coo(R,C,T) :- position(robot(R),C,T).

% - oldmove/3 ----------------------------------------------------------------------
coo(R,C,T) :- oldmove(R,D,T), coo(R,C',T-1),     nextto(C',D,C).
                :- oldmove(R,D,T), coo(R,C ,T-1), not nextto(C ,D,_).

% - conflicts -------------------------------------------------------------------
conflict(R,S,T):- R<S, coo(R,C,T), coo(S,C,T).

{move(S,D,T) : oldmove(S,D,T)} 1 :- conflict(R,S,T'), T < T', time(T).

% - Voraussetzung: Roboter R verlässt sofort das sinkende Schiff.
move(R,D,T):- conflict(R,S,T), oldmove(R,D,T).
move(S,D,T+1):- conflict(R,S,T), oldmove(S,D,T).

%move(R,D,T) :- oldmove(R,D,_), nextto()