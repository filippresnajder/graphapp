"""Importovanie knižníc, ktoré použijeme."""
import tkinter as tk
import networkx as nx

from classes.button import Button
from classes.vertex import Vertex
from classes.editmenu import EditMenu
from constants import (RADIUS, DEFAULT_OUTLINE_COLOR, DEFAULT_FILL_COLOR, DEFAULT_BG_COLOR,
                       DEFAULT_TEXT_COLOR, DEFAULT_WIDTH, VERTEX_TAG, EDGE_TAG)


class App:
    def __init__(self):
        self.state = None
        self.selected_vertex = None
        self.vertices = []
        self.edges = []
        self.root = tk.Tk()
        self.root.geometry("1280x720")
        self.root.title("GraphApp")
        self.root.config(background=DEFAULT_BG_COLOR)
        self.root.resizable(False, False)
        self.root.bind("<r>", self.__reset_edge_colors)
        self.edit_menu = EditMenu(self)
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

        self.edit_menu.render_add_edge_menu(event, start_vertex, end_vertex)

    def visualize_dijkstra(self,event):
        if self.state != "dijkstra":
            return
        
        result = self.__check_if_clicked_on_vertex(event.x, event.y)
        if result is None:
            return
        
        self.__reset_edge_colors(event)
        
        self.selected_vertex = None
        start_vertex, end_vertex = result

        G = self.build_nx_graph()
        dijkstra_result = nx.dijkstra_path(G, start_vertex.id, end_vertex.id)
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
    
    def start_move_vertex(self, event) -> None:
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

        self.edit_menu.render_vertex_edit_menu(event, vertex)
    
    def edit_edge(self, event):
        self.state = None

        item_id = self.canvas.find_withtag("current")[0]
        edge = self.canvas_id_to_edge[item_id]

        self.edit_menu.render_edge_edit_menu(event, edge)
    
    def update_layers(self):
        """Aktualizácie vrstiev po pridaní hrany."""
        self.canvas.tag_lower("edge")
        self.canvas.tag_raise("vertex")
        self.canvas.tag_raise("edge_label")

    def build_nx_graph(self):
        G = nx.Graph()

        for edge in self.edges:
            v1, v2 = edge.vertices
            G.add_edge(v1.id, v2.id, weight=edge.weight)

        return G
    
    def __reset_edge_colors(self, event):
        for edge in self.edges:
            self.canvas.itemconfig(edge.canvas_object_id, fill=edge.line_color)

        