import os
from gen import main as generate

# for each size and density always generate three random examples
SIZE = [5, 6, 7, 8]
DENSITY = [0.2] #[0.2, 0.3, 0.4]

os.system(f"mkdir benchmark_examples")
for size in SIZE:

    print(f"Currently working on size: {size}x{size}")
    dir = f"./benchmark_examples/size{size}x{size}"
    os.system(f"mkdir {dir}")

    for density in DENSITY:

        print(f"Working on examples with density {density}.")
        folder = f"{dir}/density{int(density * 100)}"
        os.system(f"mkdir {folder}")

        for i in range(1,2): 

            print(f"Example Number {i}.")
    
            numRobots = int((size**2) * density)
            file = f"./{folder}/ex{i}.lp"
            
            # generate random new example with appropriate sizes
            generate([f"-s={size}", f"-n={numRobots}", f"{file}"])
            exit()
