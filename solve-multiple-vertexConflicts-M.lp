#include "../input.lp".

%#const horizon=1.
time(1..horizon).

direction((X,Y)) :- X=-1..1, Y=-1..1, |X+Y|=1.
nextto((X,Y),(DX,DY),(X',Y')) :- direction((DX,DY)), position((X,Y)), position((X',Y')),
                                 (X,Y)=(X'-DX,Y'-DY), (X',Y')=(X+DX,Y+DY).

oldmove(R,D,T) :- occurs(object(robot, R), action(move, D), T).
coo(R,C,T) :- position(robot(R),C,T).

% - conflicts -------------------------------------------------------------------
conflict(R,S,T)         :- vertex_conflict(R,S,T).
vertex_conflict(R,S,T)  :- R<S, coo(R,C,T), coo(S,C,T), move(robot(R),D,T), nextmove(robot(S),D',T), D != D'.

% - coo/3 -----------------------------------------------------------------------
% to have position of robots at every timepoint

coo(R,C,T) :- move(robot(R),D,T), coo(R,C',T-1), nextto(C',D,C).
           :- move(robot(R),D,T), coo(R,C ,T-1), not nextto(C ,D,_).


% give priority to the first robot and copy its old path
{ move(robot(R),D,T) }  :- oldmove(R,D,T).
move(robot(R),D,T)      :- conflict(R,S,_), oldmove(R,D,T).


% copy all old moves for the second robot up to the first conflict
nextmove(S,D,T) :- move(robot(S),D,T-1), oldmove(S,D,T).

wait(S,T)   :- conflict(R,S,T).
move(robot(S),D,T+Z) :- conflict(R,S,_), oldmove(S,D,T), Z = #sum{1: wait(S,T')}, T' <= T, time(T'), time(Z).

% idea: plan ahead and use these for identifying conflicts w/o the moves
nextmove(S,D,T+Z)   :- conflict(R,S,_), oldmove(S,D,T+1), Z = #sum{wait(S,T')}, T' <= T, time(T'), time(Z).

nextcoo(R,C,T)  :- nextmove(R,D,T), coo(R,C',T-1), nextto(C',D,C).
                :- nextmove(R,D,T), coo(R,C ,T-1), not nextto(C ,D,_).


% take different actions depending on the type of the conflict
% vertex_conflict: second robot waits for one time point

%move(robot(A),D,T):- oldmove(A,D,T), not conflict(_,_,_).

% last idea: Produce nextmove always one stop ahead of time, to first check for conflicts
% it is enough to have nextmove for robot S