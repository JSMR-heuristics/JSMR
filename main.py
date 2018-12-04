import sys
from pathlib import Path
import os

# option 1
cwd = os.getcwd()
path = os.path.join(*[cwd, 'code', 'algorithms'])
sys.path.append(path)

# # option 2
# path = str(Path.cwd())
# loc = path.find("JSMR")
# path = path[0:loc+5]
# for dirpath, dirnames, filenames in os.walk(path):
#     for filename in filenames:
#         if (filename == "smartgrid.py"):
#             sys.path.append(dirpath)
#             break
from smartgrid import Smartgrid


class Main(object):
    def __init__(self):
        iterations = None
        neighbourhood = input("Neighbourhood: ")
        algorithm = input("Algorithm: ")
        if str(algorithm) == "greedy":
            iterations = input("Iterations: ")
        plot = input("Do you want intermediate plots to be made? (y/n): ")

        Smartgrid(neighbourhood, algorithm, iterations, plot)


if __name__ == "__main__":
    Main()
