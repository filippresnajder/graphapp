import tkinter as tk
import networkx as nx

class Button:
    def __init__(self, app, btn_type, label, x, y):
        self.app = app
        self.btn_type = btn_type
        self.label = label
        self.x = x
        self.y = y
        self.button = tk.Button(self.app.root, text=self.label, font=("Arial", 16), command=self.onclick)
        self.button.place(x=self.x, y=self.y)

    def onclick(self):
        self.app.state = self.btn_type
        print("state set to", self.btn_type)
        if (self.app.state == "add_vertex"):
            self.app.canvas.bind("<Button-1>", self.app.create_vertex)
        elif (self.app.state == "add_edge"):
            self.app.canvas.bind("<Button-1>", self.app.create_edge)
        elif (self.app.state == "dijkstra"):
            result = nx.dijkstra_path(self.app.graph, 1, 6)
            for edge in self.app.edges:
                edge_vertices_ids = [vertex.id for vertex in edge.vertices]
                for i in range(len(result)-1):
                    if result[i] in edge_vertices_ids and result[i+1] in edge_vertices_ids:
                        self.app.canvas.itemconfig(edge.canvas_object_id, fill="blue")