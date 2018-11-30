#!/usr/bin/python

import sys
import csv
# import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import re
import operator
import os
import random
import statistics
import pickle
from pathlib import Path
import time
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler
from geopy.distance import great_circle
from shapely.geometry import MultiPoint



path = str(Path.cwd()).replace("test_scripts", "code/classes")
sys.path.append(path)
from battery import Battery
from house import House


from helpers import *

# nog aanpassen als we meerdere algoritmes en/of eigen wijken gaan maken
# en voor tussenplots, die maken het algorimte een stuk slomer
# Validates user input and gives instructions if it's wrong

ITER = 0
ALGORITHM = "GREEDY"

if len(sys.argv) not in [3]:
        print("Usage: python smargrid.py <wijknummer> <plot>\nwijknummer should be 1,2 or 3")
        sys.exit(2)
elif len(sys.argv) is 3:
    if int(sys.argv[1]) not in [1, 2, 3] or isinstance(sys.argv[2], int):
        print("Usage: python smargrid.py <wijknummer>\nwijknummer should be 1,2 or 3")
        print("If you want plots type\n python smargrid.py <wijknummer> plot")
        sys.exit(2)
    else:
        INPUT = sys.argv[1]
        ITER = sys.argv[2]

class Smartgrid(object):
    def __init__(self):
        self.houses = self.load_houses()
        self.batteries = self.load_batteries()
        # self.coordinates = self.get_coordinates()
        # # self.sequences = []
        # self.link_houses()
        # self.optimize()


    def load_houses(self):
        """
        Parses through csv file and saves houses as house.House
        objects. Returns instances in dict to __init__
        """
        # find specific directory with the data
        subpath = f"data\wijk{INPUT}_huizen.csv"
        path = str(Path.cwd()).replace("test_scripts", subpath)
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
        batteries = {}
        capacity = 1507.0
        coordinates = [0, 0]
        x = 0
        y = 0
        colour = "r"
        for i in range(5):
            print(i)
            batteries[i] = Battery(capacity, x, y, colour)
        print(batteries[0])



        # return dict to INIT
        return batteries

    def find_clusters(self):

        # subpath = f"data\wijk{INPUT}_huizen.csv"
        # path = str(Path.cwd()).replace("scripts", subpath)
        #
        # df = pd.read_csv(path)
        # coords = df.as_matrix(columns=['x', 'y'])
        # db = DBSCAN(eps=0.5, min_samples=5, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
        # print(db.labels_)


        print(__doc__)

        import numpy as np

        from sklearn.cluster import DBSCAN
        from sklearn import metrics
        from sklearn.datasets.samples_generator import make_blobs
        from sklearn.preprocessing import StandardScaler


        # #############################################################################
        # Generate sample data
        X = []
        for house in self.houses.values():
            X.append([int(house.x), int(house.y)])
        X = np.array(X)

        settings_list = []
        for i in range(15):
            for j in range(15):
                settings_list.append([(i + 1), (j + 1)])
        counter = 0

        working_settings = []

        while counter < len(settings_list):
            n_clusters_, n_noise_, X, labels, core_samples_mask = self.cluster_scan(X, settings_list, counter)
            counter += 1

            if n_clusters_ is 5:
                working_settings.append([settings_list[counter][0], settings_list[counter][1]])
                self.plot_cluster(X, labels, core_samples_mask, n_clusters_)

            # print('Estimated number of clusters: %d' % n_clusters_)
            # print('Estimated number of noise points: %d' % n_noise_)

        print(working_settings)

    def cluster_scan(self, X, settings_list, counter):
        a, b = settings_list[counter][0], settings_list[counter][1]
        db = DBSCAN(eps=a, min_samples=b, algorithm="auto").fit(X)
        core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
        core_samples_mask[db.core_sample_indices_] = True
        labels = db.labels_

        # Number of clusters in labels, ignoring noise if present.
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        n_noise_ = list(labels).count(-1)

        return n_clusters_, n_noise_, X, labels, core_samples_mask
        # Plot result

    def plot_cluster(self, X, labels, core_samples_mask, n_clusters_):

        # Black removed and is used for noise instead.
        unique_labels = set(labels)
        colors = [plt.cm.Spectral(each)
                  for each in np.linspace(0, 1, len(unique_labels))]
        for k, col in zip(unique_labels, colors):
            if k == -1:
                # Black used for noise.
                col = [0, 0, 0, 1]

            class_member_mask = (labels == k)

            # print(X)

            xy = X[class_member_mask & core_samples_mask]
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
                     markeredgecolor='k', markersize=14)

            xy = X[class_member_mask & ~core_samples_mask]
            plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
                     markeredgecolor='k', markersize=6)

        plt.title('Estimated number of clusters: %d' % n_clusters_)
        plt.show()



          # kan weggewerkt worden
    # def get_coordinates(self):
    #     x_houses, y_houses, x_batt, y_batt = [], [], [], []
    #
    #     # turn dict to list so we can iterate through
    #     houses_list = list(self.houses.values())
    #     batteries_list = list(self.batteries.values())
    #
    #     # for every house save coordinates to lists
    #     for house in houses_list:
    #         x_houses.append(house.x)
    #         y_houses.append(house.y)
    #
    #     # for every battery save coordinates to lists
    #     for battery in batteries_list:
    #         x_batt.append(battery.x)
    #         y_batt.append(battery.y)
    #
    #     return [x_houses, y_houses, x_batt, y_batt]
    #
    # def link_houses(self):
    #     """
    #     DOES NOT LINK HOUSES YET, JUST PROVIDES DISTANCES
    #     """
    #     # order the batteries for each house
    #     all_distances = calculate_distance(self)
    #     for index, house in enumerate(list(self.houses.values())):
    #
    #         batteries = list(all_distances[index].keys())
    #         distances = list(all_distances[index].values())
    #
    #         diff, distance_diffs = distances[0], distances
    #         diffs = {}
    #         for index in range(len(distance_diffs)):
    #             diffs[batteries[index]] = int(distance_diffs[index]) - diff
    #         house.diffs = diffs
    #
    # def optimize(self):
    #     """
    #     This function changes links between houses and batteries
    #     so no battery is over it's capacity, this will be done
    #     with lowest cost possible for this algorithm
    #
    #
    #     SEQUENCES ONTHOUDEN VOOR EXTRA PUNTEN!!!!!!!!!! id's
    #     """
    #     # turn houses into list
    #     random_houses = list(self.houses.values())
    #     print(ITER)
    #
    #     iterations = int(ITER)
    #
    #     prices = []
    #     count = 0
    #     misses = -iterations
    #     sequence_set = set()
    #
    #
    #     # Do untill we have <iterations> succesfull configurations
    #     while count < iterations:
    #         self.disconnect()
    #         # While one or more batteries are over their capacity or not every
    #         # house is linked to a battery
    #         while self.check_linked() is False or self.check_full() is True:
    #             misses += 1
    #
    #             # shuffle order of houses
    #             # random_houses = self.shuffle_houses()
    #             random.shuffle(random_houses)
    #
    #
    #             # remove connections, if any
    #             self.disconnect()
    #
    #             # for every house find closest battery to connect to provided
    #             # that this house wont over-cap the battery
    #             for house in random_houses:
    #                 for i in range(5):
    #                     if house.output + self.batteries[list(house.diffs)[i]].filled() <= self.batteries[list(house.diffs)[i]].capacity:
    #                         house.link = self.batteries[list(house.diffs)[i]]
    #                         self.batteries[list(house.diffs)[i]].linked_houses.append(house)
    #                         break
    #
    #         # calculate price
    #         price = self.calculate_cost()
    #         prices.append(price)
    #
    #         # pickle cheapest configuration so far + sequence of houses
    #         if price is min(prices):
    #             house_batt = [self.houses, self.batteries]
    #             with open("random_greedy_lowest_WIJK{INPUT}.dat", "wb") as f:
    #                 pickle.dump(house_batt, f)
    #             with open("sequence_lowest_WIJK{INPUT}.dat", "wb") as f:
    #                 pickle.dump(random_houses, f)
    #
    #
    #         count += 1
    #         print(count)
    #     print(f"min: {min(prices)}")
    #     print(f"max: {max(prices)}")
    #     print(f"mean: {np.mean(prices)}")
    #     print(f"unsuccesfull iterations: {misses}")
    #
    # # def shuffle_houses(self):
    # #     houses = list(self.houses.values())
    # #     random.shuffle(houses)
    # #     if houses in self.sequences:
    # #         print("MAND................................................................")
    # #         self.shuffle_houses()
    # #     else:
    # #         self.sequences.append(houses)
    # #         return houses
    #
    # def check_linked(self):
    #     """
    #     Checks whether every house is linked to a battery
    #     """
    #     count = 0
    #     for house in self.houses.values():
    #         if house.link:
    #             count += 1
    #     if count is 150:
    #         return True
    #     else:
    #         return False
    #
    # def check_full(self):
    #     """
    #     Returns True if one or more of the batteries is over it's
    #     capacity, False if not.
    #     """
    #     switch = False
    #     for battery in self.batteries.values():
    #         if battery.full() is True:
    #             switch = True
    #     return switch
    #
    # def disconnect(self):
    #     """
    #     Delete all connections
    #     """
    #     for house in self.houses.values():
    #         house.link = None
    #     for battery in self.batteries.values():
    #         battery.linked_houses = []
    #
    # def calculate_cost(self):
    #     cost = 0
    #     for house in list(self.houses.values()):
    #
    #         x_house, y_house = house.x, house.y
    #         x_batt, y_batt = house.link.x, house.link.y
    #
    #         # calculate the new coordinate for the vertical line
    #         x_diff = x_batt - x_house
    #         new_x = x_house + x_diff
    #
    #         line_colour = house.link.colour
    #
    #         # calculate line cost
    #         cost += (abs(x_batt - x_house) + abs(y_batt - y_house)) * 9
    #     return cost

if __name__ == "__main__":
    start_time = time.clock()
    print(f"Start: {start_time}")
    smart = Smartgrid()
    smart.find_clusters()
    # smart = Smartgrid()
    # print(len(smart.sequences))
    print(time.clock() - start_time, "seconds")
