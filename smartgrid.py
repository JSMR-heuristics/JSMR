from house import House
from battery import Battery
import csv

INPUT_HOUSES = "wijk1_huizen.csv"

class Smartgrid(object):
    def __init__(self):
        self.houses = self.load_houses()

    def load_houses(self):
        with open(f"Huizen&Batterijen/{INPUT_HOUSES}", newline="") as houses_csv:
            data_houses = csv.reader(houses_csv, delimiter=",")
            next(data_houses, None)
            for row in data_houses:
                id = f"{row[0]}-{row[1]}"
                x = row[0]
                y = row[1]
                output = row[2]
                House.houses[id] = House(x, y, output)

    def plot_houses(self, houses):
        size = Smartgrid.size
        # create grid or let matplot do it
        # possibly convert coordinates to usable data

    # def load_batteries(self, input):
    #     # TODO
    #
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
