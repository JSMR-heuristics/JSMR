class House(object):

    """This represents every house that is created in the program"""

    def __init__(self, x, y, output):
        # Coordinates of the house instance
        self.x = int(x)
        self.y = int(y)

        # output of the house instance
        self.output = float(output)

        # to which battery is the house currently connected
        self.link = []

        # the differences in distance between the closest Battery
        # and the other batteries
        self.diffs = {}

        # {0: 51, 1: 40, etc}
        self.dists = {}

        self.filtered = []



    def filter(self):
        """A simple method that turns self.diffs, a dictionary countaining the
        available batteries as keys, and their respective distances to the
        house as values, in order of that distance (small to large)
        an iterable list"""
        
        for key in self.diffs:
            self.filtered.append(key)
            if len(self.filtered) == 4:
                return
