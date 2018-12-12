import operator, random, os, sys, pickle, time, copy
import numpy as np


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
        swap_houses(self, house, curr_batt, to_batt, changes)
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
        time_var = time.strftime("%d%m%Y_%H%M")
        if price is min(prices):
            house_batt = [self.houses, self.batteries]
            cwd = os.getcwd()
            path = os.path.join(*[cwd, 'data', 'pickles', f"greedy_lowest_WIJK{self.input}_{time_var}.dat"])
            sys.path.append(path)
            with open(path, "wb") as f:
                pickle.dump(house_batt, f)

            cwd = os.getcwd()
            path = os.path.join(*[cwd, 'data', 'pickles', f"sequence_lowest_WIJK{self.input}_{time_var}.dat"])
            sys.path.append(path)
            with open(path, "wb") as f:
                pickle.dump(random_houses, f)


        count += 1
        print(count)
    print(f"min: {min(prices)}")
    print(f"max: {max(prices)}")
    print(f"mean: {np.mean(prices)}")
    print(f"unsuccesfull iterations: {misses}")

    return int(min(prices))


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

                for i in range(4):
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
            house_batt = [self.houses, self.batteries]
            with open(f"hill_climber_batt_lowest_WIJK{self.input}_{time_var}.dat", "wb") as f:
                pickle.dump(house_batt, f)
            with open(f"sequence_lowest_WIJK{self.input}_{time_var}.dat", "wb") as f:
                pickle.dump(random_houses, f)
        count += 1
        print(count)

    print(f"min: {min(prices)}")
    print(f"max: {max(prices)}")
    print(f"mean: {np.mean(prices)}")
    print(f"unsuccesfull iterations: {misses}")

    return int(min(prices))

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
    # print(self.batteries[0])
    # print(self.batteries[1])
    # print(self.batteries[2])
    # print(self.batteries[3])
    # print(self.batteries[4])
    # nope = 0
    # yup = 0
    solutions = 0
    results_list = []
    cost_list = []
    best = 33660
    a, b, c, d, e = 0, 1, 2, 3, 4
    x = 0
    for i in self.houses:
        self.houses[i].link = self.batteries[0]
        self.batteries[0].linked_houses.append(self.houses[i])
    for one in self.houses:
        swap_houses(self, self.houses[one], self.houses[one].link, self.batteries[a])
        print(f"Amount of rounds = {x}")
        x += 1
        for two in self.houses:
            if self.houses[two] == self.houses[one]:
                continue
            swap_houses(self, self.houses[two], self.houses[two].link, self.batteries[b])
            for three in self.houses:
                if self.houses[three] == self.houses[one] or self.houses[three] == self.houses[two]:
                    continue
                swap_houses(self, self.houses[three], self.houses[three].link, self.batteries[c])
                for four in self.houses:
                    if self.houses[four] == self.houses[one] or self.houses[four] == self.houses[two] or self.houses[four] == self.houses[three]:
                        continue
                    swap_houses(self, self.houses[four], self.houses[four].link, self.batteries[d])
                    for five in self.houses:
                        if self.batteries[e].full():
                            break
                        if self.houses[five] == self.houses[one] or self.houses[five] == self.houses[two] or self.houses[five] == self.houses[three] or self.houses[five] == self.houses[four]:
                            continue
                        swap_houses(self, self.houses[five], self.houses[five].link, self.batteries[e])
                        print(check_full(self))
                        if not check_full(self):
                            solutions += 1
                            print(solutions)
                            new = calculate_cost(self)
                            if new < best:
                                best = new
                                links_copy = copy.copy([self.houses, self.batteries])
                                results_list.append(links_copy)
                                cost_list.append(new)

    print(cost_list)
    with open(f"dfs_result_for_WIJK{self.input}.dat", "wb") as f:
        pickle.dump(results_list, f)
