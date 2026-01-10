import tkinter as tk
import random
import networkx as nx
from classes.button import Button
from classes.vertex import Vertex
from classes.edge import Edge

RADIUS = 10
DEFAULT_COLOR = "black"
DEFAULT_WIDTH = 4
DEFAULT_WEIGHT = 0

class App:
    def __init__(self):
        self.state = None
        self.selected_vertex = None
        self.graph = nx.Graph()
        self.vertices = []
        self.edges = []
        self.canvas_object_ids = []
        self.root = tk.Tk()
        self.root.geometry("1280x720")
        self.root.title("GraphApp")
        self.add_vertex_button = Button(self,"add_vertex","Add Vertex", 800, 20)
        self.add_edge_button = Button(self,"add_edge", "Add Edge", 920, 20)
        self.test_dijkstra_button = Button(self,"dijkstra", "Dijkstra Algorithm", 1030, 20)
        self.canvas = tk.Canvas(self.root, width=1280, height=640, bg="white")
        self.canvas.place(x=0,y=80)
        self.root.mainloop()

    def create_vertex(self, event):
        if self.state != "add_vertex":
            return
        
        vertex = Vertex(self, (event.x - RADIUS, event.y - RADIUS, event.x + RADIUS, event.y + RADIUS), DEFAULT_COLOR, DEFAULT_WIDTH)
        self.vertices.append(vertex)
        self.canvas_object_ids.append(vertex.canvas_object_id)

    def create_edge(self, event):
        if self.state != "add_edge":
            return
           
        result = self.__check_if_clicked_on_vertex(event.x, event.y)
        if result is None:
            return
        
        self.selected_vertex = None
        start_vertex, end_vertex = result

        start_vertex.neighbours.append(end_vertex)
        end_vertex.neighbours.append(start_vertex)

        edge = Edge(self, DEFAULT_COLOR, DEFAULT_WIDTH, random.randint(1,10), "none", start_vertex, end_vertex)
        self.edges.append(edge)
        self.canvas_object_ids.append(edge.canvas_object_id)
        self.graph.add_edge(start_vertex.id, end_vertex.id, weight=edge.weight)

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
        