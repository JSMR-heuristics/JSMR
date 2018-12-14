import sys
import os
import time

# Load classes and helpers after path is specified
cwd = os.getcwd()
path = os.path.join(*[cwd, 'code', 'algorithms'])
sys.path.append(path)

from smartgrid import Smartgrid
from cluster import Cluster
from configure import Configure
from weights import Weights
from helpers import *


class Main(object):
    """Calls all other scripts.

    This script checks commandline arguments and loads the correct algorithms
    needed for the specified command.
    """

    def __init__(self):
        """Here, all commandline arguments are checked and used."""
        # Check if enough commandline args are given
        if len(sys.argv) is 1:
            print("python main.py <1, 2, 3> <algorithm> <iterations>")
            sys.exit()

        else:
            # Check if neighbourhood input is correct
            if sys.argv[1] in ["1", "2", "3"]:
                self.input = int(sys.argv[1])
                neighbourhood = self.input
            else:
                print("please insert either a valid neighbourhood number "
                      "as 1st argument")
                print("select from: 1, 2, 3")
                sys.exit(2)

            # If user wants plots
            if "plot" in sys.argv:
                plot = "y"
            else:
                plot = "n"

            # Check if correct algorithm is given in third argument
            if sys.argv[2] in ["stepdown", "greedy", "hill", "dfs", "random",
                               "bnb"]:
                algorithm = sys.argv[2]
                cluster_option = None

                if sys.argv[2] in ["stepdown", "dfs", "bnb"]:
                    iterations = 0

                # Initialize n iterations, if any
                elif len(sys.argv) > 3 and sys.argv[3].isnumeric():
                    iterations = int(sys.argv[3])

                else:
                    print("No #iteration given, will be set to 1000")
                    iterations = 1000

                # Call cluster algorithm
                if ("cluster" in sys.argv) and not("configure" in sys.argv):
                    cluster = Cluster(neighbourhood)
                    min_cost = 999999
                    index = 0

                    # Find cheapest positions for battery
                    for i in cluster.options_list:
                        print(f"Checking option {i}...")
                        smart = Smartgrid(neighbourhood, "stepdown", 0, "n", i,
                                          "cluster")
                        if smart.cost < min_cost:
                            file = smart.pickle_file
                            min_cost = smart.cost
                            index = i


                    # Call specified algorithm for cheapest option
                    Smartgrid(neighbourhood, algorithm, iterations, "n", index,
                              "cluster")
                    time_var = time.strftime("%d%m%Y")
                    file = os.path.join(*[cwd, 'results', f"wijk_{self.input}",
                                          algorithm, "cluster",
                                          f"{algorithm}_lowest_WIJK{self.input}"
                                          + f"_{time_var}.dat"])
                    # Load pickle so cheapest option can be plotted
                    load_pickle(self, file)
                    sys.exit()

                # If not cluster, use configure and find cheapest configuration
                # for this neighbourhood
                elif ("configure" in sys.argv) and not ("cluster" in sys.argv):

                    Configure(neighbourhood)

                    # Should user want to test with anything else than
                    # greedy-1000 iterations specifically, do this
                    if algorithm != "greedy" and int(iterations) != 1000:
                        Weights(neighbourhood, "test", iterations, "configure")
                        Weights(neighbourhood, algorithm, iterations,
                                "configure")
                    else:
                        Weights(neighbourhood, algorithm, iterations,
                                "configure")
                    sys.exit()
            # Else, algorithm argument was incorrect
            else:
                print("please insert the preferred algorithm as 2nd argument")
                print("select from: \"stepdown\", \"greedy\", \"hill\", "
                      "\"cluster\", \"configure\", \"random\"")
                sys.exit(2)

        # No cluster or configure, so use fixed battery locations
        Smartgrid(neighbourhood, algorithm, iterations, plot, cluster_option,
                  "fixed")


if __name__ == "__main__":
    Main()
