from random import randint

def make_instance(size, numRobots):

    string = ""

    for x in range(1, size+1):
        for y in range(1, size+1):
            string += f"init(object(node,{x*y}),value(at,({x},{y}))). "
    
    cooRobs = []
    cooShelfs = []
    
    for n in range(numRobots):
        r = (randint(1,size), randint(1,size))
        s = (randint(1,size), randint(1,size))
        while (r == s) or (r in cooRobs) or (s in cooShelfs):
            r = (randint(1,size), randint(1,size))
            s = (randint(1,size), randint(1,size))
        if r != s:
            cooRobs.append(r)
            cooShelfs.append(s)
            
    print(f"cooShelfs: {cooShelfs}")
    print(f"cooRobs: {cooRobs}")

    for n in range(1,numRobots+1):
        string += f"init(object(robot,{n}),value(at,{cooRobs.pop()})). "
        string += f"init(object(shelf,{n}),value(at,{cooShelfs.pop()})). "

    return string        