#include "../input.lp".

%#const horizon=1.
time(1..horizon).

direction((X,Y)) :- X=-1..1, Y=-1..1, |X+Y|=1.
nextto((X,Y),(DX,DY),(X',Y')) :- direction((DX,DY)), position((X,Y)), position((X',Y')),
                                 (X,Y)=(X'-DX,Y'-DY), (X',Y')=(X+DX,Y+DY).

oldmove(R,D,T) :- occours(object(robot, R), action(oldmove, D), T).

% - oldmove/3 ----------------------------------------------------------------------
position(R,C,T) :- oldmove(R,D,T), position(R,C',T-1),     nextto(C',D,C).
                :- oldmove(R,D,T), position(R,C ,T-1), not nextto(C ,D,_).

% - conflicts -------------------------------------------------------------------
{conflict(R,S,T) : position(R,C,T), position(S,C,T)} 1 :- isRobot(R), isRobot(S).

{move(R,D,T) : oldmove(R,D,T)} 1 :- conflict(R,S,T'), T < T'.

% Voraussetzung: Roboter R verlässt sofort das sinkende Schiff.
move(R,D,T):- conflict(R,S,T), position(R,D,T)
move(S,D,T+1):- conflict(R,S,T), position(S,D,T)