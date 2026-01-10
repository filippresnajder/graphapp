class Vertex:
    identifier = 1
    def __init__(self, app, coords, color, width):
        self.app = app
        self.coords = coords
        self.id = Vertex.identifier
        self.tag = self.id
        self.color = color
        self.width = width
        self.neighbours = []
        self.canvas_object_id = self.app.canvas.create_oval(coords, fill=color, outline=color, width=width)
        self.canvas_text = self.app.canvas.create_text(self.get_center_x(), self.get_center_y(), fill="red", text=self.tag, font=("Arial", 20))
        Vertex.identifier += 1

    def is_clicked(self, x, y):
        return ((x >= self.coords[0] and x <= self.coords[2]) and (y >= self.coords[1] and y <= self.coords[3]))
    
    def get_center_x(self):
        return (self.coords[0] + self.coords[2]) / 2
    
    def get_center_y(self):
        return (self.coords[1] + self.coords[3]) / 2