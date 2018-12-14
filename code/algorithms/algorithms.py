import operator
import random
import pickle
import time
import copy
import numpy as np

from helpers import *


def stepdown(self):
    """Self named stepdown algorithm.

    This function starts with every house linked to the closest battery and
    changes links between houses and batteries so no battery is over it's
    capacity, this will be done with lowest cost possible for this algorithm
    """
    # Initialize changes counter, this gives insight to
    # the speed of this algorithm
    changes = 0

    # link every house to closet battery
    for house in self.houses.values():
        house.link = self.batteries[list(house.diffs.keys())[0]]

    # While one or more batteries are over their capacity
    # Stops when 500 changes are made.
    while check_full(self) and changes < 500:

        # Sorts batteries based off total inputs from high to low
        total_inputs = []
        for battery in self.batteries.values():
            total_inputs.append([battery.filled(), battery])
        high_low = sorted(total_inputs, key=operator.itemgetter(0),
                          reverse=True)

        # Prioritize battery with highest inputs to disconnect a house from
        for i in range(len(high_low)):
            battery = high_low[i][1]

            # Sort houses linked to this battery by distance
            # to other battery from low to high
            # distance_list = self.sort_linked_houses(battery)
            distance_list = sort_linked_houses(self, battery)

            # Determine the cheapest option first, if any
            # else transfer option with lowest output
            try:
                house, to_batt = find_best(self, distance_list, "strict")
            except TypeError:
                    house, to_batt = find_best(self, distance_list,
                                               "not-strict")

            # Switch the house from battery
            curr_batt = house.link
            changes += 1
            swap_houses(self, house, curr_batt, to_batt)

    # Return cost to be used for possible comparison between configurations
    return calculate_cost(self)

    # Prints total input of every battery, to check whether all constraints are
    # met
    for i in self.batteries:
        print(self.batteries[i].filled())
        print(f"{self.batteries[i].x}/{self.batteries[i].y}")


def greedy(self, iterations):
    """Greedy algorithm, non deterministic,, saves best solution in pickle.

    This function links every house in a random sequence to the closest
    possible battery without putting the battery over it's capacity, for a
    specifiec number of iterations.
    """
    # Turns houses objects into list
    random_houses = list(self.houses.values())

    # Get number of iterations
    iterations = int(iterations)

    prices = []
    count = 0
    misses = -iterations

    # Do until we have <iterations> succesfull configurations
    while count < iterations:

        # Disconnect links from possible previous configurations
        disconnect(self)

        # While one or more batteries are over their capacity or not every
        # house is linked to a battery
        while check_linked(self) is False or check_full(self) is True:
            misses += 1

            # If algorithm finds too many misses, stop it
            if misses > (7 * iterations):
                return None


            # shuffle order of houses
            random.shuffle(random_houses)

            # remove connections, if any
            disconnect(self)

            # for every house find closest battery to connect to provided
            # that this house wont over-cap the battery
            for house in random_houses:
                for i in range(len(self.batteries.values())):
                    batt = self.batteries[list(house.diffs)[i]]

                    # Check if operation is within constraints
                    if house.output + batt.filled() <= batt.capacity:
                        house.link = batt
                        batt.linked_houses.append(house)
                        break

        count += 1

        # calculate price and add to the list
        price = calculate_cost(self)
        prices.append(price)

        # pickle cheapest configuration so far + sequence of houses
        if price is min(prices):
            file = save_dat_file(self)

    # print results
    print(f"min: {min(prices)}")
    print(f"max: {max(prices)}")
    print(f"mean: {np.mean(prices)}")
    print(f"unsuccesfull iterations: {misses}")

    # return filename of lowest file
    return file


def hill_climber(self, iterations):
    """Hill climber, non deterministic, saves best solution in pickle.

    This function changes links between houses and batteries
    so no battery is over it's capacity, this will be done
    with lowest cost possible for this algorithm.
    For each iteration the sequence houses will be randomized.
    """
    # Randomize house sequences
    random_houses = list(self.houses.values())
    random_houses_2 = list(self.houses.values())

    # Initializing
    iterations = int(iterations)
    count = 0
    misses = -iterations
    prices = []

    # Randomize battery indexation
    batt_index = range(len(self.batteries))

    # Do until we have <iterations> succesfull configurations
    while count < iterations:

        # Disconnect possible connections from previous iteration
        disconnect(self)

        # While one or more batteries are over their capacity or not every
        # house is linked to a battery
        while check_linked(self) is False or check_full(self) is True:
            misses += 1

            # shuffle order of houses
            random.shuffle(random_houses)

            # remove connections, if any
            disconnect(self)

            # for every house find closest battery to connect to provided
            # that this house wont over-cap the battery
            # for house in random_houses:
            for house in random_houses:
                index = random.sample(batt_index, 1)[0]
                house.link = self.batteries[index]
                self.batteries[index].linked_houses.append(house)

        # Save starting configuration and cost
        base_copy = copy.copy([self.houses, self.batteries])
        base_cost = calculate_cost(self)
        step_back_cost = base_cost
        step_back = base_copy

        print("Start Hillclimb")

        # Initializing
        climbs = 0
        hillcount = 0
        alt_directions = 150 * 150

        # Randomize house sequences
        random.shuffle(random_houses)
        random.shuffle(random_houses_2)

        # Shorten time by checking calbe diff instead of whole gridcost
        while hillcount < alt_directions:

            # loop while the new step is inefficient
            for house_1 in random_houses:
                for house_2 in random_houses_2:

                    # Take a step if not the same batteries
                    if not (house_1.link == house_2.link):
                        switch_houses(self, house_1, house_2)
                        step_cost = calculate_cost(self)
                        if (step_cost < step_back_cost) and (check_full(self) is
                                                             False):
                            climbs += 1
                            step_back = copy.copy([self.houses, self.batteries])
                            step_back_cost = step_cost
                            hillcount = 0
                        else:
                            switch_houses(self, house_1, house_2)
                    hillcount += 1

        print(f"bc={base_cost}, hilltop = {step_cost}")
        time_var = time.strftime("%d%m%Y")
        prices.append(step_cost)

        # Save setup if this is the cheapest found
        if step_cost is min(prices):
            save_dat_file(self)

        count += 1
        print(count)

    with open(f"prices_list_WIJK{self.input}_hill.dat", "wb") as f:
        pickle.dump(prices, f)

    print(f"min: {min(prices)}")
    print(f"max: {max(prices)}")
    print(f"mean: {np.mean(prices)}")
    print(f"unsuccesfull iterations: {misses}")


def dfs(self):
    """Depth First parent.

    This method calls the actual depth first search and saves the best
    result found.
    """
    # Find best configuration using greedy algorithm
    self.best = greedy(self, 500)
    self.extra = []

    # Put house objects in list
    for i in self.houses:
        self.extra.append(self.houses[i])

    # Call actual depth first search
    dfs_search(self, 0)

    # Print and save results
    for i in range(self.solutions):
        print(f"The costs for solution{i}: {self.cost_list[i]}")
    with open(f"dfs_result_for_WIJK{self.input}.dat", "wb") as f:
        pickle.dump(self.results_list, f)


def dfs_search(self, num):
    """Depth first search algorithm.

    This algorithm finds all possible solutions by recursively searching for
    all possible setups for each battery. Also saves the best solution found
    yet and all prices found.
    """
    # Finds all possible links for each battery
    for battery in self.batteries:

        # Swap links if a new connection possibility is found
        if self.extra[num].link == self.batteries[battery]:
            pass
        else:
            swap_houses(self, self.extra[num], self.extra[num].link,
                        self.batteries[battery])

        # Keep running until every house is checked
        if num < 149:
            dfs_search(self, num + 1)

        # Saves results if constraints are met and the current option is
        # better than anything found yet
        elif not check_full(self):
            self.solutions += 1
            print(f"Amount of solutions found: {self.solutions}")
            new = calculate_cost(self)
            self.cost_list.append(new)
            if new < self.best:
                self.best = new
                self.links_copy = copy.copy([self.houses, self.batteries])
                self.results_list.append(self.links_copy)
    if num < 125:
        print(f"Current house: {num}")


def bnb(self):
    """Branch and Bound parent.

    This method calls the actual depth first search and saves the best
    result found.
    """
    # 3 = 22185
    # 2 = 21627
    # 1 = 33687
    self.best = 34000
    print(f"Score to beat: {self.best}")
    self.solutions = 0
    self.results_list = []
    self.cost_list = []
    self.extra = []
    self.up = (1 / 125) * 100
    self.percentage = 0
    for i in self.houses:
        self.extra.append(self.houses[i])
        self.houses[i].filter()
    print("Processing...")
    print(f"{self.percentage}% done")
    bnb_search(self, 0)
    for i in range(self.solutions):
        print(f"The costs for solution{i}: {self.cost_list[i]}")
    with open(f"bnb_result_for_WIJK{self.input}.dat", "wb") as f:
        pickle.dump(self.results_list, f)

def bnb_search(self, num):
    cap_space = (150 - num) * 45 + 1507
    cost_space = (150 - num) * 45 + self.best
    for battery in self.extra[num].filtered:
        # print(self.extra[num].x, self.extra[num].y)
        # print(battery)
        # print(self.batteries[battery].x, self.batteries[battery].y)
        if self.extra[num].link == self.batteries[battery]:
            pass
        else:
            swap_houses(self, self.extra[num], self.extra[num].link, self.batteries[battery])
        if num < 149:
            # print(f"{num} is below 149")
            if self.batteries[battery].filled() > cap_space:
                continue
            elif calculate_cost(self) > cost_space:
                continue
            else:
                bnb_search(self, num + 1)
        elif not check_full(self):
            print(f"{num} is not full")
            self.solutions += 1
            print(f"Amount of solutions found: {self.solutions}")
            print(new)
            new = calculate_cost(self)
            self.cost_list.append(new)
            if new < self.best:
                self.best = new
                save_dat_file(self)
                self.results_list.append(new)
        else:
            print(f"{num} is full")
    if num < 10:
        self.percentage += 1
        print(f"{self.percentage}% done")


def random_algorithm(self, iterations):
    """Random algorithm, , saves best solution in pickle.

    This algorithm links houses and batteries
    so no battery is over it's capacity, this will be done
    with in random sequence.
    """
    # Put house objects in list
    random_houses = list(self.houses.values())

    # Initialize
    prices = []
    count = 0
    misses = -iterations

    # Get all battery indices
    batt_index = range(len(self.batteries))

    # Do until we have <iterations> succesfull configurations
    while count < iterations:

        # Disconnect possible connections from previous iteration
        disconnect(self)

        # While one or more batteries are over their capacity or not every
        # house is linked to a battery
        while check_linked(self) is False or check_full(self) is True:
            misses += 1

            # Randomize order of houses
            random.shuffle(random_houses)

            # Remove connections, if any
            disconnect(self)

            # For every house find closest battery to connect to provided
            # that this house wont over-cap the battery
            for house in random_houses:
                for i in range(len(self.batteries.values())):
                    index = sorted(batt_index, key=lambda k: random.random())
                    output = house.output
                    curr = self.batteries[index[i]].filled()
                    batt = self.batteries[index[i]]

                    # Check if operation is within constraints
                    if output + curr <= batt.capacity:
                        house.link = batt
                        batt.linked_houses.append(house)
                        break

        # Calculate price
        price = calculate_cost(self)
        prices.append(price)

        # Pickle cheapest configuration so far + sequence of houses
        if price is min(prices):
            house_batt = [self.houses, self.batteries]
            with open(f"random_greedy_lowest_WIJK{self.input}_{iterations}.dat",
                      "wb") as f:
                pickle.dump(house_batt, f)
            with open(f"sequence_lowest_WIJK{self.input}_{iterations}.dat",
                      "wb") as f:
                pickle.dump(random_houses, f)

        count += 1

    # Save all costs found for histogram
    with open(f"prices{self.input}_{iterations}.dat", "wb") as f:
        pickle.dump(prices, f)

    # Print results
    print(f"min: {min(prices)}")
    print(f"max: {max(prices)}")
    print(f"mean: {np.mean(prices)}")
    print(f"unsuccesfull iterations: {misses}")

    # Load cheapest solution, so it can be plotted
    with open(f"random_greedy_lowest_WIJK{self.input}_{iterations}.dat",
              "rb") as f:
        unpickler = pickle.Unpickler(f)
        house_batt = unpickler.load()
        self.houses, self.batteries = house_batt[0], house_batt[1]
