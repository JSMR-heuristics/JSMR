import sys
from pathlib import Path
import os
cwd = os.getcwd()
path = os.path.join(*[cwd, 'code', 'algorithms'])
sys.path.append(path)

from smartgrid import Smartgrid

class Main(object):
    def __init__(self):
        iterations = None
        neighbourhood = input("Neighbourhood: ")
        algorithm = input("Algorithm: ")
        if str(algorithm) == "greedy":
            iterations = input("Iterations: ")
        plot = input("Do you want intermediate plots to be made? (y/n): ")
        # print(algorithm)
        # print(iterations)

        Smartgrid(neighbourhood, algorithm, iterations, plot)


if __name__ == "__main__":
    Main()
