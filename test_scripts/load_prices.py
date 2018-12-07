#!/usr/bin/python

import sys
import csv
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
import re
import operator
import os
import random
import statistics
import pickle
# from matplotlib.font_manager import FontProperties


from pathlib import Path

from helpers import *
"""
SLAAT HUIZEN NOG NIET MET JUISTE NAAM ENZO OP
"""

class Smartgrid(object):
    def __init__(self):
        self.plot()


    def plot(self):
        """
        Plots houses, batteries and cables. Also calculates the total
        cost of the cable
        """
        G1, R1, G2, R2, G3, R3 = self.load(1)[0], self.load(1)[1], \
                                 self.load(2)[0], self.load(2)[1], \
                                 self.load(3)[0], self.load(3)[1]

        L1, L2, L3 = 28188.0, 20268.0, 17757.0
        O1, O2, O3 = 31401, 21401, 20300.0
        H1, H2, H3 = 30843, 20574, 18801
        U1, U2, U3 = mode(R1), mode(R2), mode(R3)

        n_bins = 20

        f, axs =  plt.subplots(1, 3, sharex = False, sharey = False)
        axs[0].hist(G1, bins=n_bins)
        axs[1].hist(G2, bins=n_bins)
        axs[2].hist(G3, bins=n_bins)
        axs[0].hist(R1, bins=n_bins)
        axs[1].hist(R2, bins=n_bins)
        axs[2].hist(R3, bins=n_bins)
        axs[0].vlines(L1, 0, 200, color = "g")
        axs[1].vlines(L2, 0, 200, color = "g")
        axs[2].vlines(L3, 0, 200, color = "g")
        axs[0].vlines(O1, 0, 200, color = "purple")
        axs[1].vlines(O2, 0, 200, color = "purple")
        axs[2].vlines(O3, 0, 200, color = "purple")
        axs[0].vlines(H1, 0, 200, color = "brown")
        axs[1].vlines(H2, 0, 200, color = "brown")
        axs[2].vlines(H3, 0, 200, color = "brown")
        axs[0].vlines(U1, 0, 200, color = "r")
        axs[1].vlines(U2, 0, 200, color = "r")
        axs[2].vlines(U3, 0, 200, color = "r")
        axs[0].set_ylim(0, 170)
        axs[1].set_ylim(0, 170)
        axs[2].set_ylim(0, 170)
        axs[0].set_title("Wijk 1")
        axs[1].set_title("Wijk 2")
        axs[2].set_title("Wijk 3")

        red_patch = mpatches.Patch(color='red', label='Upper Bound')
        green_patch = mpatches.Patch(color='g', label='Absolute Lower Bound')
        blue_patch = mpatches.Patch(color='#1f77b4', label='Greedy Algorithm')
        orange_patch = mpatches.Patch(color='#ff7f0e', label='Random Algorithm')
        purple_patch = mpatches.Patch(color='purple', label='Step-down Algorithm')
        brown_patch = mpatches.Patch(color='brown', label='Hill-climber Algorithm')
        handles = [red_patch, green_patch, blue_patch, orange_patch, purple_patch, brown_patch]
        axs[2].legend(handles = handles, bbox_to_anchor=(1.4, 1.05))


        plt.show()

    def load(self, wijk):
        """
        This function changes links between houses and batteries
        so no battery is over it's capacity, this will be done
        with lowest cost possible for this algorithm
        """
        with open(f"prices{wijk}_1000.dat", "rb") as f:
            unpickler = pickle.Unpickler(f)
            prices_greedy = unpickler.load()

        with open(f"prices{wijk}_1000_RANDOM.dat", "rb") as f:
            unpickler = pickle.Unpickler(f)
            prices_random = unpickler.load()

        return [prices_greedy, prices_random]
if __name__ == "__main__":
    Smartgrid()
