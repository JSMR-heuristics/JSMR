# SmartGrid

## Problem:
When enough houses can generate their own energy, it becomes possible that
excess energy will be generated. It's economically beneficial to be able to
store that excess energy into batteries for later use, however it is
economically beneficial as well to place and select batteries as strategically
as possible to minimize battery and cable costs. What exactly is the most
economic set-up can result into an astronomically large range of battery and
cable layouts. Thus this program is made to return the most beneficial layout
according to our set of priorities.

## Progress:
Currently we have implemented a greedy algorithm which runs until the constraints are satisfied. The constraint here being maximal capacity of the batteries. We wouldn't want them to explode!

### This is what our neighbourhood would look like when all houses are simply linked to the nearest battery:
![alt text](https://github.com/JSMR-heuristics/JSMR/blob/master/figures/Wijk_1/No_algorithm_SG1_lower.png)

### And this is what the neighbourhood looks like when our greedy algorithm has been implemented:
![alt text](https://github.com/JSMR-heuristics/JSMR/blob/master/figures/Wijk_1/plotFINAL_GREEDY.png)

## Repository layout:
* Our datafiles are stored in the "Huizen&batterijen" folder.
* Processing takes place in the "scripts" folder.
* Output files are stored in the "figures" folder.
* Our testing area is contained in "test_scripts".

## Running the code:
* For the code to run, certain libraries need to be installed. Check these libraries in the Requirements.txt
* To run our main code, "smartgrid.py"
  * go to the location of the JSMR/scripts folder on your PC
  * open the command window here
  * run "python smartgrid.py 'Number' 'plot'"
  * for number use 1, 2 or 3, this indicates which neighbourhood you want to use
  * for plot either type "plot" if you want intermediate plots to be saved or leave it empty if you don't want intermediate plots.
    * example:
        """
        python smartgrid.py 1 plot
        """
