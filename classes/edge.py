import tkinter as tk

class Edge:
    identifier = 1
    def __init__(self, app, color, width, weight, orientation, first_vertex, second_vertex):
        self.id = Edge.identifier
        self.app = app
        self.coords = (first_vertex.get_center_x(), first_vertex.get_center_y(), second_vertex.get_center_x(), second_vertex.get_center_y())
        self.color = color
        self.width = width
        self.weight = weight
        self.orientation = orientation
        self.vertices = [first_vertex, second_vertex]
        self.canvas_object_id = self.app.canvas.create_line(first_vertex.get_center_x(), first_vertex.get_center_y(), second_vertex.get_center_x(), second_vertex.get_center_y(), fill=color, width=width)
        self.canvas_text = self.app.canvas.create_text(self.get_center_x(), self.get_center_y(), fill="red", text=self.weight, font=("Arial", 20))
        Edge.identifier += 1

    def get_center_x(self):
        return (self.coords[0] + self.coords[2]) / 2
    
    def get_center_y(self):
        return (self.coords[1] + self.coords[3]) / 2