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

from pathlib import Path

# nog aanpassen als we meerdere algoritmes en/of eigen wijken gaan maken
# Validates user input and gives instructions if it's wrong
if len(sys.argv) is not 2:
    print("Usage: python smargrid.py <wijknummer>")
    sys.exit(2)
elif int(sys.argv[1]) not in [1, 2, 3]:
    print("Usage: python smargrid.py <wijknummer>\nwijknummer should be 1,2 or 3")
    sys.exit(2)

INPUT = sys.argv[1]


class Smartgrid(object):
    def __init__(self):
        self.houses = self.load_houses()
        self.batteries = self.load_batteries()
        self.link_houses()
        self.optimize()
        self.plot_houses()


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

    def plot_houses(self):
        """
        Plots houses, batteries and cables. Also calculates the total
        cost of the cable
        """

        x_houses, y_houses, x_batt, y_batt  = self.get_coordinates()

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
            x_diff = abs(x_batt - x_house)
            y_diff = abs(y_batt - y_house)
            tot_cost = (x_diff + y_diff) * 9
            total += tot_cost
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
        plt.savefig('plot.png')


    def link_houses(self):
        """
        Links houses to batteries regardless of capacity, choses the
        closest option

        LINK_HOUSES CALCULATE_CABLE EN GET_COORDINATES MOGEN LATER DENK
        IK WEL IN 1 METHOD GESCHREVEN
        """
        # order the batteries for each house
        all_distances = self.calculate_distance()
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

    def calculate_distance(self):
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

        return x_houses, y_houses, x_batt, y_batt

    def optimize(self):
        """
        This function changes links between houses and batteries
        so no battery is over it's capacity, this will be done
        with lowest cost possible for this algorithm
        """
        # Initialize changes counter, this gives insight to
        # the speed of this algorithm
        changes = 0

        # While one or more batteries are over their capacity
        while self.check_full() and changes < 250:

            # kan korter
            # Sorts batteries based off total inputs from high to low
            total_inputs = []
            for battery in self.batteries.values():
                total_inputs.append([battery.filled(), battery])
            high_low = sorted(total_inputs, key=operator.itemgetter(0), reverse = True)

            # Prioritize battery with highest inputs
            # to disconnect a house from
            for i in high_low:
                battery = i[1]

                # Sort houses linked to this battery by distance
                # to other battery from low to high
                distance_list = self.sort_linked_houses(battery)

                # Determine the cheapest option first, if any
                # else transfer option with lowest output
                try:
                    house, to_batt = self.find_best(distance_list, "strict")
                except TypeError:
                    house, to_batt = self.find_best(distance_list, "not-strict")

                # Switch the house from battery
                curr_batt = house.link
                changes += 1
                self.swap_houses(house, curr_batt, to_batt, changes)
                break
        for i in self.batteries:
            print(self.batteries[i].filled())
            print(f"{self.batteries[i].x}/{self.batteries[i].y}")
            # for house in self.batteries[i].linked_houses:
            #     print(house.output)

    def sort_linked_houses(self, battery):
        """
        Sorts list of linked houses of a battery by distances
        """
        distance_list = []
        for house in battery.linked_houses:
            batts = list(house.diffs.keys())
            distance = []
            weight = 50 / house.output
            for diff in list(house.diffs.values()):
                weighted_diff = diff * weight
                distance.append(weighted_diff)
            # distance = list(house.diffs.values())
            # print(weight)
            # print(distance)
            houses = [house] * len(distance)
            outputs = [house.output] * len(distance)
            element = []
            element = list(map(list, zip(batts, distance, houses, outputs)))
            distance_list += element
        return sorted(distance_list, key=operator.itemgetter(1))


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

    def find_best(self, list, status):
        """
        Tries to find either the cheapest house to possibly switch from battery
        or the one with the lowest possible output
        """
        if status is "strict":
            for option in list:
                a = self.batteries[option[0]].filled() + option[2].output
                b = self.batteries[option[0]].capacity
                c = b - a
                if a <= b and not 7 < c < 35:
                    return option[2], self.batteries[option[0]]
        # wordt vervangen door output gewicht
        else:
            list = sorted(list, key=operator.itemgetter(3))
            for option in list:
                if (option[2].link.filled() - option[2].output) < option[2].link.capacity:
                    print(option[2].link.filled() - option[2].output)
                    return option[2], self.batteries[option[0]]

# conditie toevoegen om te zorgen dat huizen niet op een batterij komen die verder dan een max afstand ligt
# conditie toevoegen om te zorgen dat een huis niet wordt verplaatst als dat de batterij nét niet onder full brengt

    def swap_houses(self, house, current_batt, next_batt, changes):
        """
        Switches house from battery it's currently linked to, to the next
        one
        """
        house.link = next_batt
        next_batt.linked_houses.append(house)
        current_batt.linked_houses.remove(house)
        print(f"house at x{house.x}/y{house.y} changed from battery at x{current_batt.x}/y{current_batt.y} to battery at x{next_batt.x}/y{next_batt.y}")
        print(f"house capacity = {house.output}")
        print(f"capacity = {current_batt.filled()}")
        print(f"changes = {changes}")


if __name__ == "__main__":
    Smartgrid()
