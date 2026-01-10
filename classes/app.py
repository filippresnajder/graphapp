import tkinter as tk
import random
import networkx as nx

from tkinter import colorchooser
from classes.button import Button
from classes.vertex import Vertex
from classes.edge import Edge
from constants import RADIUS, DEFAULT_OUTLINE_COLOR, DEFAULT_FILL_COLOR, DEFAULT_TEXT_COLOR, DEFAULT_WIDTH, VERTEX_TAG, EDGE_TAG

class App:
    def __init__(self):
        self.state = None
        self.selected_vertex = None
        self.graph = nx.Graph()
        self.vertices = []
        self.edges = []
        self.root = tk.Tk()
        self.root.geometry("1280x720")
        self.root.title("GraphApp")
        self.add_vertex_button = Button(self,"add_vertex","AV", 800, 20)
        self.add_vertex_button = Button(self,"move_vertex","MV", 850, 20)
        self.add_edge_button = Button(self,"add_edge", "AE", 900, 20)
        self.dijkstra = Button(self, "dijkstra", "DA", 950, 20)
        self.canvas = tk.Canvas(self.root, width=1280, height=640, bg="white")
        self.canvas.place(x=0,y=80)
        self.canvas.tag_bind(VERTEX_TAG, "<Button-3>", self.edit_vertex)
        self.canvas.tag_bind(EDGE_TAG, "<Button-3>", self.edit_edge)
        self.canvas_id_to_vertex = {}
        self.canvas_id_to_edge = {}
        self.root.mainloop()

    def create_vertex(self, event):
        if self.state != "add_vertex":
            return
        
        vertex = Vertex(self, (event.x - RADIUS, event.y - RADIUS, event.x + RADIUS, event.y + RADIUS), DEFAULT_FILL_COLOR, DEFAULT_OUTLINE_COLOR, DEFAULT_TEXT_COLOR, DEFAULT_WIDTH)
        self.vertices.append(vertex)
        self.canvas_id_to_vertex[vertex.canvas_object_id] = vertex
        self.canvas_id_to_vertex[vertex.canvas_text] = vertex

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

        edge = Edge(self, DEFAULT_OUTLINE_COLOR, DEFAULT_OUTLINE_COLOR, DEFAULT_TEXT_COLOR, DEFAULT_WIDTH, random.randint(1,10), "none", start_vertex, end_vertex)
        self.edges.append(edge)
        start_vertex.edges.append(edge)
        end_vertex.edges.append(edge)
        self.graph.add_edge(start_vertex.id, end_vertex.id, weight=edge.weight)
        self.canvas_id_to_edge[edge.canvas_object_id] = edge
        self.canvas_id_to_edge[edge.canvas_text] = edge
        self.canvas_id_to_edge[edge.canvas_text_bg] = edge

    def visualize_dijkstra(self,event):
        if self.state != "dijkstra":
            return
        
        result = self.__check_if_clicked_on_vertex(event.x, event.y)
        if result is None:
            return
        
        self.selected_vertex = None
        start_vertex, end_vertex = result
        
        dijkstra_result = nx.dijkstra_path(self.graph, start_vertex.id, end_vertex.id)
        for edge in self.edges:
            edge_vertices_ids = [vertex.id for vertex in edge.vertices]
            for i in range(len(dijkstra_result)-1):
                if dijkstra_result[i] in edge_vertices_ids and dijkstra_result[i+1] in edge_vertices_ids:
                    self.canvas.itemconfig(edge.canvas_object_id, fill="yellow")

        self.state = None

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
    
    def start_move_vertex(self, event):
        if self.state != "move_vertex":
            return
        
        for vertex in self.vertices:
            if vertex.is_clicked(event.x, event.y):
                self.selected_vertex = vertex
                break

    def move_vertex(self, event):
        if self.selected_vertex is None:
            return
        
        new_x = event.x
        new_y = event.y

        self.selected_vertex.move_to(new_x, new_y)

    def stop_move_vertex(self, event):
        self.selected_vertex = None

    def edit_vertex(self, event):
        self.state = None

        item_id = self.canvas.find_withtag("current")[0]
        vertex = self.canvas_id_to_vertex[item_id]

        popup = tk.Toplevel(self.root)
        popup.title("Edit Menu")
        popup.geometry("200x350+{}+{}".format(event.x_root, event.y_root))

        tk.Label(popup, text="Change Vertex Name:").pack(pady=5)
        entry = tk.Entry(popup)
        entry.insert(0, str(vertex.tag))
        entry.pack(padx=2)

        def change_color(type):
            color = colorchooser.askcolor()[1]
            if type == "fill":
                change_fill_color_label["text"] = color
                change_fill_color_label["bg"] = color
            if type == "outline":
                change_outline_color_label["text"] = color
                change_outline_color_label["bg"] = color
            if type == "text":
                change_text_color_label["text"] = color
                change_text_color_label["bg"] = color

        change_fill_color = tk.Button(popup, text="Change Fill Color", command=lambda: change_color("fill"))
        change_fill_color.pack(pady=5)

        change_fill_color_label = tk.Label(popup, text=vertex.fill_color, bg=vertex.fill_color)
        change_fill_color_label.pack(pady=1)

        change_outline_color = tk.Button(popup, text="Change Outline Color", command=lambda: change_color("outline"))
        change_outline_color.pack(pady=5)

        change_outline_color_label = tk.Label(popup, text=vertex.outline_color, bg=vertex.outline_color)
        change_outline_color_label.pack(pady=1)

        change_text_color = tk.Button(popup, text="Change Text Color", command=lambda: change_color("text"))
        change_text_color.pack(pady=5)

        change_text_color_label = tk.Label(popup, text=vertex.text_color, bg=vertex.text_color)
        change_text_color_label.pack(pady=1)

        def save():
            vertex.tag = entry.get()
            vertex.fill_color, vertex.outline_color, vertex.text_color = change_fill_color_label["text"], change_outline_color_label["text"], change_text_color_label["text"]
            self.canvas.itemconfig(vertex.canvas_object_id, fill=vertex.fill_color, outline=vertex.outline_color)
            self.canvas.itemconfig(vertex.canvas_text, fill=vertex.text_color, text=vertex.tag)
            popup.destroy()

        tk.Button(popup, text="Save", command=save).pack(pady=10)    
    
    def edit_edge(self, event):
        print(self.canvas_id_to_edge)
    
    def update_layers(self):
        self.canvas.tag_lower("edge")
        self.canvas.tag_raise("vertex")
        self.canvas.tag_raise("edge_label")

        