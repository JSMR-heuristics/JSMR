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
        list = self.load()
        print(list)
        plt.plot(list)
        plt.ylabel("Cable cost")
        plt.xlabel("iterations")
        plt.show()

    def load(self):
        """
        This function changes links between houses and batteries
        so no battery is over it's capacity, this will be done
        with lowest cost possible for this algorithm
        """
        with open(f"test_pickle.dat", "rb") as f:
            unpickler = pickle.Unpickler(f)
            prices_hill = unpickler.load()


        return prices_hill
if __name__ == "__main__":
    Smartgrid()
