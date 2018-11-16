class House(object):
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

    # def add_distance(self, dist_list):
    #     self.dist = dist_list
    # def add_house(self, ""):
    #     Smartgrid.houses["id"] = .....
    #
    # def move_house(self, id, to_coordinates):
    #     self.house[self.id].coordinates = self.to_coordinates
    #
    # def delete_house(self, id):
    #     del self.houses[self.id]
