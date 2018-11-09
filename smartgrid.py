from house import House
from battery import Battery
import csv
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import re
import operator
# Dit moet later worden gesoftcodedet
INPUT_HOUSES = "wijk3_huizen.csv"
INPUT_BATTERIES = "wijk3_batterijen.txt"
COLOUR_LIST = ["m", "k", "g", "c", "y", "r", "b", "grey", "maroon", "yellow", "orange", "fuchsia", "lime", "peru"]

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
        ax.scatter(x_batt, y_batt, marker = "o")
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
            ax.plot([x_house, x_batt], [y_house, y_house], color=f'{line_colour}',linestyle='-', linewidth=2)
            # plac evertical line
            ax.plot([new_x, new_x], [y_house, y_batt], color=f'{line_colour}',linestyle='-', linewidth=2)

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
            diff = ord_dist[0][1]
            ord_dist_diff = ord_dist
            del ord_dist_diff[0]
            diffs = {}
            for index in range(len(ord_dist_diff)):
                diffs[ord_dist_diff[index][0]] = int(ord_dist_diff[index][1]) - diff
            house.diffs = diffs
            house.ord_dist = dict(ord_dist)
        print(smart.houses["10-27"].diffs)

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

    # def calculate_battery_input():
    #     # TODO
    #
    # def calculate_battery_output():
    #     # TODO
    #     dict = {}
if __name__ == "__main__":
    smart = Smartgrid()
    smart.calculate_cable()

    smart.link_houses()
    smart.plot_houses()
