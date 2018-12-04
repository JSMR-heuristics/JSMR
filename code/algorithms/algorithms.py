import operator
import random
import numpy as np
import pickle

from helpers import *
import time


def optimize(self):
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
    while check_full(self) and changes < 50:

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
            with open(f"greedy_lowest_WIJK{self.input}_{time_var}.dat", "wb") as f:
                pickle.dump(house_batt, f)
            with open(f"sequence_lowest_WIJK{self.input}_{time_var}.dat", "wb") as f:
                pickle.dump(random_houses, f)


        count += 1
        print(count)
    print(f"min: {min(prices)}")
    print(f"max: {max(prices)}")
    print(f"mean: {np.mean(prices)}")
    print(f"unsuccesfull iterations: {misses}")
