"""Importovanie knižníc, ktoré použijeme."""
import tkinter as tk
import networkx as nx

from classes.button import Button
from classes.vertex import Vertex
from classes.edge import Edge
from classes.editmenu import EditMenu
from classes.algorithms import Algorithms
from constants import (RADIUS, DEFAULT_OUTLINE_COLOR, DEFAULT_FILL_COLOR, DEFAULT_BG_COLOR,
                       DEFAULT_TEXT_COLOR, DEFAULT_WIDTH, VERTEX_TAG, EDGE_TAG)


class App:
    def __init__(self):
        self.state = None
        self.zoom = 1
        self.selected_vertex = None
        self.vertices = []
        self.edges = []
        self.canvas_id_to_vertex = {}
        self.canvas_id_to_edge = {}
        self.root = tk.Tk()
        self.root.geometry("1280x720")
        self.root.title("GraphApp")
        self.root.config(background=DEFAULT_BG_COLOR)
        self.root.resizable(False, False)
        self.edit_menu = EditMenu(self)
        self.add_vertex_button = Button(self,"add_vertex","AV", 800, 20)
        self.add_vertex_button = Button(self,"move_vertex","MV", 850, 20)
        self.add_edge_button = Button(self,"add_edge", "AE", 900, 20)
        self.dijkstra = Button(self, "dijkstra", "DA", 950, 20)
        self.algorithms = Algorithms(self)
        self.canvas = tk.Canvas(self.root, width=1280, height=640, bg="white")
        self.canvas.place(x=0,y=80)
        self.canvas.tag_bind(VERTEX_TAG, "<Button-3>", self.edit_vertex)
        self.canvas.tag_bind(EDGE_TAG, "<Button-3>", self.edit_edge)
        self.root.bind("<r>", self.__reset_edge_colors)
        self.root.bind("<Control-d>", self.__remove_all_objects)
        self.root.bind("<Control-MouseWheel>", self.__zoom)
        self.root.mainloop()

    def create_vertex(self, event):
        if self.state != "add_vertex":
            return
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        vertex = Vertex(self, (x - (RADIUS * self.zoom), y - (RADIUS * self.zoom), x + (RADIUS * self.zoom), y + (RADIUS * self.zoom)),
                        DEFAULT_FILL_COLOR, DEFAULT_OUTLINE_COLOR, DEFAULT_TEXT_COLOR, DEFAULT_WIDTH)
        self.vertices.append(vertex)
        self.canvas_id_to_vertex[vertex.canvas_object_id] = vertex
        self.canvas_id_to_vertex[vertex.canvas_text] = vertex

    def create_edge(self, event):
        if self.state != "add_edge":
            return
           
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        result = self.__check_if_clicked_on_vertex(x, y)
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
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        result = self.__check_if_clicked_on_vertex(x, y)
        if result is None:
            return
        
        self.__reset_edge_colors(event)
        
        self.selected_vertex = None
        start_vertex, end_vertex = result

        G = self.build_nx_graph()
        dijkstra_result = nx.dijkstra_path(G, start_vertex.id, end_vertex.id)

        distances, previous = self.algorithms.dijkstra(start_vertex)
        path = self.algorithms.get_dijkstra_path(start_vertex, end_vertex, previous)
        own_res = [v.id for v in path]

        print(dijkstra_result == own_res)

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

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)    
    
        for vertex in self.vertices:
            if vertex.is_clicked(x, y):
                self.selected_vertex = vertex
                break

    def move_vertex(self, event):
        if self.selected_vertex is None:
            return
        new_x = self.canvas.canvasx(event.x)
        new_y = self.canvas.canvasy(event.y)

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

    def update_all_edges(self, line, box, text):
        for edge in self.edges:
            edge.update(edge.weight, line, box, text)

    def update_all_vertices(self, fill, outline, text):
        for vertex in self.vertices:
            vertex.update(str(vertex.tag), fill, outline, text)

    def __remove_all_objects(self, event):
        self.canvas.delete("all")
        self.edges.clear()
        self.vertices.clear()
        self.canvas_id_to_edge.clear()
        self.canvas_id_to_vertex.clear()
        Vertex.identifier = 1
        Edge.identifier = 1

    def __zoom(self, event):
        if event.delta > 0:
            factor = 1.05
        else:
            factor = 0.95
            
        new_zoom = self.zoom * factor

        if new_zoom > 2 or new_zoom < 0.4:
            return
        
        self.zoom = new_zoom
        self.canvas.scale("all", self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2, factor, factor)

        for vertex in self.vertices:
            vertex.coords = self.canvas.coords(vertex.canvas_object_id)


        