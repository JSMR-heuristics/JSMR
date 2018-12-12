import sys
import os

# option 1
cwd = os.getcwd()
path = os.path.join(*[cwd, 'code', 'algorithms'])
sys.path.append(path)

from smartgrid import Smartgrid
from cluster import Cluster
from configure import Configure
from weights import Weights
from helpers import *


class Main(object):
    def __init__(self):
        if len(sys.argv) is 1:
            print("python main.py <1, 2, 3> <algorithm> <iterations>")
            sys.exit()
        if "spec" in sys.argv:
            iterations = None
            battery_file = None
            neighbourhood = input("Neighbourhood (1/2/3): ")

            cluster_option = input("Do you want to optimize the battery "
                                   "location? (y/n):")
            if str(cluster_option) == "y":
                Cluster(neighbourhood)
                cluster_option = input("Pick which of the clusters in the "
                                       "chart are best suitable: ")
            else:
                cluster_option = None

            algorithm = str(input("Algorithm (stepdown/greedy/hill/"
                                  "configure): "))

            if algorithm == "greedy" or algorithm == "hill":
                iterations = input("Iterations: ")
            plot = input("Do you want intermediate plots to be made? (y/n): ")

        else:
            # neighbourhood
            if sys.argv[1] in ["1", "2", "3"]:
                neighbourhood = int(sys.argv[1])
            else:
                print("please insert either a valid neighbourhood number or "
                      "\"spec\" as 1st argument")
                print("select from: 1, 2, 3, \"spec\"")
                sys.exit(2)

            # iteration here due to configure needing iterations
            if sys.argv[2] == "stepdown":
                    iterations = 1
                    print("num2")
            else:
                if sys.argv[3].isnumeric():
                    iterations = int(sys.argv[3])
                    print("num2")
                else:
                    print("No #iteration given, will be set to 1000")
                    iterations = 1000

            if sys.argv[2] in ["stepdown", "greedy", "hill", "dfs", "bnb"]:
                algorithm = sys.argv[2]
                cluster_option = None
                battery_file = None


                if ("cluster" in sys.argv) and not("configure" in sys.argv):
                    cluster = Cluster(neighbourhood)
                    costs = []
                    min_cost = 999999
                    index = 0
                    for i in cluster.options_list:
                        print(f"Checking option {i}...")
                        smart = Smartgrid(neighbourhood, "greedy", 1000, "n", i)
                        if smart.cost < min_cost:
                            file = smart.pickle_file
                            min_cost = smart.cost
                            index = i
                    print(file)
                    load_pickle(self, file)
                    sys.exit()

                elif ("configure" in sys.argv) and not ("cluster" in sys.argv):
                    Configure(neighbourhood)
                    Weights(neighbourhood, algorithm, iterations)
                    sys.exit()

            else:
                print("please insert the preferred algorithm as 2nd argument")
                print("select from: \"stepdown\", \"greedy\", \"hill\", "
                      "\"cluster\", \"configure\", \"spec\"")
                sys.exit(2)

            if "plot" in sys.argv:
                plot = "y"
            else:
                plot = "n"

        Smartgrid(neighbourhood, algorithm, iterations, plot, cluster_option)


if __name__ == "__main__":
    Main()
