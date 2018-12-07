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
from statistics import mean
"""
DIT IS EEN TEST MET EEN LIBRARY VAN INTERNET. IMPLEMENTATIE MOET NOG
VERANDERT WORDEN
"""
cwd = os.getcwd()
path = os.path.join(*[cwd, 'code', 'classes'])
sys.path.append(path)
from battery import Battery
from house import House


from helpers import *

# nog aanpassen als we meerdere algoritmes en/of eigen wijken gaan maken
# en voor tussenplots, die maken het algorimte een stuk slomer
# Validates user input and gives instructions if it's wrong


class Cluster(object):
    def __init__(self, input):
        self.options_list = []
        self.input = input
        self.houses = self.load_houses()

        self.find_clusters()

    def load_houses(self):
        """
        Parses through csv file and saves houses as house.House
        objects. Returns instances in dict to __init__
        """
        # find specific directory with the data
        cwd = os.getcwd()
        path = os.path.join(*[cwd, 'data', f'wijk{self.input}_huizen.csv'])
        # open file
        with open(path) as houses_csv:

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


    def find_clusters(self):
        # Generate sample data
        big_counter = 1
        X = []
        for house in self.houses.values():
            X.append([int(house.x), int(house.y)])
        X = np.array(X)

        settings_list = []
        for i in range(25):
            for j in range(50):
                settings_list.append([(i + 1), (j + 1)])
        counter = 0

        working_settings = []

        subplot_data = []

        while counter < len(settings_list):
            n_clusters, noise_points, X, labels, mask_samples = self.cluster_scan(X, settings_list, counter)
            counter += 1

            if n_clusters is 5:
                working_settings.append([settings_list[counter][0], settings_list[counter][1]])
                subplot_data.append([X, labels, mask_samples, n_clusters, big_counter])
                big_counter += 1

        self.plot_cluster(subplot_data)

    def cluster_scan(self, X, settings_list, counter):
        a, b = settings_list[counter][0], settings_list[counter][1]
        db = DBSCAN(eps=a, min_samples=b, algorithm="ball_tree", metric="manhattan").fit(X)
        mask_samples = np.zeros_like(db.labels_, dtype=bool)
        mask_samples[db.core_sample_indices_] = True
        labels = db.labels_

        # Number of clusters in labels, ignoring noise if present.
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        noise_points = list(labels).count(-1)

        return n_clusters, noise_points, X, labels, mask_samples
        # Plot result

    def plot_cluster(self, data):
        n_plots = len(data)

        # fig, axs = plt.subplots(1, n_plots, figsize=(18, 6))

        for index in range(n_plots):
            # Black removed and is used for noise instead.
            X = data[index][0]
            labels = data[index][1]
            mask_samples = data[index][2]
            n_clusters = data[index][3]
            big_counter = data[index][4]
            unique_labels = set(labels)
            colors = [plt.cm.Spectral(each)
                      for each in np.linspace(0, 1, len(unique_labels))]
            cap = [1507.0, 1508.25, 1506.75]

            all_coords = "pos\t\tcap\n"
            weights = []
            # battery_index = 0
            for k, col in zip(unique_labels, colors):
                if k == -1:
                    # Black used for noise.
                    col = [0, 0, 0, 1]

                class_member_mask = (labels == k)

                # print(X)
                list_X , list_Y = [], []


                xy_big = X[class_member_mask & mask_samples]
                if xy_big[:,0].any() and xy_big[:,1].any():
                    for i in range(3):
                        list_X.append(mean(xy_big[:,0]))
                        list_Y.append(mean(xy_big[:,1]))

                # axs[index].plot(xy_big[:, 0], xy_big[:, 1], 'o', markerfacecolor=tuple(col),
                #          markeredgecolor='k', markersize=14)

                xy_small = X[class_member_mask & ~mask_samples]
                if xy_small[:,0].any() and xy_small[:,1].any() and col[0] is not 0:
                        list_X.append(mean(xy_small[:,0]))
                        list_Y.append(mean(xy_small[:,1]))

                # axs[index].plot(xy_small[:, 0], xy_small[:, 1], 'o', markerfacecolor=tuple(col),
                #          markeredgecolor='k', markersize=6)
                #
                # axs[index].set_title(index + 1)

                if list_X and list_Y:
                    all_coords += f"[{mean(list_X)}, {mean(list_Y)}]\t\t{cap[int(self.input) - 1]}\n"
                    weights.append(len(xy_big) * 3 + len(xy_small))

            cwd = os.getcwd()
            path = os.path.join(*[cwd, "data", f"wijk{self.input}_cluster_{big_counter}.txt"])
            sys.path.append(path)

            with open (path, "w") as f:
                f.write(all_coords)

            cwd = os.getcwd()
            path = os.path.join(*[cwd, "data", f"wijk{self.input}_cluster_{big_counter}_weigth.txt"])
            sys.path.append(path)

            with open (path, "w") as f:
                f.write(str(weights))

        # fig.suptitle("Choose one of these plots and enter after closing this window", fontsize=16)
        for i in range(big_counter):
            self.options_list.append(i + 1)


if __name__ == "__main__":
    start_time = time.clock()

    cluster = Cluster()
    cluster.find_clusters()
