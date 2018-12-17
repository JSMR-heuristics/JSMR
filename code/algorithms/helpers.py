import operator
import sys
import os
import pickle
import matplotlib.pyplot as plt
import numpy as np
import time


def calculate_distance(self):
    """Calculate distance between each house and each battery."""
    all_distances = []

    # For each house, find the difference in X and Y coordinates
    # to each battery
    for house in self.houses.values():
        x_house, y_house = house.x, house.y
        house_diff = {}
        counter = 0

        # For each battery
        for battery in self.batteries.values():
            x_batt, y_batt = battery.x, battery.y
            x_diff = abs(x_batt - x_house)
            y_diff = abs(y_batt - y_house)
            house_diff[counter] = (x_diff + y_diff)
            counter += 1

        # Sort by distance
        house_diff = dict(sorted(house_diff.items(), key=operator.itemgetter(1)))
        all_distances.append(house_diff)

        # Save as attribute
        house.dists = house_diff

    # Return the distances
    return all_distances


def sort_linked_houses(self, battery):
    """Sorts list of linked houses of a battery by distances."""
    distance_list = []

    # For each house linked to the given battery, calculate, distances and
    # outputs
    for house in battery.linked_houses:
        batts = list(house.diffs.keys())
        distance = []
        weight = 50 / house.output
        for diff in list(house.diffs.values()):
            weighted_diff = diff * weight
            distance.append(weighted_diff)
        houses = [house] * len(distance)
        outputs = [house.output] * len(distance)
        element = []

        # Save information in list
        element = list(map(list, zip(batts, distance, houses, outputs)))
        distance_list += element

    # Return the list sorted by distance
    return sorted(distance_list, key=operator.itemgetter(1))


def find_best(self, list, status):
    """Find best battery to switch house to."""
    # Find the cheapest switch which will not overcap the next battery.
    if status is "strict":
        for option in list:
            a = self.batteries[option[0]].filled() + option[2].output
            b = self.batteries[option[0]].capacity
            if a <= b:
                return option[2], self.batteries[option[0]]

    # Else, choose to switch house with largest output
    else:
        option = list[0]
        return option[2], self.batteries[option[0]]


def swap_houses(self, house, current_batt, next_batt):
    """Switch house from battery it's currently linked to, to the next one."""
    house.link = next_batt
    next_batt.linked_houses.append(house)
    current_batt.linked_houses.remove(house)


def check_linked(self):
    """Return true if all houses are linked."""
    count = 0
    for house in self.houses.values():
        if house.link:
            count += 1
    if count is 150:
        return True
    else:
        return False


def check_full(self):
    """Return true if a battery is over capacity, false if not."""
    for battery in self.batteries.values():
        if battery.full() is True:
            return True
    return False


def disconnect(self):
    """Delete all connections."""
    for house in self.houses.values():
        house.link = None
    for battery in self.batteries.values():
        battery.linked_houses = []


def calculate_cost(self):
    """Return total cable cost."""
    cost = 0
    for house in list(self.houses.values()):

        x_house, y_house = house.x, house.y
        x_batt, y_batt = house.link.x, house.link.y

        # calculate cable cost
        cost += (abs(x_batt - x_house) + abs(y_batt - y_house)) * 9
    return cost


def switch_houses(self, house1, house2):
    """Switch houses from battery."""
    house2.link, house1.link = house1.link, house2.link


def load_pickle(self, file):
    """Load pickle file containing battery and house objects."""
    # Load pickle from data/pickles/ folder
    cwd = os.getcwd()
    path = os.path.join(*[cwd, 'data', 'pickles', file])
    with open(path, "rb") as f:
        unpickler = pickle.Unpickler(f)
        house_batt = unpickler.load()

    self.houses, self.batteries = house_batt[0], house_batt[1]
    plot_houses(self)


def plot_houses(self):
    """Plot batteries, houses and cables."""
    # Get house and battery coordinates
    x_houses, y_houses, x_batt, y_batt = get_coordinates(self)

    # make plot
    ax = plt.gca()
    ax.axis([-2, 52, -2, 52])

    # Plot houses and batteries
    ax.scatter(x_houses, y_houses, marker=".")
    ax.scatter(x_batt, y_batt, marker="o", s=40, c="r")

    # Get gridlines
    ax.set_xticks(np.arange(0, 52, 1), minor=True)
    ax.set_yticks(np.arange(0, 52, 1), minor=True)
    ax.grid(b=True, which="major", linewidth=1)
    ax.grid(b=True, which="minor", linewidth=.2)

    total = 0

    # For each house, plot cable
    for house in list(self.houses.values()):

        x_house, y_house = house.x, house.y
        x_batt, y_batt = house.link.x, house.link.y

        # calculate the new coordinate for the vertical line
        x_diff = x_batt - x_house
        new_x = x_house + x_diff

        line_colour = house.link.colour

        # place horizontal line
        ax.plot([x_house, x_batt], [y_house, y_house],
                color=f'{line_colour}', linestyle='-', linewidth=1)

        # place vertical line
        ax.plot([new_x, new_x], [y_house, y_batt],
                color=f'{line_colour}', linestyle='-', linewidth=1)

        # calculate line cost
        total += (abs(x_batt - x_house) + abs(y_batt - y_house)) * 9

    # Print costs
    print(f"Total cost of cable: {total}")
    plt.title(f"Total cost of cable: {total}")

    plt.show()


def get_coordinates(self):
    """Load house and battery coordinates to list of lists."""
    x_houses, y_houses, x_batt, y_batt = [], [], [], []

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

    return [x_houses, y_houses, x_batt, y_batt]


def save_dat_file(self):
    """Save battery and house objects using pickle."""
    # Put house and battery dict into list
    house_batt = [self.houses, self.batteries]

    # Get time
    time_var = time.strftime("%d%m%Y")

    # Save in folder correspoding to neighbourhood and algorithm
    cwd = os.getcwd()
    path = os.path.join(*[cwd, 'results', f"wijk_{self.input}", self.algorithm,
                          self.set_up,
                          f"{self.algorithm}_lowest_WIJK{self.input}_{time_var}.dat"])
    sys.path.append(path)

    with open(path, "wb") as f:
        pickle.dump(house_batt, f)

    return path
