class Battery(object):
    """Battery objects defined here.

    Battery objects have the following attributes:
    - x and y coordinates
    - A color, to distiguish which cable runs to which battery
    - Capacity of the battery
    - Which houses are linked to the battery

    Methods full and filled are described in method docstrings.
    """

    """This represents every battery that is created in the program"""

    def __init__(self, capacity, x, y, colour):
        self.capacity = float(capacity)
        self.x = int(x)
        self.y = int(y)
        self.colour = colour
        self.linked_houses = []


    def full(self):
        """Return true if 1 or more batteries are over capacity."""
        sum = 0.00
        for i in self.linked_houses:
            sum += i.output
        if self.capacity < sum:
            return True
        else:
            return False


    def filled(self):
        """Return total input of battery."""
        sum = 0.00
        for j in self.linked_houses:
            sum += j.output
        return sum
