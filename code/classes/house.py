class House(object):
    """House objects defined here.

    House objects have the following attributes:
    - x and y coordinates (int)
    - Output of the house (float)
    - house.link is a battery object, to which the house is linked
    - house.diffs: differences in distace to each battery (dict)
    - house.dist: absolute distance to each battery (dict)

    Method filtered is described in method docstring.
    """
    
    def __init__(self, x, y, output):
        self.x = int(x)
        self.y = int(y)
        self.output = float(output)
        self.link = []
        self.diffs = {}
        self.dists = {}
        self.filtered = []

    def filter(self):
        for key in self.diffs:
            self.filtered.append(key)
            if len(self.filtered) == 4:
                return
