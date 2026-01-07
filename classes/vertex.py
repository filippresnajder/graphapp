class Vertex:
    identifier = 1
    def __init__(self, app, coords, color):
        self.app = app
        self.coords = coords
        self.id = Vertex.identifier
        self.tag = self.id
        self.color = color
        self.neighbours = []
        Vertex.identifier += 1

    def is_clicked(self, x, y):
        if (x >= self.coords[0] and x <= self.coords[2]) and (y >= self.coords[1] and y <= self.coords[3]):
            return True
        return False
    
    def get_center_x(self):
        return (self.coords[0] + self.coords[2]) / 2
    
    def get_center_y(self):
        return (self.coords[1] + self.coords[3]) / 2