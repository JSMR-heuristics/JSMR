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
from cluster import Cluster


class Main(object):
    def __init__(self):
        iterations = None
        battery_file = None
        neighbourhood = input("Neighbourhood (1/2/3): ")

        cluster_option = input("Do you want to optimize the battery location? (y/n):")
        if str(cluster_option) == "y":
            Cluster(neighbourhood)
            cluster_option  = input("Pick which of the clusters in the chart are best suitable: ")
        else:
            cluster_option = None

        algorithm = str(input("Algorithm (optimize/greedy/hill): "))
        if algorithm == "greedy" or algorithm == "hill":
            iterations = input("Iterations: ")
        plot = input("Do you want intermediate plots to be made? (y/n): ")


        Smartgrid(neighbourhood, algorithm, iterations, plot, cluster_option, battery_file)


if __name__ == "__main__":
    Main()
