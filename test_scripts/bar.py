import matplotlib.pyplot as plt
import numpy as np

# 1 step-down
# closest: 53188.0
# furthest: 103030.0
# our: 56401

# 1 step-down_protobatt_3
# closest: 40228
# furthest: 96964
# our: 41686
N = 3

X1 = [53188, 56401, 103030]
X2 = [40228, 41686, 96964]
X3 = [(13860 + 10800), (14832 + 10800), (76518 + 10800)]


# long = [, , , , , , , , ]
# long_text = [ , , , "41686", , , , ]

long = [53188, 40228, (13860 + 10800), 56401, 41686, (14832 + 10800), 103030, 96964, (76518 + 10800)]
long_text = ["53188", "40228", "24660", "56401", "41686", "25632", "103030", "96964", "87318"]
L = [53188, 40228, (13860 + 10800)]
A = [56401, 41686, (14832 + 10800)]
U = [103030, 96964, (76518 + 10800)]

fig, ax = plt.subplots()
ind = np.arange(N)

width = 0.25
x = [0, 0 + width, 0 + width * 2, 1, 1 + width, 1 + width * 2, 2, 2 + width, 2 + width * 2,]

p1 = ax.bar(ind, X1, width, color="c")
p2 = ax.bar(ind + width, X2, width, color="slategrey")
p3 = ax.bar(ind + 2 * width, X3, width, color="indianred")


ax.set_title('Change of Cost for Absolute Lower and Upper bounds \n and Outcome of Greedy Algorithm')
ax.set_xticks(ind + width)
ax.set_xticklabels(('Lower-Bound', 'Algorithm', 'Upper-Bound'))
ax.legend((p1[0], p2[0], p3[0]), ('Fixed', 'Reallocated', 'Reconfigured'))
# for i in range(9):
#     ax.text(x[i], (long[i] - 3000), long_text[i], horizontalalignment="center", fontsize=9, color="black")
plt.ylabel("Cost", fontsize=12)
ax.autoscale_view()

plt.show()
# f, axs = plt.subplots(1, 1, sharex = False, sharey = True)
# # axs[0].bar([1, 2, 3], X1, 0.5)
# # axs[0].bar(X2)
#
# axs[0].bar(["lower", "algorithm", "upper"], X1, color=("green", "blue", "red"))
# axs[0].set_title("Before battery reallocation")
# axs[1].bar(["lower", "algorithm", "upper"], X2, color=("green", "blue", "red"))
# axs[1].set_title("After battery reallocation")

plt.show()
