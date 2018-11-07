from house import House
from battery import Battery
import csv
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import re

INPUT_HOUSES = "wijk1_huizen.csv"
INPUT_BATTERIES = "wijk1_batterijen.txt"

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

    def plot_houses(self, houses):

        x = []
        y = []

        # turn dict to list so we can iterate through
        houses_list = list(houses.values())

        # for every house save coordinates to lists
        for house in houses_list:
            x.append(house.x)
            y.append(house.y)


        # make plot
        ax = plt.gca()
        ax.axis([-2, 52, -2 , 52])
        ax.scatter(x , y, marker = ".")
        ax.scatter(x_batt, y_batt, marker = "+")
        ax.set_xticks(np.arange(0, 52, 1), minor = True)
        ax.set_yticks(np.arange(0, 52, 1), minor = True)
        ax.grid(b = True, which="major", linewidth=1)
        ax.grid(b = True, which="minor", linewidth=.2)




        plt.show()


    # Nu kijken of we batterijen ook kunnen toevoegen,
    # wanneer deze ingeladen zijn

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
                batteries[id] = Battery(cap, x, y)

        # return dict to INIT
        return batteries


    # def place_batteries(self, batteries):
    #     # TODO
    #
    # def calculate_cable():
    #     # TODO
    #
    # def calculate_battery_input():
    #     # TODO
    #
    # def calculate_battery_output():
    #     # TODO
    #     dict = {}
if __name__ == "__main__":
    smart = Smartgrid()
    #smart.plot_houses(smart.houses)
