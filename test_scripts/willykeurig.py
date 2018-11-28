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
import random
import statistics
import pickle
import time

from pathlib import Path

from helpers import *

# nog aanpassen als we meerdere algoritmes en/of eigen wijken gaan maken
# en voor tussenplots, die maken het algorimte een stuk slomer
# Validates user input and gives instructions if it's wrong

ITER = 0
ALGORITHM = "GREEDY"

if len(sys.argv) not in [3]:
        print("Usage: python smargrid.py <wijknummer> <plot>\nwijknummer should be 1,2 or 3")
        sys.exit(2)
elif len(sys.argv) is 3:
    if int(sys.argv[1]) not in [1, 2, 3] or isinstance(sys.argv[2], int):
        print("Usage: python smargrid.py <wijknummer>\nwijknummer should be 1,2 or 3")
        print("If you want plots type\n python smargrid.py <wijknummer> plot")
        sys.exit(2)
    else:
        INPUT = sys.argv[1]
        ITER = sys.argv[2]

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
        DOES NOT LINK HOUSES YET, JUST PROVIDES DISTANCES
        """
        # order the batteries for each house
        all_distances = calculate_distance(self)
        for index, house in enumerate(list(self.houses.values())):

            batteries = list(all_distances[index].keys())
            distances = list(all_distances[index].values())

            diff, distance_diffs = distances[0], distances
            diffs = {}
            for index in range(len(distance_diffs)):
                diffs[batteries[index]] = int(distance_diffs[index]) - diff
            house.diffs = diffs

    def optimize(self):
        """
        This function changes links between houses and batteries
        so no battery is over it's capacity, this will be done
        with lowest cost possible for this algorithm
        """
        # turn houses into list
        random_houses = list(self.houses.values())
        print(ITER)

        iterations = int(ITER)

        prices = []
        count = 0
        misses = -iterations
        batt_index = [0, 1, 2, 3, 4]

        # Do untill we have <iterations> succesfull configurations
        while count < iterations:
            self.disconnect()
            # While one or more batteries are over their capacity or not every
            # house is linked to a battery
            while self.check_linked() is False or self.check_full() is True:
                misses += 1
                print(misses)

                # shuffle order of houses
                random.shuffle(random_houses)

                # remove connections, if any
                self.disconnect()

                # for every house find closest battery to connect to provided
                # that this house wont over-cap the battery
                for house in random_houses:
                    index = random.sample(batt_index, 1)[0]
                    house.link = self.batteries[index]
                    self.batteries[index].linked_houses.append(house)


            # calculate price
            price = self.calculate_cost()
            prices.append(price)

            # pickle cheapest configuration so far + sequence of houses
            if price is min(prices):
                house_batt = [self.houses, self.batteries]
                with open(f"random_greedy_lowest_WIJK{INPUT}_{ITER}.dat", "wb") as f:
                    pickle.dump(house_batt, f)
                with open(f"sequence_lowest_WIJK{INPUT}_{ITER}.dat", "wb") as f:
                    pickle.dump(random_houses, f)


            count += 1
            print(count)
        with open(f"prices{INPUT}_{ITER}.dat", "wb") as f:
            pickle.dump(prices, f)


        print(f"min: {min(prices)}")
        print(f"max: {max(prices)}")
        print(f"mean: {np.mean(prices)}")
        print(f"unsuccesfull iterations: {misses}")

    def check_linked(self):
        """
        Checks whether every house is linked to a battery
        """
        count = 0
        for house in self.houses.values():
            if house.link:
                count += 1
        if count is 150:
            return True
        else:
            return False

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

    def disconnect(self):
        """
        Delete all connections
        """
        for house in self.houses.values():
            house.link = None
        for battery in self.batteries.values():
            battery.linked_houses = []

    def calculate_cost(self):
        cost = 0
        for house in list(self.houses.values()):

            x_house, y_house = house.x, house.y
            x_batt, y_batt = house.link.x, house.link.y

            # calculate the new coordinate for the vertical line
            x_diff = x_batt - x_house
            new_x = x_house + x_diff

            line_colour = house.link.colour

            # calculate line cost
            cost += (abs(x_batt - x_house) + abs(y_batt - y_house)) * 9
        return cost

if __name__ == "__main__":
    start_time = time.clock()
    print(f"Start: {start_time}")
    Smartgrid()
    print(time.clock() - start_time, "seconds")
