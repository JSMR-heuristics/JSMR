import sys
from pathlib import Path
import os

# option 1
cwd = os.getcwd()
path = os.path.join(*[cwd, 'code', 'algorithms'])
sys.path.append(path)

from smartgrid import Smartgrid
from cluster import Cluster

if "spec" in sys.argv:
    spec = True
else:
    if sys.argv[1] in ["1", "2", "3"]:
        neighbourhood = int(sys.argv[1])
    else:
        print("please insert either a valid neighbourhood number or \"spec\" as 1st argument")
        print("select from: 1, 2, 3, \"spec\"")
        sys.exit(2)

    if sys.argv[2] in ["stepdown", "greedy", "hill", "cluster"]:
        algorithm = sys.argv[2]
        cluster_option = None
        battery_file = None

    else:
        print("please insert the wanted algorithm as 2nd argument")
        print("select from: \"stepdown\", \"greedy\", \"hill\", \"cluster\",\"spec\"")
        sys.exit(2)

    if sys.argv[2] == "stepdown":
            iterations = 1
    else:
        if sys.argv[3].isnumeric():
            iterations = int(sys.argv[3])
        else:
            print("please insert an integer as 3rd argument if you're running either greedy or hillclimber")
            sys.exit(2)

    if "plot" in sys.argv:
        plot = "y"
    else:
        plot = "n"

class Main(object):
    def __init__(self):
        if spec is True:
            iterations = None
            battery_file = None
            neighbourhood = input("Neighbourhood (1/2/3): ")

            cluster_option = input("Do you want to optimize the battery location? (y/n):")
            if str(cluster_option) == "y":
                Cluster(neighbourhood)
                cluster_option  = input("Pick which of the clusters in the chart are best suitable: ")
            else:
                cluster_option = None

            algorithm = str(input("Algorithm (stepdown/greedy/hill): "))
            if algorithm == "greedy" or algorithm == "hill":
                iterations = input("Iterations: ")
            plot = input("Do you want intermediate plots to be made? (y/n): ")


        Smartgrid(neighbourhood, algorithm, iterations, plot, cluster_option, battery_file)


if __name__ == "__main__":
    Main()
