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

        # return dict to INIT
        return batteries

    def find_clusters(self):
        # Generate sample data
        X = []
        for house in self.houses.values():
            X.append([int(house.x), int(house.y)])
        X = np.array(X)

        settings_list = []
        for i in range(25):
            for j in range(50):
                settings_list.append([(i + 1), (j + 1)])
        counter = 0

        print("mand")
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
        db = DBSCAN(eps=a, min_samples=b, algorithm="ball_tree", metric="manhattan").fit(X)
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

if __name__ == "__main__":
    start_time = time.clock()
    print(f"Start: {start_time}")
    smart = Smartgrid()
    smart.find_clusters()
    # smart = Smartgrid()
    # print(len(smart.sequences))
    print(time.clock() - start_time, "seconds")
