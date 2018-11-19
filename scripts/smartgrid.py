#!/usr/bin/python

import sys
from house import House
from battery import Battery
import csv
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import re
import operator
import os

from pathlib import Path

from helpers import *


# nog aanpassen als we meerdere algoritmes en/of eigen wijken gaan maken
# en voor tussenplots, die maken het algorimte een stuk slomer
# Validates user input and gives instructions if it's wrong

PLOT = False
ALGORITHM = "GREEDY"

if len(sys.argv) not in [2, 3]:
        print("Usage: python smargrid.py <wijknummer> <plot>\nwijknummer should be 1,2 or 3")
        sys.exit(2)
elif len(sys.argv) is 2:
    if int(sys.argv[1]) not in [1, 2, 3]:
        print("Usage: python smargrid.py <wijknummer>\nwijknummer should be 1,2 or 3")
        sys.exit(2)
    else:
        INPUT = sys.argv[1]
elif len(sys.argv) is 3:
    if int(sys.argv[1]) not in [1, 2, 3] or sys.argv[2] != "plot":
        print("Usage: python smargrid.py <wijknummer>\nwijknummer should be 1,2 or 3")
        print("If you want plots type\n python smargrid.py <wijknummer> plot")
        sys.exit(2)
    else:
        INPUT = sys.argv[1]
        PLOT = True

class Smartgrid(object):
    def __init__(self):
        self.houses = self.load_houses()
        self.batteries = self.load_batteries()
        self.coordinates = self.get_coordinates()
        self.link_houses()
        self.optimize()


    def load_houses(self):
        """
        Parses through csv file and saves houses as house.House
        objects. Returns instances in dict to __init__
        """
        # find specific directory with the data
        subpath = f"Huizen&Batterijen\wijk{INPUT}_huizen.csv"
        path = str(Path.cwd()).replace("scripts", subpath)
        # open file
        with open(path, newline="") as houses_csv:

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
        subpath = f"Huizen&Batterijen\wijk{INPUT}_batterijen.txt"
        path = str(Path.cwd()).replace("scripts", subpath)

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
            diff, distance_diffs = distances[0], distances[1:]
            diffs = {}
            for index in range(len(distance_diffs)):
                diffs[batteries[index + 1]] = int(distance_diffs[index]) - diff
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
        # plt.show()
        subpath = f"figures/Wijk_{INPUT}/plot{changes}_{ALGORITHM}.png"
        path = str(Path.cwd()).replace("scripts", subpath)
        plt.savefig(path)


    def optimize(self):
        """
        This function changes links between houses and batteries
        so no battery is over it's capacity, this will be done
        with lowest cost possible for this algorithm
        """
        # Initialize changes counter, this gives insight to
        # the speed of this algorithm
        changes = 0
        # for num in self.batteries:
        #     print(f"Battery{num}: {self.batteries[num].filled()}")
        #     for ding in self.batteries[num].linked_houses:
        #         print(f"House: {ding.output}")

        # While one or more batteries are over their capacity
        while self.check_full() and changes < 50:

            # kan korter
            # Sorts batteries based off total inputs from high to low
            total_inputs = []
            for battery in self.batteries.values():
                total_inputs.append([battery.filled(), battery])
            high_low = sorted(total_inputs, key=operator.itemgetter(0), reverse = True)

            # Prioritize battery with highest inputs
            # to disconnect a house from
            # for i in high_low:
            battery = high_low[0][1]

            # Sort houses linked to this battery by distance
            # to other battery from low to high
            # distance_list = self.sort_linked_houses(battery)
            distance_list = sort_linked_houses(self, battery)

            # Determine the cheapest option first, if any
            # else transfer option with lowest output
            try:
                house, to_batt = find_best(self, distance_list, "strict")
            except TypeError:
                house, to_batt = find_best(self, distance_list, "not-strict")

            # Switch the house from battery
            curr_batt = house.link
            changes += 1
            swap_houses(self, house, curr_batt, to_batt, changes)
            if (changes % 5) is 0 and PLOT:
                self.plot_houses(changes)
            # break
        self.plot_houses("FINAL")
        for i in self.batteries:
            print(self.batteries[i].filled())
            print(f"{self.batteries[i].x}/{self.batteries[i].y}")
            # for house in self.batteries[i].linked_houses:
            #     print(house.output)

    def check_full(self):
        """
        Returns True if one or more of the batteries is over it's
        capacity, False if not.
        """
        switch = False
        for battery in self.batteries.values():
            if battery.full() is True:
                switch = True
        return switch

if __name__ == "__main__":
    Smartgrid()
