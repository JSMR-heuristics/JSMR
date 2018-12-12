#!/usr/bin/python

import sys
import csv
import matplotlib.pyplot as plt
import numpy as np
import re
import os

from pathlib import Path
from helpers import *
from algorithms import *

cwd = os.getcwd()
path = os.path.join(*[cwd, 'code', 'classes'])
sys.path.append(path)

from battery import Battery
from house import House

class Smartgrid(object):
    def __init__(self, neighbourhood, algorithm, iterations, plot, c_option):
        self.input = neighbourhood
        self.algorithm = algorithm
        self.iterations = iterations
        self.plot_option = plot
        self.c_option = c_option
        self.houses = self.load_houses()
        self.batteries = self.load_batteries()
        self.coordinates = self.get_coordinates()
        self.link_houses()
        self.pickle_file = ""
        self.run_algorithm()
        self.plot_houses(1)
        self.cost = calculate_cost(self)
        if self.plot_option is "y":
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

        # Not clusteroptions will be called more often so is pu in if statement
        if not self.c_option:
            path = os.path.join(*[cwd, 'data',
                                f'wijk{self.input}_batterijen.txt'])
        else:
            path = os.path.join(*[cwd, 'data',
                                f'wijk{self.input}_cluster_{self.c_option}.txt'])

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

        x_houses, y_houses, x_batt, y_batt = (self.coordinates[0],
                                              self.coordinates[1],
                                              self.coordinates[2],
                                              self.coordinates[3])

        # make plot
        ax = plt.gca()
        ax.axis([-2, 52, -2, 52])
        ax.scatter(x_houses, y_houses, marker=".")
        ax.scatter(x_batt, y_batt, marker="o", s=40, c="r")
        ax.set_xticks(np.arange(0, 52, 1), minor=True)
        ax.set_yticks(np.arange(0, 52, 1), minor=True)
        ax.grid(b=True, which="major", linewidth=1)
        ax.grid(b=True, which="minor", linewidth=.2)

        total = 0
        for house in list(self.houses.values()):

            x_house, y_house = house.x, house.y
            x_batt, y_batt = house.link.x, house.link.y

            # calculate the new coordinate for the vertical line
            x_diff = x_batt - x_house
            new_x = x_house + x_diff

            line_colour = house.link.colour

            # place horizontal line
            ax.plot([x_house, x_batt], [y_house, y_house],
                    color=f'{line_colour}', linestyle='-', linewidth=1)

            # place vertical line
            ax.plot([new_x, new_x], [y_house, y_batt],
                    color=f'{line_colour}', linestyle='-', linewidth=1)

            # calculate line cost
            total += (abs(x_batt - x_house) + abs(y_batt - y_house)) * 9

        print(f"Total cost of cable: {total}")
        plt.title(f"Total cost of cable: {total}")
        plt.show()

        cwd = os.getcwd()
        path = os.path.join(*[cwd, 'results',
                            (f'wijk_{self.input}') +
                            (f"/{self.algorithm}") +
                            (f"/plot{changes}_{self.algorithm}.png")])
        sys.path.append(path)


        plt.savefig(path)



    def run_algorithm(self):
        if self.algorithm == "stepdown":
            stepdown(self)
        elif self.algorithm == "greedy":
            self.pickle_file = greedy(self, self.iterations)
        elif self.algorithm == "hill":
            hill_climber(self, self.iterations)
        elif self.algorithm == "backup":
            backup(self)
        elif self.algorithm == "dfs":
            dfs(self)
        elif self.algorithm == "bnb":
            bnb(self)


if __name__ == "__main__":
    Smartgrid()
