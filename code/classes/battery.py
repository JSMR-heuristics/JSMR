class Battery(object):

    """This represents every battery that is created in the program"""

    def __init__(self, capacity, x, y, colour):
        self.capacity = float(capacity)
        self.x = int(x)
        self.y = int(y)
        self.colour = colour
        self.linked_houses = []


    # returns a boolean corresponding to whether max capacity is reached or not
    def full(self):
        sum = 0.00
        for i in self.linked_houses:
            sum += i.output
        if self.capacity < sum:
            return True
        else:
            return False


    # current house input
    def filled(self):
        sum = 0.00
        for j in self.linked_houses:
            sum += j.output
        return sum
