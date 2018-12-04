import sys
from pathlib import Path
import os
cwd = os.getcwd()
path = os.path.join(*[cwd, 'code', 'algorithms'])
sys.path.append(path)

from smartgrid import Smartgrid

class Main(object):
    def __init__(self):
        Smartgrid()


if __name__ == "__main__":
    Main()
