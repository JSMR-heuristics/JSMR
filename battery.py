class Battery(object):

    def __init__(self, capacity, x, y, colour):
        self.capacity = float(capacity)
        self.x = int(x)
        self.y = int(y)
        self.colour = colour
        self.linked_houses = []
        # latere opdrachten de prijs


    def full(self):
        sum = 0.00
        for j in self.linked_houses:
            sum += j.output
        if self.capacity < sum:
            return True
        else:
            return False


    def filled(self):
        sum = 0.00
        for j in self.linked_houses:
            sum += j.output
        return sum





    # Later in de opdracht functies als add_battery en move battery er bij
