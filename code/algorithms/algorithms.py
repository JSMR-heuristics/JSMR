import copy
import datetime
import numpy as np
import operator
import pickle
import random
import time

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

        #  note the user that the hillclimb portion of the
        #  iteration has been initiated
        print("Start Hillclimb")

        # Initializing
        hillcount = 0
        alt_directions = 150 * 150
        prices = []

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
                        #  calculate the new cost
                        step_cost = calculate_cost(self)
                        #  check if the new step costs less and fits within
                        #  the contraintst
                        if (step_cost < step_back_cost) and (check_full(self) is
                                                             False):
                            #  make the current step the curently best found
                            #  configuration
                            step_back = copy.copy([self.houses, self.batteries])
                            step_back_cost = step_cost
                            #  reset the counter for checking directions
                            hillcount = 0
                        else:
                            # switch back the houses
                            switch_houses(self, house_1, house_2)
                    #  increment the tried directions
                    hillcount += 1
        # keep track for the user the stating cost and
        # the end cost of the iteration
        print(f"bc={base_cost}, hilltop = {step_cost}")
        time_var = time.strftime("%d%m%Y")
        prices.append(step_cost)

        # Save setup if this is the cheapest found of all the iterations up to
        # this point
        if step_cost is min(prices):
            # saves the current configuration to its respective folder in the
            # results folder as a .dat file and overwrites the previously made
            # .dat file
            save_dat_file(self)
        #  keeps track of the succesfull iterations
        count += 1
        print(count)

    #  gives the user the most relevant details when all the iterations
    #  are completed
    print(f"min: {min(prices)}")
    print(f"max: {max(prices)}")
    print(f"mean: {np.mean(prices)}")
    print(f"unsuccesfull iterations: {misses}")


def dfs(self):
    """This sets up the conditions for the depth-first algorithm below"""

    # These numbers refer to a simple cost that should at the very least be
    # improved for a score to be saved. Every time that happens, the variable
    # self.best is replaced with the new score.
    if self.input == 1:
        self.best = 34000
    elif self.input == 2:
        self.best = 22000
    else:
        self.best = 22500

    # Creates a new list of houses, which is iterable by number
    self.extra = []

    # Put house objects in list
    for i in self.houses:
        self.extra.append(self.houses[i])

    # Call actual depth first search, starting from the first house at 0
    dfs_search(self, 0)

    # Saves a list of results that got the lowest score at the time
    with open(f"dfs_result_for_WIJK{self.input}.dat", "wb") as f:
        pickle.dump(self.results_list, f)


def dfs_search(self, num):
    """
    Depth-first search algorithm.

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
            print(f"Number of solutions found: {self.solutions}")
            new = mini_cost(self)
            self.cost_list.append(new)
            if new < self.best:
                self.best = new
                save_dat_file(self)
                self.results_list.append(self.links_copy)
    if num < 125:
        print(f"Current house: {num}")


def bnb(self):
    """This sets up the conditions for the branch-and-bound algorithm below"""

    # These numbers refer to a simple cost that should at the very least be
    # improved upon for a score to be saved. Every time that happens,
    # the variable self.best is replaced with the new score
    if self.input == 1:
        self.best = 34000
    elif self.input == 2:
        self.best = 22000
    else:
        self.best = 22500

    print(f"Score to beat: {self.best}")

    # Several variables that are used in the search
    self.solutions = 0
    self.results_list = []
    self.cost_list = []
    self.extra = []

    # This serves to clear all batteries of any possible connections that may
    # corrupt the search
    for battery in self.batteries:
        self.batteries[battery].linked_houses = []

    # Likewise, the houses are all cleared of any connections, plus the
    # iterable list of houses self.extra is appended. In addition, for every
    # house, filter() is run, which creates a list of batteries in order of
    # distance to that specific house
    for i in self.houses:
        self.houses[i].link = None
        self.extra.append(self.houses[i])
        self.houses[i].filter()

    # An initial print statement letting the user know the algorithm has
    # launched is printed, and the search loop is entered with the first house
    # in the list.
    print("Processing...")
    bnb_search(self, 0)

    # The list of results found is saved to a pickle file
    with open(f"bnb_result_for_WIJK{self.input}.dat", "wb") as f:
        pickle.dump(self.results_list, f)


def bnb_search(self, num):
    """
    Branch-and-bound algorithm.

    This algorithm explores the state space in a similar fashion as the
    depth-first algorithm, but has added checks that will cut off certain
    branches that are deemed to have no chance at returning a useful result.
    """

    # Saves the output for the current house in a variable
    output = self.extra[num].output

    # Calculates an approximated minimal amount of cost that the following
    # houses will have, to be used in pruning checks. The current best cost is
    # reduced buy the amount of houses still left to be connected times 45.
    # The number 45 is made by multiplying 5 (the approximated average minimal
    # distance between a house and battery) with 9 (the cable cost per segment)
    cost_margin = self.best - (149 - num) * 45

    # Here the loop starts, by checking the current house (represented by num)
    # with the battery options in order of distance (closest to farthest),
    # which is saved in every house's "filtered" attribute
    for battery in self.extra[num].filtered:

        # This loop is specific for the houses earlier in the list, which are
        # checked for their potential cost.
        if num < 120:
            # If connecting the current house to the current battery puts that
            # battery over capacity, the branch is skipped
            if self.batteries[battery].filled() + output > 1507:
                pass
            # The connection is then made and checked for the resulting cost.
            # If that new cost is still profitable, the branch is explored
            # further
            else:
                self.extra[num].link = self.batteries[battery]
                self.batteries[battery].linked_houses.append(self.extra[num])
                if mini_cost(self, num + 1) > cost_margin:
                    pass
                else:
                    bnb_search(self, num + 1)
                # Once the branch has been explored below, the connection is
                # undone
                self.batteries[battery].linked_houses.remove(self.extra[num])

        # This loop is specific for the houses later in the list, which are not
        # checked for their potential cost.
        elif num < 149:
            if self.batteries[battery].filled() + output > 1507:
                pass
            else:
                self.extra[num].link = self.batteries[battery]
                self.batteries[battery].linked_houses.append(self.extra[num])
                bnb_search(self, num + 1)
                self.batteries[battery].linked_houses.remove(self.extra[num])

        # If this part is entered, the last house is the list has been
        # succesfully reached, and a check for a solution will be made
        else:
            if self.batteries[battery].filled() + output > 1507:
                pass
            else:
                self.extra[num].link = self.batteries[battery]
                self.batteries[battery].linked_houses.append(self.extra[num])

                # To ensure nothing has gone wrong, another check of all of the
                # batteries is made.
                if not check_full(self):

                    # As the current setup is approved, the cost is calculated
                    self.solutions += 1
                    new = mini_cost(self, num + 1)
                    self.cost_list.append(new)

                    # Every 1000 solutions, a the amount of solutions is
                    # printed, to give the user an idea of the progress
                    if self.solutions % 1000 == 0:
                        print(f"{self.solutions} solutions found at"
                              + f"{datetime.datetime.now()}")

                    # The new result is checked to see if it's better than any
                    # previous one and, if so, it is saved
                    if new < self.best:
                        print(f"New best found: {new}"
                              + f"Solutions found: {self.solutions}")
                        self.best = new
                        save_dat_file(self)
                        self.results_list.append(new)
                self.batteries[battery].linked_houses.remove(self.extra[num])


def mini_cost(self, num):
    """A slightly more inefficient version of calculate_cost, specifically
    made to be used by the above branch-and-bound algorithm"""

    cost = 0
    for i in range(num):
        cost += (abs(self.extra[i].link.x - self.extra[i].x) + abs(self.extra[i].link.y - self.extra[i].y)) * 9
    return cost


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
