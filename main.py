import sys
from pathlib import Path
path = str(Path.cwd()) + "\code\\algorithms"
print(path)
sys.path.append(path)

from smartgrid import Smartgrid

class Main(object):
    def __init__(self):
        print(path)
        Smartgrid()

if __name__ == "__main__":
    Main()
