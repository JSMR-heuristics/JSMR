class Battery(object):

    def __init__(self, capacity, x, y):
        self.capacity = capacity
        self.x = int(x)
        self.y = int(y)
        self.full = False

        # dict met de huizen die verbonden zijn
        self.linked_houses = []
        # latere opdrachten de prijs


    # Later in de opdracht functies als add_battery en move battery er bij
