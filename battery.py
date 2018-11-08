class Battery(object):

    def __init__(self, capacity, x, y, colour):
        self.capacity = capacity
        self.full = False
        self.x = int(x)
        self.y = int(y)
        self.colour = colour
        self.linked_houses = []
        # latere opdrachten de prijs


    # Later in de opdracht functies als add_battery en move battery er bij
