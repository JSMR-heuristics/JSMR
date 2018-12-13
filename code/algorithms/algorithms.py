import operator, random, os, sys, pickle, time, copy
import numpy as np
import os


from helpers import *


def stepdown(self):
    """
    This function changes links between houses and batteries
    so no battery is over it's capacity, this will be done
    with lowest cost possible for this algorithm
    """
    # Initialize changes counter, this gives insight to
    # the speed of this algorithm
    changes = 0
    # for num in self.batteries:
    #     print(f"Battery{num}: {self.batteries[num].filled()}")
    #     for ding in self.batteries[num].linked_houses:
    #         print(f"House: {ding.output}")

    # While one or more batteries are over their capacity
    while check_full(self) and changes < 500:

        # kan korter
        # Sorts batteries based off total inputs from high to low
        total_inputs = []
        for battery in self.batteries.values():
            total_inputs.append([battery.filled(), battery])
        high_low = sorted(total_inputs, key=operator.itemgetter(0), reverse = True)

        # Prioritize battery with highest inputs
        # to disconnect a house from
        # for i in high_low:
        battery = high_low[0][1]

        # Sort houses linked to this battery by distance
        # to other battery from low to high
        # distance_list = self.sort_linked_houses(battery)
        distance_list = sort_linked_houses(self, battery)

        # Determine the cheapest option first, if any
        # else transfer option with lowest output
        try:
            house, to_batt = find_best(self, distance_list, "strict")
        except TypeError:
            house, to_batt = find_best(self, distance_list, "not-strict")

        # Switch the house from battery
        curr_batt = house.link
        changes += 1
        swap_houses(self, house, curr_batt, to_batt)
        if (changes % 5) is 0 and self.plot_option == "y":
            self.plot_houses(changes)
        # break
    self.plot_houses("FINAL")
    for i in self.batteries:
        print(self.batteries[i].filled())
        print(f"{self.batteries[i].x}/{self.batteries[i].y}")


def greedy(self, iterations):
    """
    This function changes links between houses and batteries
    so no battery is over it's capacity, this will be done
    with lowest cost possible for this algorithm


    SEQUENCES ONTHOUDEN VOOR EXTRA PUNTEN!!!!!!!!!! id's
    """
    # turn houses into list
    random_houses = list(self.houses.values())

    iterations = int(iterations)

    prices = []
    count = 0
    misses = -iterations

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
                for i in range(5):
                    if house.output + self.batteries[list(house.diffs)[i]].filled() <= self.batteries[list(house.diffs)[i]].capacity:
                        house.link = self.batteries[list(house.diffs)[i]]
                        self.batteries[list(house.diffs)[i]].linked_houses.append(house)
                        break

        # calculate price
        price = calculate_cost(self)
        prices.append(price)

        # pickle cheapest configuration so far + sequence of houses
        # include time
        time_var = time.strftime("%d%m%Y")

        if price is min(prices):
            save_dat_file(self)


        count += 1
        # print(count)
    print(f"min: {min(prices)}")
    print(f"max: {max(prices)}")
    print(f"mean: {np.mean(prices)}")
    print(f"unsuccesfull iterations: {misses}")

    return f"greedy_lowest_WIJK{self.input}_{time_var}.dat"


def hill_climber(self, iterations):
    """
    This function changes links between houses and batteries
    so no battery is over it's capacity, this will be done
    with lowest cost possible for this algorithm
    """

    random_houses = list(self.houses.values())
    random_houses_2 = list(self.houses.values())
    iterations = int(iterations)
    count = 0
    misses = -iterations
    prices = []

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
            for house in random_houses:

                for i in range(len(self.batteries.values())):
                    if house.output + self.batteries[list(house.diffs)[i]].filled() <= self.batteries[list(house.diffs)[i]].capacity:
                        house.link = self.batteries[list(house.diffs)[i]]
                        self.batteries[list(house.diffs)[i]].linked_houses.append(house)
                        break
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
    self.best = 22000
    print(f"Score to beat: {self.best}")
    self.solutions = 0
    self.results_list = []
    self.cost_list = []
    self.extra = []
    for i in self.houses:
        self.extra.append(self.houses[i])
        self.houses[i].filter()
    print("Initialized")
    bnb_search(self, 0)
    for i in range(self.solutions):
        print(f"The costs for solution{i}: {self.cost_list[i]}")
    with open(f"bnb_result_for_WIJK{self.input}.dat", "wb") as f:
        pickle.dump(self.results_list, f)


def bnb_search(self, num):
    lower = (150 - num) * 35 + 1507
    prospect = (150 - num) * 70
    for battery in self.extra[num].filtered:
        if self.extra[num].link == self.batteries[battery]:
            pass
        else:
            swap_houses(self, self.extra[num], self.extra[num].link, self.batteries[battery])
        if num > 144:
            if num < 149:
                bnb_search(self, num + 1)
            elif not check_full(self):
                self.solutions += 1
                print(f"Amount of solutions found: {self.solutions}")
                new = calculate_cost(self)
                self.cost_list.append(new)
                if new < self.best:
                    self.best = new
                    self.links_copy = copy.copy([self.houses, self.batteries])
                    self.results_list.append(self.links_copy)
        elif num > 115:
            if self.batteries[battery].filled() > lower:
                continue
            elif calculate_cost(self) > self.best + prospect:
                continue
            else:
                bnb_search(self, num + 1)
        elif num < 15:
            bnb_search(self, num + 1)
        else:
            if self.batteries[battery].filled() > lower:
                return
            elif calculate_cost(self) > self.best + prospect:
                return
            else:
                bnb_search(self, num + 1)
    if num < 100:
        print(f"Current house: {num}")

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
