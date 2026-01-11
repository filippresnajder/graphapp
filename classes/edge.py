import tkinter as tk
import math
from constants import EDGE_TAG, EDGE_LABEL_TAG, BOX_SIZE, RADIUS

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
        self.canvas_object_id = self.__create_line(orientation, first_vertex, second_vertex)
        self.canvas_text_bg = self.app.canvas.create_rectangle(self.get_center_x()-BOX_SIZE, self.get_center_y()-BOX_SIZE, self.get_center_x()+BOX_SIZE, self.get_center_y()+BOX_SIZE, fill="white", outline=box_color, tags=EDGE_LABEL_TAG)
        self.canvas_text = self.app.canvas.create_text(self.get_center_x(), self.get_center_y(), fill=text_color, text=self.weight, font=("Arial", 12), tags=EDGE_LABEL_TAG)
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

        if self.orientation == "yes":
            x2, y2 = self.__calculate_position_with_arrow(self.vertices[0], self.vertices[1])

        self.coords = (x1, y1, x2, y2)

        self.app.canvas.coords(self.canvas_object_id, self.coords)

        nx = self.get_center_x()
        ny = self.get_center_y()

        nc = (nx-BOX_SIZE, ny-BOX_SIZE, nx+BOX_SIZE, ny+BOX_SIZE)
        self.app.canvas.coords(self.canvas_text_bg, nc)
        self.app.canvas.coords(self.canvas_text, nx, ny)

    def __create_line(self, orientation, v1, v2):
        if orientation == "yes":
            x2n, y2n = self.__calculate_position_with_arrow(v1, v2)
            return self.app.canvas.create_line(v1.get_center_x(), v1.get_center_y(), x2n, y2n, fill=self.line_color, width=self.width, tags=EDGE_TAG, arrow=tk.LAST)

        return self.app.canvas.create_line(v1.get_center_x(), v1.get_center_y(), v2.get_center_x(), v2.get_center_y(), fill=self.line_color, width=self.width, tags=EDGE_TAG)
    
    def __calculate_position_with_arrow(self, v1, v2):
        dx = v2.get_center_x() - v1.get_center_x()
        dy = v2.get_center_y() - v1.get_center_y()
        length = math.hypot(dx, dy)

        if length != 0:
            dx /= length
            dy /= length

        x2_new = v2.get_center_x() - dx * RADIUS
        y2_new = v2.get_center_y() - dy * RADIUS

        return (x2_new, y2_new)
    
    def update(self, weight, line, box, text):
        try:
            self.weight = int(weight)
        except ValueError:
            return "weight-error"
        self.line_color, self.box_color, self.weight_color = line, box, text
        self.app.canvas.itemconfig(self.canvas_object_id, fill=self.line_color)
        self.app.canvas.itemconfig(self.canvas_text_bg, outline=self.box_color)
        self.app.canvas.itemconfig(self.canvas_text, fill=self.weight_color, text=self.weight)      

    def delete(self):
        self.app.canvas.delete(self.canvas_object_id)
        self.app.canvas.delete(self.canvas_text_bg)
        self.app.canvas.delete(self.canvas_text)
        self.app.edges.remove(self)
        for v in self.vertices:
            if self in v.edges:
                v.edges.remove(self)
        for cid in (
            self.canvas_object_id,
            self.canvas_text,
            self.canvas_text_bg
        ):
            self.app.canvas_id_to_edge.pop(cid, None)