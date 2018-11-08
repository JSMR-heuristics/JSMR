# kijken naar de huizen op alle volle Batterijen
# kies het huis dat het goedkoopst naar een niet volle batterij kan
# verander de link van dat huis naar die niet volle batterij

for battery in self.batteries:
    if battery.capacity <= sum(battery.linked_houses.output):
        battery.full = True

switch = 9999
switch_batt = 0
go = 9999
go_batt = 0
changer = 0

for battery in self.batteries:
    while battery.full == True:
        for house in battery.linked_houses:
            for link in house.diffs.items():
                if (battery.capacity - sum(battery.linked_houses.output)) >
                house.output && link[1] < switch:
                    switch = link[1]
                    switch_batt = link[0]
            if switch < go:
                go = switch
                go_batt = switch_batt
                changer = house
                switch = 9999
        changer.link = go_batt
