#!/usr/bin/python

import sys
import csv
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import re
import operator
import os

from pathlib import Path
from helpers import *
from algorithms import *

cwd = os.getcwd()
path = os.path.join(*[cwd, 'code', 'classes'])
sys.path.append(path)

from battery import Battery
from house import House


# nog aanpassen als we meerdere algoritmes en/of eigen wijken gaan maken
# en voor tussenplots, die maken het algorimte een stuk slomer
# Validates user input and gives instructions if it's wrong

# PLOT = False
# ALGORITHM = "optimize"
#
# if len(sys.argv) not in [2, 3]:
#         print("Usage: python smargrid.py <wijknummer> <plot>\nwijknummer should be 1,2 or 3")
#         sys.exit(2)
# elif len(sys.argv) is 2:
#     if int(sys.argv[1]) not in [1, 2, 3]:
#         print("Usage: python smargrid.py <wijknummer>\nwijknummer should be 1,2 or 3")
#         sys.exit(2)
#     else:
#         INPUT = sys.argv[1]
# elif len(sys.argv) is 3:
#     if int(sys.argv[1]) not in [1, 2, 3] or sys.argv[2] != "plot":
#         print("Usage: python smargrid.py <wijknummer>\nwijknummer should be 1,2 or 3")
#         print("If you want plots type\n python smargrid.py <wijknummer> plot")
#         sys.exit(2)
#     else:
#         INPUT = sys.argv[1]
#         PLOT = True

class Smartgrid(object):
    def __init__(self, neighbourhood, algorithm, iterations, plot, cluster_option, battery_file):
        self.input = neighbourhood
        self.algorithm = algorithm
        self.iterations = iterations
        self.plot_option = plot
        self.cluster_option = cluster_option
        self.houses = self.load_houses()
        self.batteries = self.load_batteries()
        self.coordinates = self.get_coordinates()
        self.link_houses()
        self.run_algorithm()
        self.plot_houses(50)


    def load_houses(self):
        """
        Parses through csv file and saves houses as house.House
        objects. Returns instances in dict to __init__
        """
        # find specific directory with the data
        cwd = os.getcwd()
        path = os.path.join(*[cwd, 'data', f'wijk{self.input}_huizen.csv'])
        # open file
        with open(path) as houses_csv:

            # read data from csv
            data_houses = csv.reader(houses_csv, delimiter=",")

            # skip headers
            next(data_houses, None)
            houses = {}

            # for every house, save coordinates and output in dictionary
            # name for instance in dict is Xcoord-Ycoord
            for row in data_houses:
                x = row[0]
                y = row[1]
                id = f"{x}-{y}"

                output = row[2]
                houses[id] = House(x, y, output)

        # returns dict, goes to init (self.houses)
        return houses

    def load_batteries(self):
        """
        Parses through text file and saves batteries as battery.Battery
        objects. Returns instances in dict to __init__
        """
        # find specific directory with the data
        cwd = os.getcwd()

        if not self.cluster_option:
            path = os.path.join(*[cwd, 'data', f'wijk{self.input}_batterijen.txt'])
        else:
            path = os.path.join(*[cwd, 'data', f'wijk{self.input}_cluster_{self.cluster_option}.txt'])

        with open(path) as batteries_text:

            # read text file per line
            data_batteries = batteries_text.readlines()

            # delete headers
            data_batteries.pop(0)

            batteries = {}

            # Library color list toevoegen
            COLOUR_LIST = ["m", "g", "c", "y", "b",
                           "grey", "maroon", "yellow", "orange",
                           "fuchsia", "lime", "peru"]

            # for every batterie isolate coordinates and capacity
            for id, battery in enumerate(data_batteries):
                coordinates = battery.split("\t", 1)[0]
                cap = battery.split("\t", 1)[1].strip()
                x = re.sub("\D", "", coordinates.split(",", 1)[0])
                y = re.sub("\D", "", coordinates.split(",", 1)[1])
                colour = COLOUR_LIST[id]
                batteries[id] = Battery(cap, x, y, colour)

        # return dict to INIT
        return batteries

    # kan weggewerkt worden
    def get_coordinates(self):
        x_houses, y_houses, x_batt, y_batt = [], [], [], []

        # turn dict to list so we can iterate through
        houses_list = list(self.houses.values())
        batteries_list = list(self.batteries.values())

        # for every house save coordinates to lists
        for house in houses_list:
            x_houses.append(house.x)
            y_houses.append(house.y)

        # for every battery save coordinates to lists
        for battery in batteries_list:
            x_batt.append(battery.x)
            y_batt.append(battery.y)

        return [x_houses, y_houses, x_batt, y_batt]

    def link_houses(self):
        """
        Links houses to batteries regardless of capacity, choses the
        closest option

        LINK_HOUSES CALCULATE_CABLE EN GET_COORDINATES MOGEN LATER DENK
        IK WEL IN 1 METHOD GESCHREVEN
        """
        # order the batteries for each house
        all_distances = calculate_distance(self)
        for index, house in enumerate(list(self.houses.values())):
            # for right now, the link is the shortest
            # regardless of battery capacity
            batteries = list(all_distances[index].keys())
            distances = list(all_distances[index].values())

            house.link = self.batteries[batteries[0]]
            self.batteries[batteries[0]].linked_houses.append(house)
            diff, distance_diffs = distances[0], distances
            diffs = {}
            for index in range(len(distance_diffs)):
                diffs[batteries[index]] = int(distance_diffs[index]) - diff
            house.diffs = diffs

    def plot_houses(self, changes):
        """
        Plots houses, batteries and cables. Also calculates the total
        cost of the cable
        """

        x_houses, y_houses, x_batt, y_batt  = self.coordinates[0], self.coordinates[1], self.coordinates[2], self.coordinates[3]

        # make plot
        ax = plt.gca()
        ax.axis([-2, 52, -2 , 52])
        ax.scatter(x_houses , y_houses, marker = ".")
        ax.scatter(x_batt, y_batt, marker = "o", s = 40, c = "r" )
        ax.set_xticks(np.arange(0, 52, 1), minor = True)
        ax.set_yticks(np.arange(0, 52, 1), minor = True)
        ax.grid(b = True, which="major", linewidth=1)
        ax.grid(b = True, which="minor", linewidth=.2)

        total = 0
        for house in list(self.houses.values()):

            x_house, y_house = house.x, house.y
            x_batt, y_batt = house.link.x, house.link.y

            # calculate the new coordinate for the vertical line
            x_diff = x_batt - x_house
            new_x = x_house + x_diff

            line_colour = house.link.colour

            # place horizontal line
            ax.plot([x_house, x_batt], [y_house, y_house], \
            color=f'{line_colour}',linestyle='-', linewidth=1)

            # place vertical line
            ax.plot([new_x, new_x], [y_house, y_batt], \
            color=f'{line_colour}',linestyle='-', linewidth=1)

            # calculate line cost
            total += (abs(x_batt - x_house) + abs(y_batt - y_house)) * 9

        print(f"Total cost of cable: {total}")
        plt.title(f"Total cost of cable: {total}")

        ## adds the id to the batteries on the plot
        ## alter in the sub3,4 to type of battery
        # count = 0
        # for battery in list(self.batteries.values()):
        #     x = battery.x
        #     y = battery.y
        #     plt.text(x, y, f"{count}")
        #     count += 1
        plt.show()
        # subpath = f"results/Wijk_{INPUT}/{ALGORITHM}/plot{changes}_{ALGORITHM}.png"
        # path = str(Path.cwd()).replace("scripts", subpath)

        cwd = os.getcwd()
        path = os.path.join(*[cwd, 'results', f'wijk_{self.input}/{self.algorithm}/plot{changes}_{self.algorithm}.png'])
        sys.path.append(path)


        plt.savefig(path)



    def run_algorithm(self):
        if self.algorithm == "stepdown":
            stepdown(self)
        elif self.algorithm == "greedy":
            greedy(self, self.iterations)
        elif self.algorithm == "hill":
            hill_climber(self, self.iterations)
        elif self.algorithm == "backup":
            backup(self)
        elif self.algorithm == "dfs":
            dfs()


if __name__ == "__main__":
    Smartgrid()
