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

    def plot_houses(self):

        x_houses, y_houses, x_batt, y_batt  = smart.get_coordinates()

        # make plot
        ax = plt.gca()
        ax.axis([-2, 52, -2 , 52])
        ax.scatter(x_houses , y_houses, marker = ".")
        ax.scatter(x_batt, y_batt, marker = "o", s = 40, c = "r" )
        ax.set_xticks(np.arange(0, 52, 1), minor = True)
        ax.set_yticks(np.arange(0, 52, 1), minor = True)
        ax.grid(b = True, which="major", linewidth=1)
        ax.grid(b = True, which="minor", linewidth=.2)


        for house in list(smart.houses.values()):

            x_house = house.x
            y_house = house.y

            id_batt = house.link[0]
            x_batt, y_batt = smart.batteries[id_batt].x, smart.batteries[id_batt].y

            # calculate the new coordinate for the vertical line
            x_diff = x_batt - x_house
            new_x = x_house + x_diff

            line_colour = smart.batteries[id_batt].colour
            # place horizontal line
            ax.plot([x_house, x_batt], [y_house, y_house], color=f'\
            {line_colour}',linestyle='-', linewidth=1)
            # plac evertical line
            ax.plot([new_x, new_x], [y_house, y_batt], color=f'\
            {line_colour}',linestyle='-', linewidth=1)

            # calcualte line cost
            x_diff = abs(x_batt - x_house)
            y_diff = abs(y_batt - y_house)
            tot_cost = (x_diff + y_diff) * 9
            # print(tot_cost)

        plt.show()

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
                # colour = smart.colour_list[id]
                colour = COLOUR_LIST[id]
                batteries[id] = Battery(cap, x, y, colour)

        # return dict to INIT
        return batteries

    def link_houses(self):

        # order the batteries for each house
        for house in list(smart.houses.values()):
            dist = house.dist
            ord_dist = sorted(dist.items(), key=operator.itemgetter(1))

            # for right now, the link is the shortest
            # regardless of battery capacity
            house.link = ord_dist[0]
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
        x_houses, y_houses, x_batt, y_batt  = smart.get_coordinates()

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
        keys_list = list(smart.houses.keys())
        for i, key in enumerate(keys_list):
                smart.houses[key].dist = all_diff[i]


    def get_coordinates(self):
        x_houses = []
        y_houses = []

        x_batt = []
        y_batt = []

        # turn dict to list so we can iterate through
        houses_list = list(smart.houses.values())
        batteries_list = list(smart.batteries.values())

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
        for i in self.batteries:
            print(self.batteries[i].full())
        for i in self.batteries:
            print(self.batteries[i].filled())

        # Initialize variables
        switch = 9999
        switch_batt = 0
        go = 9999
        go_batt = 0
        changer = 0
        changes = 0
        a = 0
        b = 0
        c = 0

        # Iterate every battery
        while self.batteries[0].full() or self.batteries[1].full() or self.batteries[2].full() or self.batteries[3].full() or self.batteries[4].full():
            for i in self.batteries:
                print(f"i = {i}")
                if self.batteries[i].full():
                    # print(f"full = {self.batteries[i].full()}")
                    # Iterate every house linked to the battery
                    for house in self.batteries[i].linked_houses:
                        # print(f"house = {house}")
                        # Check every possible connection the house has
                        for link in house.diffs.items():
                            # print(f"link = {link}")
                            # print(f"switch = {switch}")
                            # print(f"output =  {float(house.output)}")
                            # print(f"filled = {self.batteries[i].filled()}")
                            # print(f"capacity = {float(self.batteries[i].capacity)}")
                            # print(f"link0 = {link[0]}")
                            # print(f"link1 = {link[1]}")
                            # If the connection switch is possible, save it
                            a = self.batteries[link[0]].capacity
                            b = self.batteries[link[0]].filled()
                            c = house.output
                            if link[1] < switch:
                                 # (a - b) > c and
                                 # and ((a - (b + c)) > 24) or ((a - (b + c)) < 6)
                                # print(f"switch2 = {switch}")
                                # print(f"output2 =  {float(house.output)}")
                                # print(f"filled2 = {self.batteries[i].filled()}")
                                # print(f"capacity2 = {float(self.batteries[i].capacity)}")
                                # print(f"link02 = {link[0]}")
                                # print(f"link12 = {link[1]}")
                                switch = link[1]
                                switch_batt = link[0]
                        # Check the house's best switch option against the best
                        # overal option for the battery
                        if switch < go:
                            go = switch
                            go_batt = switch_batt
                            changer = house
                            switch = 9999
                            # print(go)
                            # print(changer)
                            # print(go_batt)
                    # Change the connection for the best house
                    # print(f"go = {go}")
                    # print(f"changer = {changer}")
                    # print(f"go_batt = {go_batt}")
                    changer.link = self.batteries[go_batt]
                    self.batteries[go_batt].linked_houses.append(changer)
                    self.batteries[i].linked_houses.remove(changer)
                    go = 9999
                    changes += 1
                    print(f"house capacity = {changer.output}")
                    print(f"Added to battery{go_batt}")
                    print(f"capacity = {self.batteries[i].filled()}")
                    print(f"Current changes = {changes}")
            for i in self.batteries:
                print(self.batteries[i].full())
            for i in self.batteries:
                print(self.batteries[i].filled())


if __name__ == "__main__":
    smart = Smartgrid()
    smart.calculate_cable()

    smart.link_houses()
    # smart.plot_houses()
    smart.optimize()
