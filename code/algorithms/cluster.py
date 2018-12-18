import csv
import numpy as np
import os
import sys

from sklearn.cluster import DBSCAN
from statistics import mean

cwd = os.getcwd()
path = os.path.join(*[cwd, 'code', 'classes'])
sys.path.append(path)

from house import House

class Cluster(object):
    """Cluster class, finds clusters and writes coordinates to txt file.

    Finds 5 clusters of houses by trying different settings. Writes calculated
    centers of these classes as coordinates in a text file.
    """

    def __init__(self, input):
        """Take neighbourhoodnumber as input."""
        self.options_list = []
        self.input = input
        self.houses = self.load_houses()
        self.find_clusters()


    def load_houses(self):
        """Load houses from csv to dict objects.

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
        """Find 5 clusters in given neighbourhood.

        Try all possible settings which might result in 5 clusters. If
        exactly 5 clusters are found, save coordinates.
        """
        big_counter = 1
        X = []

        # Get all house coordinates
        for house in self.houses.values():
            X.append([int(house.x), int(house.y)])
        X = np.array(X)

        # Make eps and minPTS setting-combinations
        settings_list = []
        for i in range(25):
            for j in range(50):
                settings_list.append([(i + 1), (j + 1)])
        counter = 0

        working_settings = []

        subplot_data = []

        # Run DBSCAN with every setting
        while counter < len(settings_list):
            temp_list = self.cluster_scan(X, settings_list, counter)
            n_clusters, noise_points, X, labels, mask_samples = (temp_list[0],
                                                                 temp_list[1],
                                                                 temp_list[2],
                                                                 temp_list[3],
                                                                 temp_list[4])
            counter += 1

            # Save coordinates when 5 clusters are found
            if n_clusters is 5:
                working_settings.append([settings_list[counter][0],
                                         settings_list[counter][1]])
                subplot_data.append([X, labels, mask_samples, n_clusters,
                                    big_counter])

                big_counter += 1

        self.save_coordinates(subplot_data)


    def cluster_scan(self, X, settings_list, counter):
        """Calculate clusters and return result to find_cluster."""
        # Credit:
        # https://scikit-learn.org/stable/auto_examples/cluster/plot_dbscan.html
        a, b = settings_list[counter][0], settings_list[counter][1]

        # Run DBSCAN with variable eps and minPTS settings
        db = DBSCAN(eps=a, min_samples=b, algorithm="ball_tree",
                    metric="manhattan").fit(X)
        mask_samples = np.zeros_like(db.labels_, dtype=bool)
        mask_samples[db.core_sample_indices_] = True
        labels = db.labels_

        # Calculate number of clusters by substacting noise from cluster labels
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        noise_points = list(labels).count(-1)

        return [n_clusters, noise_points, X, labels, mask_samples]


    def save_coordinates(self, data):
        """Save coordinates of cluster-centers."""
        length_data = len(data)

        # For every solution with 5 clusters
        for index in range(length_data):
            X = data[index][0]
            labels = data[index][1]
            mask_samples = data[index][2]
            n_clusters = data[index][3]
            big_counter = data[index][4]
            unique_labels = set(labels)

            # Capacities corresponding to neighbourhood
            cap = [1507.0, 1508.25, 1506.75]

            # Headers of txt file
            all_coords = "pos\t\tcap\n"

            # Switch for recognizing noise points
            switch = True

            # For each point in this configuration
            for i in unique_labels:

                # Exclude noise points
                if i == -1:
                    switch = False

                # Determine class of point (eg cluster or part of cluster)
                class_member_mask = (labels == i)

                list_X, list_Y = [], []

                # Append all coordinates of cluster points in triple weight
                # to coordinates-lists
                xy_big = X[class_member_mask & mask_samples]
                if xy_big[:, 0].any() and xy_big[:, 1].any():
                    for i in range(3):
                        list_X.append(mean(xy_big[:, 0]))
                        list_Y.append(mean(xy_big[:, 1]))

                # Append all "part-of cluster" points to coordintes-lists
                xy_small = X[class_member_mask & ~mask_samples]
                if xy_small[:, 0].any() and xy_small[:, 1].any() and switch:
                        list_X.append(mean(xy_small[:, 0]))
                        list_Y.append(mean(xy_small[:, 1]))

                # Write mean coordinates per cluster to text file
                if list_X and list_Y:
                    all_coords += f"[{mean(list_X)}, {mean(list_Y)}]\t\t"
                    all_coords += f"{cap[int(self.input) - 1]}\n"

            # Save text files
            cwd = os.getcwd()
            path = os.path.join(*[cwd, "data", f"wijk{self.input}_cluster_"
                                  + f"{big_counter}.txt"])
            sys.path.append(path)

            with open(path, "w") as f:
                f.write(all_coords)

        for i in range(big_counter):
            self.options_list.append(i + 1)


if __name__ == "__main__":
    cluster = Cluster()
    cluster.find_clusters()
