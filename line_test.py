# lijn test file van Julian

from house import House
from battery import Battery
import csv
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

from smartgrid import Smartgrid


INPUT_HOUSES = "wijk1_huizen.csv"



x_batt = 5
y_batt = 5

# make plot
ax = plt.gca()
ax.axis([-2, 52, -2 , 52])

ax.scatter(x_batt, y_batt, marker = "+")
ax.set_xticks(np.arange(0, 52, 1), minor = True)
ax.set_yticks(np.arange(0, 52, 1), minor = True)
ax.grid(b = True, which="major", linewidth=1)
ax.grid(b = True, which="minor", linewidth=.2)

# test to connect battery with house
# x_house = 10
# y_house = 10

map = "wijk1_huizen.csv"

with open(f"Huizen&Batterijen/{map}", newline="") as houses_csv:
    # read data from csv
    data_houses = csv.reader(houses_csv, delimiter=",")
    # skip headers
    next(data_houses, None)
    houses = {}

    # for every house, save coordinates and output in dictionary
    # name for instance in dict is Xcoord-Ycoord
    for row in data_houses:
        x = row[0]
        y = row[1]
        id = f"{x}-{y}"

        output = row[2]
        houses[id] = House(x, y, output)

meh = list(houses.values())
for house in meh:
    x_house = house.x
    y_house = house.y
    x_diff = x_batt - x_house

    # calculate the new coordinate for the vertical line
    new_x = x_house + x_diff
    ax.plot([x_house, x_batt], [y_house, y_house], color='b',linestyle='-', linewidth=2)
    ax.plot([new_x, new_x], [y_house, y_batt], color='b',linestyle='-', linewidth=2)
    ax.scatter(x_house , y_house, marker = ".")

    x_diff = abs(x_batt - x_house)
    y_diff = abs(y_batt - y_house)
    tot_cost = (x_diff + y_diff) * 9
    print(tot_cost)



# # calclate difference in x-coordinate
# x_diff = x_batt - x_house
# # if x_batt < x_house:
#     batt_loc_x = "Left"
#
# elif x_batt > x_house:
#     batt_loc_x = "Right"
#
# # else:
# #     batt_loc_x = "Same"
#
# y_diff = abs(y_batt - y_house)
# if y_batt < y_house:
#     batt_loc_y = "Lower"
#
# elif y_batt > y_house:
#     batt_loc_y = "Higher"
#
# # else:
# #     batt_loc_y = "Same"

# if batt_loc_x == "Left":
#     # make line to the left of the house with length x_diff
#     ax.plot([x_house, x_batt], [y_house, y_house], color='b',linestyle='-', linewidth=2)
#     pass
#
# elif batt_loc_x == "Right":
#     # make line to the right  of the house with length x_diff
#     ax.plot([x_house, x_batt], [y_house, y_house], color='b',linestyle='-', linewidth=2)
#     pass
#
# new_x = x_house + x_diff
# if batt_loc_y == "Lower":
#     # make line upwards on the endpoint of the previously made line
#     # with length y_diff
#     ax.plot([new_x, new_x], [y_house, y_batt], color='b',linestyle='-', linewidth=2)
#     pass
#
# elif batt_loc_y == "Higher":
#     # make line downwards on the endpoint of the previously made linewidth
#     # with length y_diff
#     ax.plot([new_x, new_x], [y_house, y_batt], color='b',linestyle='-', linewidth=2)
#     pass

# x_diff = x_batt - x_house
# # calculate the new coordinate for the vertical line
# new_x = x_house + x_diff
# ax.plot([x_house, x_batt], [y_house, y_house], color='b',linestyle='-', linewidth=2)
# ax.plot([new_x, new_x], [y_house, y_batt], color='b',linestyle='-', linewidth=2)
#
# x_diff = abs(x_batt - x_house)
# y_diff = abs(y_batt - y_house)
# tot_cost = (x_diff + y_diff) * 9
# print(tot_cost)


# dus x_diff = abs(x_batt - x_house) Dat is wat korter
# J: klopt, maar ik zit zelf nog ff te kijken naar een manier waarop het programma
# weet waar de lijn geplaatst moet worden

# calculate difference in y-coordinate


plt.show()
