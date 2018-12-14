import operator
import random
import os
import sys
import pickle
import time
import copy
import numpy as np
import os

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
    """Greedy algorithm, non deterministic.

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
    """Hill climber, non deterministic.

    This function changes links between houses and batteries
    so no battery is over it's capacity, this will be done
    with lowest cost possible for this algorithm.
    """
    random_houses = list(self.houses.values())
    random_houses_2 = list(self.houses.values())
    iterations = int(iterations)
    count = 0
    misses = -iterations
    prices = []
    print(self.batteries.values)
    batt_index = range(len(self.batteries))
    print(f"batt_index= {batt_index}")
    # Do untill we have <iterations> succesfull configurations
    while count < iterations:
        disconnect(self)
        # connect random houses to the closest option  within the constraints
        # While one or more batteries are over their capacity or not every
        # house is linked to a battery
        while check_linked(self) is False or check_full(self) is True:
            # print(misses)
            misses += 1

            # shuffle order of houses
            random.shuffle(random_houses)
            # remove connections, if any
            disconnect(self)

            # for every house find closest battery to connect to provided
            # that this house wont over-cap the battery
            # for house in random_houses:
            #
            #     for i in range(len(self.batteries.values())):
            #         if house.output + self.batteries[list(house.diffs)[i]].filled() <= self.batteries[list(house.diffs)[i]].capacity:
            #             house.link = self.batteries[list(house.diffs)[i]]
            #             self.batteries[list(house.diffs)[i]].linked_houses.append(house)
            #             break
            for house in random_houses:
                index = random.sample(batt_index, 1)[0]
                house.link = self.batteries[index]
                self.batteries[index].linked_houses.append(house)


        base_copy = copy.copy([self.houses, self.batteries])
        base_cost = calculate_cost(self)

        print("Start Hillclimb")
        step_back_cost = base_cost
        step_back = base_copy

        climbs = 0
        hillcount = 0
        alt_directions = 150 * 150

        random.shuffle(random_houses)
        random.shuffle(random_houses_2)

        # shorten time by checking calbe diff instead of whole gridcost
        while hillcount < alt_directions:
            # loop while the new step is inefficient
            for house_1 in random_houses:
                for house_2 in random_houses_2:
                    # take a step if not the same batteries
                    if not (house_1.link == house_2.link):
                        switch_houses(self, house_1, house_2)
                        step_cost = calculate_cost(self)
                        if (step_cost < step_back_cost) and (check_full(self) is False):
                            climbs += 1
                            step_back = copy.copy([self.houses, self.batteries])
                            step_back_cost = step_cost
                            hillcount = 0
                        else:
                            switch_houses(self, house_1, house_2)
                            #self.houses, self.batteries = step_back[0], step_back[1]
                    hillcount += 1

        print(f"bc={base_cost}, hilltop = {step_cost}")
        time_var = time.strftime("%d%m%Y")
        prices.append(step_cost)

        if step_cost is min(prices):
            save_dat_file(self)
            # house_batt = [self.houses, self.batteries]
            # path = os.path.join(*[cwd, 'results', f'wijk_{self.input}', 'hill'])
            #
            # with open(f"hill_climber_batt_lowest_WIJK{self.input}_{time_var}.dat", "wb") as f:
            #     pickle.dump(house_batt, f)
            # with open(f"sequence_lowest_WIJK{self.input}_{time_var}.dat", "wb") as f:
            #     pickle.dump(random_houses, f)
        count += 1
        print(count)

    with open(f"prices_list_WIJK{self.input}_hill.dat", "wb") as f:
        pickle.dump(prices, f)

    print(f"min: {min(prices)}")
    print(f"max: {max(prices)}")
    print(f"mean: {np.mean(prices)}")
    print(f"unsuccesfull iterations: {misses}")

def backup(self):
    """
    Probeer wijk 3 weer te laten werken maar zonder succes
    """
    # Initialize changes counter, this gives insight to
    # the speed of this algorithm
    changes = 0

    # While one or more batteries are over their capacity
    while check_full(self):

        # Sorts batteries based off total inputs from high to low
        total_inputs = []
        for battery in self.batteries.values():
            total_inputs.append([battery.filled(), battery])
        high_low = sorted(total_inputs, key=operator.itemgetter(0), reverse = True)

        # Prioritize battery with highest inputs
        # to disconnect a battery from
        for i in high_low:
            battery = i[1]
            distance_list = []

            # Sort houses linked to this battery by distance
            # to other battery from low to high
            for house in battery.linked_houses:
                element = []
                batts = list(house.diffs.keys())
                distance = list(house.diffs.values())
                houses = [house] * len(distance)
                outputs = [house.output] * len(distance)
                element = list(map(list, zip(batts, distance, houses, outputs)))
                distance_list += element
            distance_list = sorted(distance_list, key=operator.itemgetter(1))

            # Determine the cheapest option first, if any
            # else transfer option with lowest output
            try:
                print(distance_list)
                house, to_batt = find_best_backup(self, distance_list, "strict")
            except TypeError:
                print("type-error")
                house, to_batt = find_best_backup(self, distance_list, "not-strict")

            # Switch the house from battery
            curr_batt = house.link
            changes += 1
            swap_houses(self, house, curr_batt, to_batt, changes)


def dfs(self):
    self.best = greedy(self, 500)
    self.extra = []
    for i in self.houses:
        self.extra.append(self.houses[i])
    dfs_search(self, 0)
    for i in range(self.solutions):
        print(f"The costs for solution{i}: {self.cost_list[i]}")
    with open(f"dfs_result_for_WIJK{self.input}.dat", "wb") as f:
        pickle.dump(self.results_list, f)

def dfs_search(self, num):
    for battery in self.batteries:
        if self.extra[num].link == self.batteries[battery]:
            pass
        else:
            swap_houses(self, self.extra[num], self.extra[num].link, self.batteries[battery])
        if num < 149:
            dfs_search(self, num + 1)
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
    """
    This function changes links between houses and batteries
    so no battery is over it's capacity, this will be done
    with lowest cost possible for this algorithm
    """
    # turn houses into list
    random_houses = list(self.houses.values())

    prices = []
    count = 0
    misses = -iterations
    batt_index = [0, 1, 2, 3, 4]

    # Do untill we have <iterations> succesfull configurations
    while count < iterations:
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
            for house in random_houses:
                for i in range(len(self.batteries.values())):
                    index = sorted(batt_index, key=lambda k: random.random())
                    output = house.output
                    curr = self.batteries[index[i]].filled()
                    batt = self.batteries[index[i]]

                    if output + curr <= batt.capacity:
                        house.link = batt
                        batt.linked_houses.append(house)
                        break

        # calculate price
        price = calculate_cost(self)
        prices.append(price)

        # pickle cheapest configuration so far + sequence of houses
        if price is min(prices):
            house_batt = [self.houses, self.batteries]
            with open(f"random_greedy_lowest_WIJK{self.input}_{iterations}.dat", "wb") as f:
                pickle.dump(house_batt, f)
            with open(f"sequence_lowest_WIJK{self.input}_{iterations}.dat", "wb") as f:
                pickle.dump(random_houses, f)

        count += 1
    with open(f"prices{self.input}_{iterations}.dat", "wb") as f:
        pickle.dump(prices, f)


    print(f"min: {min(prices)}")
    print(f"max: {max(prices)}")
    print(f"mean: {np.mean(prices)}")
    print(f"unsuccesfull iterations: {misses}")

    with open(f"random_greedy_lowest_WIJK{self.input}_{iterations}.dat", "rb") as f:
        unpickler = pickle.Unpickler(f)
        house_batt = unpickler.load()
        self.houses, self.batteries = house_batt[0], house_batt[1]
