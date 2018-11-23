import operator

def calculate_distance(self):
    all_distances = []
    for house in self.houses.values():
        x_house, y_house = house.x, house.y
        house_diff = {}
        counter = 0
        for battery in self.batteries.values():
            x_batt, y_batt = battery.x, battery.y
            x_diff = abs(x_batt - x_house)
            y_diff = abs(y_batt - y_house)
            house_diff[counter] = (x_diff + y_diff)
            counter += 1
        house_diff = dict(sorted(house_diff.items(), key=operator.itemgetter(1)))
        all_distances.append(house_diff)
    return all_distances

def sort_linked_houses(self, battery):
    """
    Sorts list of linked houses of a battery by distances
    """
    distance_list = []
    for house in battery.linked_houses:
        batts = list(house.diffs.keys())
        distance = []
        weight = 50 / house.output
        for diff in list(house.diffs.values()):
            weighted_diff = diff * weight
            distance.append(weighted_diff)
        # distance = list(house.diffs.values())
        # print(weight)
        # print(distance)
        houses = [house] * len(distance)
        outputs = [house.output] * len(distance)
        element = []
        element = list(map(list, zip(batts, distance, houses, outputs)))
        distance_list += element

    return sorted(distance_list, key=operator.itemgetter(1))

def find_best(self, list, status):
    """
    Tries to find either the cheapest house to possibly switch from battery
    or the one with the lowest possible output
    """
    if status is "strict":
        for option in list:
            a = self.batteries[option[0]].filled() + option[2].output
            b = self.batteries[option[0]].capacity
            c = b - a
            if a <= b and not 7 < c < 35:
                return option[2], self.batteries[option[0]]
    # wordt vervangen door output gewicht
    else:
        list = sorted(list, key=operator.itemgetter(3))
        for option in list:
            if (option[2].link.filled() - option[2].output) < option[2].link.capacity:
                print(option[2].link.filled() - option[2].output)
                return option[2], self.batteries[option[0]]

# conditie toevoegen om te zorgen dat huizen niet op een batterij komen die verder dan een max afstand ligt
# conditie toevoegen om te zorgen dat een huis niet wordt verplaatst als dat de batterij nét niet onder full brengt

def swap_houses(self, house, current_batt, next_batt, changes):
    """
    Switches house from battery it's currently linked to, to the next
    one
    """
    house.link = next_batt
    next_batt.linked_houses.append(house)
    current_batt.linked_houses.remove(house)
    print(f"house at x{house.x}/y{house.y} changed from battery at x{current_batt.x}/y{current_batt.y} to battery at x{next_batt.x}/y{next_batt.y}")
    print(f"house capacity = {house.output}")
    print(f"capacity = {current_batt.filled()}")
    print(f"changes = {changes}")
