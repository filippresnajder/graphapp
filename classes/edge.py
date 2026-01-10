from constants import EDGE_TAG, EDGE_LABEL_TAG

class Edge:
    identifier = 1
    def __init__(self, app, fill_color, box_color, text_color, width, weight, orientation, first_vertex, second_vertex):
        self.id = Edge.identifier
        self.app = app
        self.coords = (first_vertex.get_center_x(), first_vertex.get_center_y(), second_vertex.get_center_x(), second_vertex.get_center_y())
        self.line_color = fill_color
        self.box_color = box_color
        self.weight_color =  text_color
        self.width = width
        self.weight = weight
        self.orientation = orientation
        self.vertices = [first_vertex, second_vertex]
        self.canvas_object_id = self.app.canvas.create_line(first_vertex.get_center_x(), first_vertex.get_center_y(), second_vertex.get_center_x(), second_vertex.get_center_y(), fill=fill_color, width=width, tags=EDGE_TAG)
        self.canvas_text_bg = self.app.canvas.create_rectangle(self.get_center_x()-20, self.get_center_y()-20, self.get_center_x()+20, self.get_center_y()+20, fill="white", outline=box_color, tags=EDGE_LABEL_TAG)
        self.canvas_text = self.app.canvas.create_text(self.get_center_x(), self.get_center_y(), fill=text_color, text=self.weight, font=("Arial", 20), tags=EDGE_LABEL_TAG)
        self.app.update_layers()
        Edge.identifier += 1

    def get_center_x(self):
        return (self.coords[0] + self.coords[2]) / 2
    
    def get_center_y(self):
        return (self.coords[1] + self.coords[3]) / 2
    
    def update_position(self):
        x1 = self.vertices[0].get_center_x()
        y1 = self.vertices[0].get_center_y()
        x2 = self.vertices[1].get_center_x()
        y2 = self.vertices[1].get_center_y()

        self.coords = (x1, y1, x2, y2)

        self.app.canvas.coords(self.canvas_object_id, self.coords)

        nx = self.get_center_x()
        ny = self.get_center_y()

        nc = (nx-20, ny-20, nx+20, ny+20)
        self.app.canvas.coords(self.canvas_text_bg, nc)
        self.app.canvas.coords(self.canvas_text, nx, ny)
