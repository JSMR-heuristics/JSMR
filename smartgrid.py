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

COLOUR_LIST = ["m", "k", "g", "c", "y", "b",
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

            # calcualte line cost
            x_diff = abs(x_batt - x_house)
            y_diff = abs(y_batt - y_house)
            tot_cost = (x_diff + y_diff) * 9
            # print(tot_cost)

        plt.show()



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

        # Check initial status
        for i in self.batteries:
            print(self.batteries[i].full())
        for i in self.batteries:
            print(self.batteries[i].filled())

        # Initialize variables
        switch = 9999
        go = 9999
        changes = 0

        # Between nope and yep is the range where it'll be hard to find a
        # decent house to add to a battery
        nope = 36
        yep = 8
        nope_list = []

        # Keep looping until all batteries are below max capacity
        while self.batteries[0].full() or self.batteries[1].full() or self.batteries[2].full() or self.batteries[3].full() or self.batteries[4].full():
            # Iterate over every battery
            for i in self.batteries:
                print(f"i = {i}")
                # Keep moving houses until the battery is no longer full
                while self.batteries[i].full():
                    # Iterate every house linked to the battery
                    for house in self.batteries[i].linked_houses:
                        # Check every possible connection the house has
                        for link in house.diffs.items():
                            a = self.batteries[link[0]].capacity
                            b = self.batteries[link[0]].filled()
                            c = house.output
                            # d = leftover capacity minus the house that will be added
                            d = (a - b) - c
                            # If the switch is smaller than the other links
                            # of the house, consider it for switching
                            if link[1] < switch and not (f"{house}, {link}" in nope_list):
                                # If the connection switch is possible, save it,
                                # otherwise add it to a list of houses-connections
                                # that should be ignored. If adding the houses
                                # puts the battery in an impractical range of
                                # capacity, also ignore the switch
                                if a < b + c or ((d < nope) and (d > yep)):
                                    nope_list.append(f"{house}, {link}")
                                else:
                                    switch = link[1]
                                    switch_batt = link[0]
                        # Check the house's best switch option against the best
                        # overal option for the battery so far
                        if switch < go:
                            go = switch
                            go_batt = switch_batt
                            changer = house
                            switch = 9999
                    # The loop has checked every house now, so it changes the
                    # connection for the best house option
                    changer.link = self.batteries[go_batt]
                    self.batteries[go_batt].linked_houses.append(changer)
                    self.batteries[i].linked_houses.remove(changer)
                    go = 9999
                    changes += 1
                    nope_list = []
                    print(f"house{changer} changed from battery{i} to battery{go_batt}")
                    print(f"house capacity = {changer.output}")
                    print(f"capacity = {self.batteries[i].filled()}")
                    print(f"Current changes = {changes}")
            # Check results
            for i in self.batteries:
                print(self.batteries[i].full())
            for i in self.batteries:
                print(self.batteries[i].filled())


if __name__ == "__main__":
    Smartgrid()
