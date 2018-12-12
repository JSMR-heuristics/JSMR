#!/usr/bin/python

import sys
import csv
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import re
import operator
import os
import copy
import random
import pickle
import time


from pathlib import Path
from helpers import *

from battery import Battery
from house import House

# nog aanpassen als we meerdere algoritmes en/of eigen wijken gaan maken
# en voor tussenplots, die maken het algorimte een stuk slomer
# Validates user input and gives instructions if it's wrong

PLOT = False
ALGORITHM = "hill"

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
        self.hill_climber()
        house_count = 0
        for house in self.houses.values():
            if house.link:
                house_count += 1
        print(f"housecount = {house_count}")
        for battery in self.batteries.values():
            print(battery.filled())
    def load_houses(self):
        """
        Parses through csv file and saves houses as house.House
        objects. Returns instances in dict to __init__
        """
        # find specific directory with the data
        subpath = f"data\wijk{INPUT}_huizen.csv"
        path = str(Path.cwd()).replace("test_area", "")
        path = str(path.replace("Test_Scripts", subpath))
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
        subpath = f"data\wijk{INPUT}_batterijen.txt"
        path = str(Path.cwd()).replace("test_area", "")
        path = str(path.replace("Test_Scripts", subpath))

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
        # plt.show()
        # subpath = f"results/Wijk_{INPUT}/{ALGORITHM}/plot{changes}_{ALGORITHM}.png"
        # path = str(Path.cwd()).replace("scripts", subpath)

        subpath = f"/plot{changes}_{ALGORITHM}.png"
        path = str(Path.cwd()) + "\\hill_test\\" + subpath

        plt.savefig(path)


    def hill_climber(self):
        """
        This function changes links between houses and batteries
        so no battery is over it's capacity, this will be done
        with lowest cost possible for this algorithm
        """

        random_houses = list(self.houses.values())
        random_houses_2 = list(self.houses.values())
        iterations = 1000
        count = 0
        misses = -iterations
        prices = []
        climbs_list = []
        lowest_list = []
        time_list1 = []
        time_list2 = []
        # Do untill we have <iterations> succesfull configurations
        while count < iterations:
            self.disconnect()
            # connect random houses to the closest option  within the constraints
            # ----------------------------------------------------------------
            # While one or more batteries are over their capacity or not every
            # house is linked to a battery
            start_time = time.clock()
            print(f"Start: {start_time}")
            while self.check_linked() is False or self.check_full() is True:
                # print(misses)
                misses += 1

                # shuffle order of houses
                random.shuffle(random_houses)
                # remove connections, if any
                self.disconnect()

                # for every house find closest battery to connect to provided
                # that this house wont over-cap the battery
                for house in random_houses:
                    number_list = [0]
                    for i in range(5):
                        if house.output + self.batteries[list(house.diffs)[i]].filled() <= self.batteries[list(house.diffs)[i]].capacity:
                            house.link = self.batteries[list(house.diffs)[i]]
                            self.batteries[list(house.diffs)[i]].linked_houses.append(house)
                            break
            base_copy = copy.copy([self.houses, self.batteries])
            base_cost = self.calculate_cost()
            time1 = time.clock() - start_time
            # ----------------------------------------------------------------
            print("Start Hillclimb")
            start_time = time.clock()
            print(f"Start: {start_time}")
            step_back_cost = base_cost
            step_back = base_copy

            climbs = 0
            hillcount = 0
            alt_directions = 150 * 150

            random.shuffle(random_houses)
            random.shuffle(random_houses_2)

            while hillcount < alt_directions:
                # loop while the new step is inefficient
                for house_1 in random_houses:
                    for house_2 in random_houses_2:
                        # take a step if not the same batteries
                        if not (house_1.link == house_2.link):
                            switch_houses(self, house_1, house_2)
                            step_cost = self.calculate_cost()
                            if (step_cost < step_back_cost) and (self.check_full() is False):
                                climbs += 1
                                # print(climbs)
                                # print(step_cost)
                                # necessary to copy step back?
                                step_back = copy.copy([self.houses, self.batteries])
                                step_back_cost = step_cost
                                hillcount = 0
                            else:
                                switch_houses(self, house_1, house_2)
                                #self.houses, self.batteries = step_back[0], step_back[1]
                        hillcount += 1

            print(f"bc={base_cost}, hilltop = {step_cost}")
            time2 = time.clock() - start_time
            time_var = time.strftime("%d%m%Y")
            prices.append(step_cost)

            if step_cost is min(prices):
                lowest_list.append([step_cost, count+misses])
                house_batt = [self.houses, self.batteries]
                with open(f"hill_climber_batt_lowest_WIJK{INPUT}_{time_var}.dat", "wb") as f:
                    pickle.dump(house_batt, f)
                with open(f"sequence_lowest_WIJK{INPUT}_{time_var}.dat", "wb") as f:
                    pickle.dump(random_houses, f)
            count += 1
            time_list1.append(time1)
            time_list2.append(time2)
            climbs_list.append(climbs)
            print(count)

        # print("results wijk2 cluster 3")
        print(f"min: {min(prices)}")
        print(f"max: {max(prices)}")
        print(f"mean: {np.mean(prices)}")
        print(f"unsuccesfull iterations: {misses}")
        print(f"average # of climbs: {np.mean(climbs_list)}")
        print(f"average time greedy: {np.mean(time_list1)}")
        print(f"average time hillclimber: {np.mean(time_list2)}")
        with open(f"hill_climber_lowest_list_WIJK{INPUT}_{time_var}_{iterations}.dat", "wb") as f:
            pickle.dump(lowest_list, f)


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

    Smartgrid()
