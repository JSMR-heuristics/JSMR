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
                if link[key/battery].full == False && link[value/distance] < switch[value/distance]:
                    switch = link
            if switch < go:
                go = switch
