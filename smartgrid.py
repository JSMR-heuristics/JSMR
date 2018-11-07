from house import House
from battery import Battery
import csv
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

INPUT_HOUSES = "wijk1_huizen.csv"

class Smartgrid(object):
    def __init__(self):
        self.houses = self.load_houses()

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

        # hier gaat het fout bij mij, de asses veranderen naar de input
        ax = plt.gca()
        ax.axis([-2, 52, -2 , 52])
        ax.scatter(x , y, marker = ".")
        ax.set_xticks(np.arange(0, 52, 1), minor = True)
        ax.set_yticks(np.arange(0, 52, 1), minor = True)
        ax.grid(b = True, which="major", linewidth=1)
        ax.grid(b = True, which="minor", linewidth=.2)

        plt.show()


    # Nu kijken of we batterijen ook kunnen toevoegen,
    # wanneer deze ingeladen zijn

    def load_batteries(self, input):
        with open(f"Huizen&Batterijen/{INPUT_BATTERIES}", newline="") as batteries_text:
            data_batteries =
            
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
    smart.plot_houses(smart.houses)
