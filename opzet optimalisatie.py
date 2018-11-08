# kijken naar de huizen op alle volle Batterijen
# kies het huis dat het goedkoopst naar een niet volle batterij kan
# verander de link van dat huis naar die niet volle batterij

for battery in self.batteries:
    if battery.capacity <= sum(battery.linked_houses.output):
        battery.full = True

switch = 9999
go = 9999

for battery in self.batteries:
    while battery.full == True:
        for house in battery.linked_houses:
            for link in house.ord_dist:
                if self.batteries["link:key"].full == False && link < switch:
                    switch = link
                    switch_batt = "link:key"
            if switch < go:
                go = switch
                go_batt = "go:key"
                changer = house
        changer.link = go
