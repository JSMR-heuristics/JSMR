import csv
import matplotlib.pyplot as plt
import numpy as np
import re
import operator
from operator import itemgetter
import os
import sys
import ast
import random
import pickle
from algorithms import *

cwd = os.getcwd()
path = os.path.join(*[cwd, "code", "classes"])
sys.path.append(path)
from house import House
from battery2 import Battery


COLOUR_LIST = ["m", "g", "c", "y", "b",
               "grey", "maroon", "yellow", "orange",
               "fuchsia", "lime", "peru"]


class Weights(object):
    def __init__(self, neighbourhood, algorithm, iterations,set_up):
        self.input = neighbourhood
        self.algorithm = algorithm
        self.set_up = set_up
        self.iterations = int(iterations)
        self.configs = self.get_configs()
        self.houses = self.load_houses()
        self.big_iterations = -1
        self.small_iterations = 0
        self.caps = []
        self.batteries = {}
        self.lowest = 99999
        self.index = 0
        self.run_algorithm()


    def run_algorithm(self):
        print(f"Checking all possible configurations with {self.algorithm}...")

        if self.algorithm == "test"  or (self.algorithm == "greedy" and self.iterations == 1000):
            while True:
                try:
                    self.index += 1
                    self.batteries = self.load_batteries(self.index)
                    print("run")
                except FileNotFoundError:
                    break
                self.calculate_cable()
                self.link_houses()
                greedy(self, 1000)
                if self.algorithm == "greedy":
                    self.load()
                    self.plot_houses()

        else:
            self.load()
            if self.algorithm == "stepdown":
                stepdown(self, "configure")
            elif self.algorithm == "greedy":
                greedy(self, self.iterations, "configure")
                # self.greedy(1000)
            elif self.algorithm == "hill":
                hill_climber(self, self.iterations, "configure")
            elif self.algorithm == "dfs":
                dfs(self, "configure")
            elif self.algorithm == "random":
                random_algorithm(self, self.iterations, "configure")
            elif self.algorithm == "bnb":
                bnb(self, "configure")

            self.load()
            self.plot_houses()

    def get_configs(self):

        batts = [450, 900, 1800]

        config_list = []

        indices_list = []
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    indices_list.append([i, j, k])

        for index in indices_list:
            total_cap = 7500
            mini_list = []
            while total_cap > 0:
                for i in index:
                    if total_cap <= 0:
                        break
                    total_cap -= batts[i]
                    mini_list.append(batts[i])
            config_list.append(mini_list)

        sorted_list = []
        for i in config_list:
            sorted_list.append(sorted(i))

        return [list(item) for item in set(tuple(row) for row in sorted_list)]

    def load_houses(self):

        # open file
        INPUT_HOUSES = f"wijk{self.input}_huizen.csv"
        cwd = os.getcwd()
        path = os.path.join(*[cwd, "data", f"{INPUT_HOUSES}"])
        sys.path.append(path)

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

    def load_batteries(self, index):
        INPUT_BATTERIES = f"wijk{self.input}_cluster2_{index}.txt"
        INPUT_WEIGHTS = f"wijk{self.input}_cluster2_{index}_weigth.txt"

        cwd = os.getcwd()
        path = os.path.join(*[cwd, "data", f"{INPUT_WEIGHTS}"])
        sys.path.append(path)
        with open(path) as weights_text:
            data_weight = str(weights_text.readlines())
            data_weight = ast.literal_eval(data_weight[2:-2])

        cwd = os.getcwd()
        path = os.path.join(*[cwd, "data", f"{INPUT_BATTERIES}"])
        sys.path.append(path)
        with open(path) as batteries_text:

            # read text file per line
            data_batteries = batteries_text.readlines()

            # delete headers
            data_batteries.pop(0)

            batteries = {}

            # for every batterie isolate coordinates and capacity
            for id, battery in enumerate(data_batteries):
                coordinates = battery.split("\t", 1)[0]
                cap = battery.split("\t", 1)[1]
                cap = cap.strip()
                weight = data_weight[id]
                x = coordinates.split(",", 1)[0]
                y = coordinates.split(",", 1)[1]
                x = re.sub("\D", "", x)
                y = re.sub("\D", "", y)
                # colour = self.colour_list[id]
                colour = COLOUR_LIST[((int(id) % 11))]
                batteries[id] = Battery(cap, x, y, colour, weight)

            for i, config in enumerate(self.configs):
                if i <= self.small_iterations:
                    continue
                if len(config) is len(batteries.values()):
                    self.small_iterations = i
                    self.big_iterations += 1
                    self.caps.append(config)
                    self.batteries = batteries
                    self.set_attributes()
                    self.calculate_cable()
                    self.link_houses()
                    greedy(self, 1000)
            self.big_iterations = -1
            self.small_iterations = 0
            self.caps = []

        return batteries

    def set_attributes(self):
        """ Sets cost and capacity for the batteries. """
        for i, battery in enumerate(sorted(self.batteries.values(),
                                    key=operator.attrgetter("weight"))):
            setattr(battery, "cap", self.caps[self.big_iterations][i])
            if self.caps[self.big_iterations][i] is 450:
                cost = 900
            elif self.caps[self.big_iterations][i] is 900:
                cost = 1350
            else:
                cost = 1800
            setattr(battery, "cost", cost)
            battery.capacity = self.caps[self.big_iterations][i]

    def plot_houses(self):

        x_houses, y_houses, x_batt, y_batt = self.get_coordinates()

        # make plot
        ax = plt.gca()
        ax.axis([-2, 52, -2, 52])
        ax.scatter(x_houses, y_houses, marker=".")
        tot_cap = 0
        for battery in self.batteries.values():
            tot_cap += int(battery.cap)
            if int(battery.cap) == 450:
                ax.scatter(battery.x, battery.y, marker="o", s=25, c="r")
            elif int(battery.cap) == 900:
                ax.scatter(battery.x, battery.y, marker="o", s=50, c="r")
            elif int(battery.cap) == 1800:
                ax.scatter(battery.x, battery.y, marker="o", s=100, c="r")
        ax.set_xticks(np.arange(0, 52, 1), minor=True)
        ax.set_yticks(np.arange(0, 52, 1), minor=True)
        ax.grid(b=True, which="major", linewidth=1)
        ax.grid(b=True, which="minor", linewidth=.2)
        print(f"Total capacity of batteries: {tot_cap}")
        total = 0
        for house in list(self.houses.values()):

            x_house = house.x
            y_house = house.y

            batt = house.link
            x_batt, y_batt = batt.x, batt.y

            # calculate the new coordinate for the vertical line
            x_diff = x_batt - x_house
            new_x = x_house + x_diff

            line_colour = batt.colour

            # place horizontal line
            ax.plot([x_house, x_batt], [y_house, y_house],
                    color=f'{line_colour}', linestyle='-', linewidth=1)

            # place vertical line
            ax.plot([new_x, new_x], [y_house, y_batt],
                    color=f'{line_colour}', linestyle='-', linewidth=1)

            # calculate line cost
            x_diff = abs(x_batt - x_house)
            y_diff = abs(y_batt - y_house)
            tot_cost = (x_diff + y_diff) * 9
            total += tot_cost
        batt_cost = 0
        for battery in self.batteries.values():
            batt_cost += battery.cost
        print(f"Cost of cable: {total}")
        print(f"Cost of batts: {batt_cost}")
        print(f"Total: {total + batt_cost}")

        # LEGENDA TOEVOEGEN

        plt.title(f"Cable-cost: {total}, Battery-cost: {batt_cost}, Total: {total + batt_cost}")
        plt.suptitle(f"Best configuration found for neighbourhood {self.input}", fontsize=15)

        color_list = ["r", "r", "r", "r"]
        text_list = ["price/cap:", "450/900", "900/1350", "1800/1800"]
        size_list = [0, 5, 7.5, 10]

        patches = [plt.plot([], [], marker="o", ms=size_list[i], ls="",
                            color=color_list[i],
                            label="{:s}".format(text_list[i]))[0]
                   for i in range(len(text_list))]

        plt.legend(handles=patches, bbox_to_anchor=(.5, -.15),
                   loc="lower center", ncol=4, facecolor="white")
        plt.show()
        plt.savefig('plot.png')

    def link_houses(self):
        """NOG SAMENVOEGEN MET CALC CABLE"""
        # order the batteries for each house
        for house in list(self.houses.values()):
            dist = house.dist
            ord_dist = sorted(dist.items(), key=itemgetter(1))

            # for right now, the link is the shortest
            # regardless of battery capacity
            self.batteries[ord_dist[0][0]].linked_houses.append(house)
            diffs = {}
            for index in range(len(ord_dist)):
                diffs[ord_dist[index][0]] = int(ord_dist[index][1])
            house.diffs = diffs
            house.ord_dist = dict(ord_dist)

    def calculate_cable(self):
        """ Calculates length of cable between each house and battery. """
        x_houses, y_houses, x_batt, y_batt = self.get_coordinates()

        all_diff = []
        for x_house, y_house in list(zip(x_houses, y_houses)):
            house_diff = {}
            counter = 0
            for x, y in list(zip(x_batt, y_batt)):
                x_diff = abs(x - x_house)
                y_diff = abs(y - y_house)
                house_diff[counter] = (x_diff + y_diff)
                counter += 1
            all_diff.append(house_diff)

        # set as attributes
        keys_list = list(self.houses.keys())
        for i, key in enumerate(keys_list):
            self.houses[key].dist = all_diff[i]


    def get_coordinates(self):
        """ Returns coordinates of houses and batteries"""
        x_houses = []
        y_houses = []

        x_batt = []
        y_batt = []

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

        return x_houses, y_houses, x_batt, y_batt

    def greedy(self, iterations):
        """
        This function changes links between houses and batteries
        so no battery is over it's capacity, this will be done
        with lowest cost possible for this algorithm
        """
        # turn houses into list
        random_houses = list(self.houses.values())

        iterations = int(iterations)

        prices = []
        count = 0
        misses = -iterations

        # Do untill we have <iterations> succesfull configurations
        while count < iterations:
            self.disconnect()
            # While one or more batteries are over their capacity or not every
            # house is linked to a battery
            while self.check_linked() is False or self.check_full() is True:
                misses += 1

                # shuffle order of houses
                random.shuffle(random_houses)

                # remove connections, if any
                self.disconnect()

                # for every house find closest battery to connect to provided
                # that this house wont over-cap the battery
                for house in random_houses:
                    for i in range(len(self.batteries.values())):
                        output = house.output
                        curr = self.batteries[list(house.diffs)[i]].filled()
                        cap = self.batteries[list(house.diffs)[i]].capacity
                        if output + curr <= cap:
                            batt = self.batteries[list(house.diffs)[i]]
                            house.link = batt
                            batt.linked_houses.append(house)
                            break

            # calculate price
            for battery in self.batteries.values():
                if not battery.linked_houses:
                    del battery
            price = self.calculate_cost()
            prices.append(price)

            count += 1

        if min(prices) < self.lowest:
            self.lowest = min(prices)
            with open(f"weighted_clusters_WIJK{self.input}.dat",
                      "wb") as f:
                pickle.dump([self.houses, self.batteries], f)

        # self.plot_houses()
        return min(prices)

    def check_linked(self):
        """ Checks whether every house is linked to a battery. """

        count = 0
        for house in self.houses.values():
            if house.link:
                count += 1
        if count is 150:
            return True
        else:
            return False

    def disconnect(self):
        """ Delete all connections. """

        for house in self.houses.values():
            house.link = None
        for battery in self.batteries.values():
            battery.linked_houses = []

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

    def calculate_cost(self):
        cost = 0
        for house in list(self.houses.values()):

            x_house, y_house = house.x, house.y
            x_batt, y_batt = house.link.x, house.link.y

            # calculate line cost
            cost += (abs(x_batt - x_house) + abs(y_batt - y_house)) * 9

        for battery in self.batteries.values():
            cost += battery.cost
        return cost

    def load(self):
        """
        Loads best solution found.
        This function changes links between houses and batteries
        so no battery is over it's capacity, this will be done
        with lowest cost possible for this algorithm
        """
        with open(f"weighted_clusters_WIJK{self.input}.dat", "rb") as f:
            unpickler = pickle.Unpickler(f)
            house_batt = unpickler.load()

        self.houses, self.batteries = house_batt[0], house_batt[1]


if __name__ == "__main__":
    Weights()
