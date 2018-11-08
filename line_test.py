# lijn test file van Julian

from house import House
from battery import Battery
import csv
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker



# test to connect battery with house
x_house = 10
y_house = 10

x_batt = 20
y_batt = 20

# make plot
ax = plt.gca()
ax.axis([-2, 52, -2 , 52])
ax.scatter(x , y, marker = ".")
ax.scatter(x_batt, y_batt, marker = "+")
ax.set_xticks(np.arange(0, 52, 1), minor = True)
ax.set_yticks(np.arange(0, 52, 1), minor = True)
ax.grid(b = True, which="major", linewidth=1)
ax.grid(b = True, which="minor", linewidth=.2)

# calclate difference in x-coordinate
x_diff = abs(x_batt - x_house)
if x_batt < x_house:
    batt_loc = "Left"

elif x_batt > x_house:
    batt_loc = "Right"

else:
    batt_loc = "Same"

y_diff = abs(y_batt - y_house)
if y_batt < y_house:
    batt_loc = "Lower"

elif y_batt > y_house:
    batt_loc = "Higher"

else:
    batt_loc = "Same"
# dus x_diff = abs(x_batt - x_house) Dat is wat korter
# J: klopt, maar ik zit zelf nog ff te kijken naar een manier waarop het programma
# weet waar de lijn geplaatst moet worden

# calculate difference in y-coordinate


plt.show()
