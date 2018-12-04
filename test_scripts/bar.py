import matplotlib.pyplot as plt

# 1 step-down
# closest: 53188.0
# furthest: 103030.0
# our: 56401

# 1 step-down_protobatt_3
# closest: 40228
# furthest: 96964
# our: 41686

X1 = [53188, 56401, 103030]
X2 = [40228, 41686, 96964]

f, axs = plt.subplots(1, 2, sharex = False, sharey = True)
# axs[0].bar([1, 2, 3], X1, 0.5)
# axs[0].bar(X2)

axs[0].bar(["lower", "algorithm", "upper"], X1, color=("green", "blue", "red"))
axs[0].set_title("Before battery reallocation")
axs[1].bar(["lower", "algorithm", "upper"], X2, color=("green", "blue", "red"))
axs[1].set_title("After battery reallocation")

plt.show()
