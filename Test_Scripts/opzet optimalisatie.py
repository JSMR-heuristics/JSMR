def optimize(self):
    # Check every battery's capacity
    for battery in self.batteries:
        if battery.capacity <= sum(battery.linked_houses.output):
            battery.full = True

    # Initialize variables
    switch = 9999
    switch_batt = 0
    go = 9999
    go_batt = 0
    changer = 0

    # Iterate every battery
    for battery in self.batteries:
        while battery.full == True:
            # Iterate every house linked to the battery
            for house in battery.linked_houses:
                # Check every possible connection the house has
                for link in house.diffs.items():
                    # If the connection switch is possible, save it
                    if (battery.capacity - sum(battery.linked_houses.output)) >
                    house.output && link[1] < switch:
                        switch = link[1]
                        switch_batt = link[0]
                # Check the house's best switch option against the best overal
                # option for the battery
                if switch < go:
                    go = switch
                    go_batt = switch_batt
                    changer = house
                    switch = 9999
            # Change the connection for the best house
            changer.link = go_batt
