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
vertex_conflict(R,S,T)  :- R<S, coo(R,C,T), nextcoo(S,C,T), move(robot(R),D,T), nextmove(S,D',T), D != D'.


% - coo/3 -----------------------------------------------------------------------
% to have position of robots at every timepoint

coo(R,C,T) :- move(robot(R),D,T), coo(R,C',T-1), nextto(C',D,C).
           :- move(robot(R),D,T), coo(R,C ,T-1), not nextto(C ,D,_).

coo(R,C,T) :- wait(R,T), coo(R,C,T-1), time(T).
coo(R,C,T) :- not oldmove(R,_,T), coo(R,C,T-1), time(T-1), robot(R), robot(S), R<S.

% give priority to the first robot and copy its old path
{ move(robot(R),D,T) }  :- oldmove(R,D,T).
move(robot(R),D,T)      :- conflict(R,S,_), oldmove(R,D,T). 


% copy all old moves for the second robot up to the first conflict
nextmove(R,D,1) :- oldmove(R,D,1).

nextmove(R,D,T) :- move(robot(R),D,T-1), oldmove(R,D,T).
nextcoo(R,C,T)  :- nextmove(R,D,T), coo(R,C',T-1), nextto(C',D,C).

% when to wait and for how long
wait(S,T)   :- conflict(R,S,T).
numwait(Z,T) :- Z = #count{S,T': wait(S,T'), T>=T'}, time(T).

% moves for second robot
move(robot(S),D,T+Z) :- numwait(Z,T), oldmove(S,D,T), not wait(S,T+Z), vertex_conflict(R,S,_).
move(robot(S),D,T+Z+1) :- numwait(Z,T), oldmove(S,D,T), wait(S,T+Z), vertex_conflict(R,S,_).

% take different actions depending on the type of the conflict
% vertex_conflict: second robot waits for one time point

move(robot(A),D,T):- oldmove(A,D,T), not conflict(_,_,_).
