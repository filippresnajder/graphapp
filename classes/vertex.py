from constants import VERTEX_TAG, RADIUS

class Vertex:
    identifier = 1
    def __init__(self, app, coords, fill_color, outline_color, text_color, width):
        self.app = app
        self.coords = coords
        self.id = Vertex.identifier
        self.tag = self.id
        self.fill_color = fill_color
        self.outline_color = outline_color
        self.text_color = text_color
        self.width = width
        self.neighbours = []
        self.edges = []
        self.canvas_object_id = self.app.canvas.create_oval(coords, fill=self.fill_color, outline=self.outline_color, width=width, tags=VERTEX_TAG)
        self.canvas_text = self.app.canvas.create_text(self.get_center_x(), self.get_center_y(), fill=self.text_color, text=self.tag, font=("Arial", 20), tags=VERTEX_TAG)
        Vertex.identifier += 1

    def is_clicked(self, x, y):
        return ((x >= self.coords[0] and x <= self.coords[2]) and (y >= self.coords[1] and y <= self.coords[3]))
    
    def get_center_x(self):
        return (self.coords[0] + self.coords[2]) / 2
    
    def get_center_y(self):
        return (self.coords[1] + self.coords[3]) / 2
    
    def move_to(self, nx, ny):
        self.coords = (nx-RADIUS, ny-RADIUS, nx+RADIUS, ny+RADIUS)
        self.app.canvas.coords(self.canvas_object_id, self.coords)
        self.app.canvas.coords(self.canvas_text, nx, ny)

        for edge in self.edges:
            if self in edge.vertices:
                edge.update_position()