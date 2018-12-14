import sys
import os
import time


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
                                  "configure/random): "))

            if algorithm == "greedy" or algorithm == "hill":
                iterations = input("Iterations: ")
            plot = input("Do you want intermediate plots to be made? (y/n): ")

        else:
            # neighbourhood
            if sys.argv[1] in ["1", "2", "3"]:
                self.input = int(sys.argv[1])
                neighbourhood = self.input
            else:
                print("please insert either a valid neighbourhood number or "
                      "\"spec\" as 1st argument")
                print("select from: 1, 2, 3, \"spec\"")
                sys.exit(2)

            # iteration here due to configure needing iterations


            if sys.argv[2] in ["stepdown", "greedy", "hill", "dfs", "random", "bnb"]:
                algorithm = sys.argv[2]
                cluster_option = None
                battery_file = None

                if sys.argv[2] in ["stepdown", "dfs", "bnb"]:
                    iterations = 0

                elif len(sys.argv) > 3 and sys.argv[3].isnumeric():
                    iterations = int(sys.argv[3])

                else:
                    print("No #iteration given, will be set to 1000")
                    iterations = 1000


                if ("cluster" in sys.argv) and not("configure" in sys.argv):
                    cluster = Cluster(neighbourhood)
                    costs = []
                    min_cost = 999999
                    index = 0
                    for i in cluster.options_list:
                        print(f"Checking option {i}...")
                        smart = Smartgrid(neighbourhood, "greedy", 1000, "n", i, "cluster")
                        if smart.cost < min_cost:
                            file = smart.pickle_file
                            min_cost = smart.cost
                            index = i

                    print(file)
                    Smartgrid(neighbourhood, algorithm, iterations, "n", index, "cluster")
                    time_var = time.strftime("%d%m%Y")
                    file = os.path.join(*[cwd, 'results', f"wijk_{self.input}", algorithm, "cluster",
                                          f"{algorithm}_lowest_WIJK{self.input}_{time_var}.dat"])
                    load_pickle(self, file)
                    sys.exit()

                elif ("configure" in sys.argv) and not ("cluster" in sys.argv):
                    Configure(neighbourhood)
                    if algorithm == "greedy" and int(iterations) == 1000:
                        Weights(neighbourhood, algorithm, iterations)
                    else:
                        Weights(neighbourhood, "test", iterations)
                        Weights(neighbourhood, algorithm, iterations)
                    sys.exit()

            else:
                print("please insert the preferred algorithm as 2nd argument")
                print("select from: \"stepdown\", \"greedy\", \"hill\", "
                      "\"cluster\", \"configure\", \"spec\", \"random\"")
                sys.exit(2)

            if "plot" in sys.argv:
                plot = "y"
            else:
                plot = "n"

        Smartgrid(neighbourhood, algorithm, iterations, plot, cluster_option, "fixed")


if __name__ == "__main__":
    Main()
