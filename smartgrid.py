from house import House
from battery import Battery
import csv
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import re
import operator

INPUT_HOUSES = "wijk1_huizen.csv"
INPUT_BATTERIES = "wijk1_batterijen.txt"

COLOUR_LIST = ["m", "g", "c", "y", "b",
               "grey", "maroon", "yellow", "orange",
               "fuchsia", "lime", "peru"]

class Smartgrid(object):
    def __init__(self):
        self.houses = self.load_houses()
        self.batteries = self.load_batteries()
        self.calculate_cable()
        self.link_houses()
        self.optimize()
        self.plot_houses()


    def load_houses(self):

        # open file
        with open(f"Huizen&Batterijen/{INPUT_HOUSES}", newline="") as houses_csv:

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
        with open(f"Huizen&Batterijen/{INPUT_BATTERIES}") as batteries_text:

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
                x = coordinates.split(",", 1)[0]
                y = coordinates.split(",", 1)[1]
                x = re.sub("\D", "", x)
                y = re.sub("\D", "", y)
                # colour = self.colour_list[id]
                colour = COLOUR_LIST[id]
                batteries[id] = Battery(cap, x, y, colour)

        # return dict to INIT
        return batteries

    def plot_houses(self):

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

            x_house = house.x
            y_house = house.y

            batt = house.link
            x_batt, y_batt = batt.x, batt.y

            # calculate the new coordinate for the vertical line
            x_diff = x_batt - x_house
            new_x = x_house + x_diff

            line_colour = batt.colour

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

        # order the batteries for each house
        for house in list(self.houses.values()):
            dist = house.dist
            ord_dist = sorted(dist.items(), key=operator.itemgetter(1))

            # for right now, the link is the shortest
            # regardless of battery capacity
            house.link = self.batteries[ord_dist[0][0]]
            self.batteries[ord_dist[0][0]].linked_houses.append(house)
            diff = ord_dist[0][1]
            ord_dist_diff = ord_dist
            del ord_dist_diff[0]
            diffs = {}
            for index in range(len(ord_dist_diff)):
                diffs[ord_dist_diff[index][0]] = int(ord_dist_diff[index][1]) - diff
            house.diffs = diffs
            house.ord_dist = dict(ord_dist)

    def calculate_cable(self):

        # get coordinates
        x_houses, y_houses, x_batt, y_batt  = self.get_coordinates()

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
        while self.check_full():

            # Sorts batteries based off total inputs from high to low
            total_inputs = []
            for battery in self.batteries.values():
                total_inputs.append([battery.filled(), battery])
            high_low = sorted(total_inputs, key=operator.itemgetter(0), reverse = True)

            # Prioritize battery with highest inputs
            # to disconnect a battery from
            for i in high_low:
                battery = i[1]
                distance_list = []

                # Sort houses linked to this battery by distance
                # to other battery from low to high
                for house in battery.linked_houses:
                    element = []
                    batts = list(house.diffs.keys())
                    distance = list(house.diffs.values())
                    houses = [house] * len(distance)
                    outputs = [house.output] * len(distance)
                    element = list(map(list, zip(batts, distance, houses, outputs)))
                    distance_list += element
                distance_list = sorted(distance_list, key=operator.itemgetter(1))

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
                if self.batteries[option[0]].filled() + option[2].output <= self.batteries[option[0]].capacity:
                    return option[2], self.batteries[option[0]]
        else:
            list = sorted(list, key=operator.itemgetter(3))
            for option in list:
                if (option[2].link.filled() - option[2].output) < option[2].link.capacity:
                    print(option[2].link.filled() - option[2].output)
                    return option[2], self.batteries[option[0]]


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
