import tkinter as tk
import math
from constants import EDGE_TAG, EDGE_LABEL_TAG, BOX_SIZE, RADIUS

# TODO: FIX Overlapping edges after removal when creating new ones
# TODO: Create Edges going to self
# TODO: Fix algorithms coloring all edges in multigraphs

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
        self.curve_offset = self.__calculate_initial_offset()
        self.canvas_object_id = self.__create_line(orientation)
        self.canvas_text_bg = self.app.canvas.create_rectangle(self.get_center_x()-BOX_SIZE, self.get_center_y()-BOX_SIZE, self.get_center_x()+BOX_SIZE, self.get_center_y()+BOX_SIZE, fill="white", outline=box_color, tags=EDGE_LABEL_TAG)
        self.canvas_text = self.app.canvas.create_text(self.get_center_x(), self.get_center_y(), fill=text_color, text=self.weight, font=("Arial", 12), tags=EDGE_LABEL_TAG)
        self.app.update_layers()
        self.update_position()
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
        
        points = self.__calculate_curve_points(x1, y1, x2, y2)
        self.app.canvas.coords(self.canvas_object_id, points)

        weight_label_x, weight_label_y = self.__get_curve_midpoint(points)
        self.app.canvas.coords(self.canvas_text_bg, weight_label_x - BOX_SIZE, weight_label_y - BOX_SIZE, weight_label_x + BOX_SIZE, weight_label_y + BOX_SIZE)
        self.app.canvas.coords(self.canvas_text, weight_label_x, weight_label_y)

    def __create_line(self, orientation):
        arrow = tk.LAST if orientation == "yes" else None
        return self.app.canvas.create_line(
            0, 0, 0, 0,
            fill=self.line_color,
            width=self.width,
            tags=EDGE_TAG,
            arrow=arrow,
            smooth=True
        )  

    def __calculate_initial_offset(self):
        parallel = [e for e in self.app.edges if set(e.vertices) == set(self.vertices)]

        if not parallel:
            return 0
        
        offset_step = 50
        same_type_count = sum(1 for e in parallel[1:] if e.orientation == self.orientation)
        
        return (same_type_count + 1) * offset_step

    def __calculate_curve_points(self, x1, y1, x2, y2):
        if self.curve_offset == 0:
            return (x1, y1, x2, y2)

        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            return (x1, y1, x2, y2)

        nx = -dy / length
        ny = dx / length

        offset = self.curve_offset
        if self.orientation == "yes":  
            cx = (x1 + x2) / 2 + nx * offset
            cy = (y1 + y2) / 2 + ny * offset
        else:
            cx = (x1 + x2) / 2 - nx * offset
            cy = (y1 + y2) / 2 - ny * offset

        return (x1, y1, cx, cy, x2, y2)

    def __get_curve_midpoint(self, points):
        if len(points) == 4:
            return (points[0] + points[2]) / 2, (points[1] + points[3]) / 2
        else:
            x0, y0, cx, cy, x2, y2 = points
            t = 0.5
            x = (1 - t)**2 * x0 + 2 * (1 - t) * t * cx + t**2 * x2
            y = (1 - t)**2 * y0 + 2 * (1 - t) * t * cy + t**2 * y2

            return x, y
    
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

        for e in self.app.edges:
            if (set(e.vertices) == set(self.vertices) and
                e.orientation == self.orientation and
                e.curve_offset > self.curve_offset 
            ):
                e.curve_offset -= 50
                e.update_position()

        for cid in (
            self.canvas_object_id,
            self.canvas_text,
            self.canvas_text_bg
        ):
            self.app.canvas_id_to_edge.pop(cid, None)