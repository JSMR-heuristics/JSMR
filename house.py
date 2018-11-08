class House(object):
    def __init__(self, x, y, output):
        self.x = int(x)
        self.y = int(y)
        self.output = output
        self.houses = {}
        self.dist = []

    def add_distance(self, dist_list):
        self.dist = dist_list
    # def add_house(self, ""):
    #     Smartgrid.houses["id"] = .....
    #
    # def move_house(self, id, to_coordinates):
    #     self.house[self.id].coordinates = self.to_coordinates
    #
    # def delete_house(self, id):
    #     del self.houses[self.id]
