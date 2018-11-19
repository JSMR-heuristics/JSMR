from house import House
from battery import Battery
import csv
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import re
import operator

from pathlib import Path

INPUT = 1

link houses
if check.full true geeft:
    calculate costs
    save result
    save links
    save plot
def Depth_test(object):
    def __init__():
        self.houses = self.load_houses()
        self.batteries = self.load_batteries()
        self.links = self.link_houses()
# for i in range 150:
#     for j in range 150:
#         for k in range 150:
#             for l in range 150:
#                 for m in range 150:
#
        i, j, k, l, m = 0, 0, 0, 0, 0
        # totale loop:
        for house in self.houses:
            

        if self.check(self.links):
            write save.results()
            print("Yep")
        else:
            print("Nope")


    def load_houses():
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

    def load_batteries():
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


    def link_houses():
        while self.check_full():
            all_distances = []
            for house in self.houses.values():
                x_house, y_house = house.x, house.y
                house_diff = {}
                counter = 0
                for battery in self.batteries.values():
                    x_batt, y_batt = battery.x, battery.y
                    x_diff = abs(x_batt - x_house)
                    y_diff = abs(y_batt - y_house)
                    house_diff[counter] = (x_diff + y_diff)
                    counter += 1
                house_diff = dict(sorted(house_diff.items(), key=operator.itemgetter(1)))
                all_distances.append(house_diff)
            return all_distances


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
