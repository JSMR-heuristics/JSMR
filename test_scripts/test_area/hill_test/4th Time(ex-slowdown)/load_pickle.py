#!/usr/bin/python

import sys, os
cwd = os.getcwd()
cwd = os.path.dirname(cwd)
cwd = os.path.dirname(cwd)
path = os.path.join(*[cwd, 'code', 'classes'])
print(path)
sys.path.append(path)
from house import House
from battery import Battery
import csv
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import re
import operator
import os
import random
import statistics
import pickle

from pathlib import Path

from helpers import *
"""
SLAAT HUIZEN NOG NIET MET JUISTE NAAM ENZO OP
"""

class Smartgrid(object):
    def __init__(self):
        self.houses = {}
        self.batteries = {}
        self.load()
        self.plot_houses()
        house_count = 0
        for house in self.houses.values():
            if house.link:
                house_count += 1
        print(f"housecount = {house_count}")
        batt_count = 0
        for battery in self.batteries.values():
            print(battery.filled())
            batt_count += len(battery.linked_houses)
        print(batt_count)




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

    def plot_houses(self):
        """
        Plots houses, batteries and cables. Also calculates the total
        cost of the cable
        """

        x_houses, y_houses, x_batt, y_batt  = self.get_coordinates()

        # # make plot
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
            # print(list(house.diffs.keys())[0])
            # house.link = self.batteries[list(house.diffs.keys())[0]]
            # # house.link = self.batteries[list(house.diffs.keys())[len(self.batteries.values()) - 1]]
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
        asd = 0
        for battery in self.batteries.values():
            asd += battery.cost
        print(asd)
        plt.show()
        return total


    def load(self):
        """
        This function changes links between houses and batteries
        so no battery is over it's capacity, this will be done
        with lowest cost possible for this algorithm
        """
<<<<<<< HEAD
        with open("hill_climber_lowest_list_WIJK1_06122018_1000.dat", "rb") as f:
=======
<<<<<<< HEAD:test_scripts/test_area/load_pickle.py
        with open("weighted_clusters_WIJK2.dat", "rb") as f:
=======
        with open("hill_climber_batt_lowest_WIJK3_06122018.dat", "rb") as f:
>>>>>>> 346c75e746c5d506605dbbd56a8e0bc6d2d4722f:test_scripts/test_area/hill_test/4th Time(ex-slowdown)/load_pickle.py
>>>>>>> cbc79e24fd035ce6abb25476951a40682bf18ba0
            unpickler = pickle.Unpickler(f)
            house_batt = unpickler.load()

        self.houses, self.batteries = house_batt[0], house_batt[1]

if __name__ == "__main__":
    Smartgrid()
