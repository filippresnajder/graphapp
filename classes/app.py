import tkinter as tk
from classes.button import Button
from classes.vertex import Vertex

RADIUS = 10
DEFAULT_COLOR = "black"
DEFAULT_WIDTH = 4

class App:
    def __init__(self):
        self.state = None
        self.selected_vertex = None
        self.vertices = []
        self.edges = []
        self.root = tk.Tk()
        self.root.geometry("1280x720")
        self.root.title("GraphApp")
        self.add_vertex_button = Button(self,"add_vertex","Add Vertex", 1000, 20)
        self.add_edge_button = Button(self,"add_edge", "Add Edge", 1120, 20)
        self.canvas = tk.Canvas(self.root, width=1280, height=640, bg="white")
        self.canvas.place(x=0,y=80)
        self.root.mainloop()

    def create_vertex(self, event):
        if self.state is not "add_vertex":
            return
        
        vertex = Vertex(self, (event.x - RADIUS, event.y - RADIUS, event.x + RADIUS, event.y + RADIUS), DEFAULT_COLOR)
        self.canvas.create_oval(vertex.coords, fill=DEFAULT_COLOR, outline=DEFAULT_COLOR, width=DEFAULT_WIDTH)
        self.vertices.append(vertex)

    def create_edge(self, event):
        if self.state is not "add_edge":
            return
           
        result = self.__check_if_clicked_on_vertex(event.x, event.y)
        if result is None:
            return
        
        self.selected_vertex = None
        start_vertex, end_vertex = result

        start_vertex.neighbours.append(end_vertex)
        end_vertex.neighbours.append(start_vertex)

        self.canvas.create_line(start_vertex.get_center_x(), start_vertex.get_center_y(), end_vertex.get_center_x(), end_vertex.get_center_y(), fill=DEFAULT_COLOR, width=DEFAULT_WIDTH)

    def __check_if_clicked_on_vertex(self, x, y):
        for vertex in self.vertices:
            if vertex.is_clicked(x,y):
                if self.selected_vertex is None:
                    self.selected_vertex = vertex
                else:
                    start_vertex = self.selected_vertex
                    end_vertex = vertex
                    return (start_vertex, end_vertex)
        return None
        