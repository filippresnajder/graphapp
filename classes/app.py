"""Importovanie knižníc, ktoré použijeme."""
import tkinter as tk
import networkx as nx

from classes.button import Button
from classes.vertex import Vertex
from classes.edge import Edge
from classes.editmenu import EditMenu
from classes.algorithms import Algorithms
from constants import (RADIUS, DEFAULT_OUTLINE_COLOR, DEFAULT_FILL_COLOR, DEFAULT_BG_COLOR,
                       DEFAULT_TEXT_COLOR, DEFAULT_ALGORITHM_FILL, DEFAULT_WIDTH, VERTEX_TAG, EDGE_TAG)


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
        self.dijkstra_button = Button(self, "dijkstra", "DA", 950, 20)
        self.prim_button = Button(self, "prim", "PA", 1000, 20)
        self.kruskal_button = Button(self, "kruskal", "KA", 1050, 20)
        self.dfs_button = Button(self, "dfs", "DFS", 1100, 20)
        self.bfs_button = Button(self, "bfs", "BFS", 1150, 20)
        self.algorithms = Algorithms(self)
        self.algorithm_fill = DEFAULT_ALGORITHM_FILL
        self.canvas = tk.Canvas(self.root, width=1000, height=640, bg="white")
        self.canvas.place(x=280,y=80)
        self.canvas.tag_bind(VERTEX_TAG, "<Button-3>", self.edit_vertex)
        self.canvas.tag_bind(EDGE_TAG, "<Button-3>", self.edit_edge)
        self.root.bind("<r>", self.__reset_vertices_and_edges)
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

        self.edit_menu.render_add_edge_menu(event, start_vertex, end_vertex)

    def visualize_dijkstra(self,event):
        if self.state != "dijkstra":
            return
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        result = self.__check_if_clicked_on_vertex(x, y)
        if result is None:
            return
        
        self.__reset_vertices_and_edges(event)
        
        self.selected_vertex = None
        start_vertex, end_vertex = result

        nx_G = self.build_nx_graph()
        nx_res = nx.dijkstra_path(nx_G, start_vertex.id, end_vertex.id)
        own_res = self.algorithms.dijkstra(start_vertex, end_vertex)

        if nx_res != own_res:
            # TODO: Handle when test fails
            print(nx_res)
            print(own_res)
            return

        for edge in self.edges:
            edge_vertices_ids = [vertex.id for vertex in edge.vertices]
            for i in range(len(own_res)-1):
                if own_res[i] in edge_vertices_ids and own_res[i+1] in edge_vertices_ids:
                    self.canvas.itemconfig(edge.canvas_object_id, fill=self.algorithm_fill)

        self.state = None

    def visualize_prim(self, event):
        if self.state != "prim":
            return
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        result = self.__check_if_clicked_on_vertex(x, y)
        if result is None:
            return
        
        self.__reset_vertices_and_edges(event)

        self.selected_vertex = None
        start_vertex, _ = result

        mst_edges = self.algorithms.prim(start_vertex)
        nx_mst = nx.minimum_spanning_edges(self.build_nx_graph(), algorithm="prim", data=False)
        nx_edgelist = list(nx_mst)
        nx_sorted = sorted(sorted(e) for e in nx_edgelist)

        if (self.__mst_cost(nx_sorted) != self.__mst_cost(mst_edges)):
            # TODO: Handle when test fails
            return   

        for edge in self.edges:
            edge_ids = [v.id for v in edge.vertices]
            edge_ids_sorted = sorted(edge_ids)

            for mst_edge in mst_edges:
                if edge_ids_sorted == mst_edge:
                    self.canvas.itemconfig(edge.canvas_object_id, fill=self.algorithm_fill)
                    break

        self.state = None

    def visualize_kruskal(self):
        if self.state != "kruskal":
            return
        
        self.__reset_vertices_and_edges(None)
        mst_edges = self.algorithms.kruskal()
        nx_mst = nx.minimum_spanning_edges(self.build_nx_graph(), algorithm="kruskal", data=False)
        nx_edgelist = list(nx_mst)
        nx_sorted = sorted(sorted(e) for e in nx_edgelist)

        if (self.__mst_cost(nx_sorted) != self.__mst_cost(mst_edges)):
            # TODO: Handle when test fails
            return    

        mst_set = {frozenset(edge) for edge in mst_edges}
        for edge in self.edges:
            v1, v2 = edge.vertices
            if frozenset([v1.id, v2.id]) in mst_set:
                self.canvas.itemconfig(edge.canvas_object_id, fill=self.algorithm_fill)

        self.state = None

    def visualize_bfs(self, event):
        if self.state != "bfs":
            return
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        start_vertex = None

        for vertex in self.vertices:
            if vertex.is_clicked(x, y):
                start_vertex = vertex
                break

        if start_vertex is None:
            return
        
        self.__reset_vertices_and_edges(event)

        nx_G = self.build_nx_graph()
        nx_tree = nx.bfs_tree(nx_G, start_vertex.id)
        nx_edges = sorted(sorted(edge) for edge in nx_tree.edges())

        own_order, own_tree_edges = self.algorithms.bfs(start_vertex)
        own_sorted = sorted(sorted(edge) for edge in own_tree_edges)

        if nx_edges != own_sorted:
            # TODO: Handle when test fails - Fixnut zmeny hran
            print("nx:", nx_edges)
            print("own:", own_sorted)
            return

        for index, vertex_id in enumerate(own_order, start=1):
            for vertex in self.vertices:
                if vertex.id == vertex_id:
                    self.canvas.itemconfig(vertex.canvas_text, text=str(index), fill=self.algorithm_fill)

        self.state = None

    def visualize_dfs(self, event):
        if self.state != "dfs":
            return
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        start_vertex = None

        for vertex in self.vertices:
            if vertex.is_clicked(x, y):
                start_vertex = vertex
                break

        if start_vertex is None:
            return
        
        self.__reset_vertices_and_edges(event)

        nx_G = self.build_nx_graph()
        nx_tree = nx.dfs_tree(nx_G, start_vertex.id, sort_neighbors=sorted)
        nx_edges = {tuple(sorted(edge)) for edge in nx_tree.edges()}

        own_order, own_tree_edges = self.algorithms.dfs(start_vertex)
        own_edges = {tuple(sorted(edge)) for edge in own_tree_edges}

        if nx_edges != own_edges:
            # TODO: Handle when test fails - Fixnut zmeny hran
            print("nx:", nx_edges)
            print("own:", own_edges)
            return
        
        for index, vertex_id in enumerate(own_order, start=1):
            for vertex in self.vertices:
                if vertex.id == vertex_id:
                    self.canvas.itemconfig(vertex.canvas_text, text=str(index), fill=self.algorithm_fill)

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
        oriented = False

        for edge in self.edges:
            if edge.orientation == "yes":
                oriented = True
                break
        
        G = nx.DiGraph() if oriented else nx.Graph()

        for edge in self.edges:
            v1, v2 = edge.vertices
            if edge.orientation == "yes":
                G.add_edge(v1.id, v2.id, weight=edge.weight)
            else:
                G.add_edge(v1.id, v2.id, weight=edge.weight)
                G.add_edge(v2.id, v1.id, weight=edge.weight)

        return G
    
    def __reset_vertices_and_edges(self, event):
        for vertex in self.vertices:
            self.canvas.itemconfig(vertex.canvas_object_id, fill=vertex.fill_color, outline=vertex.outline_color)
            self.canvas.itemconfig(vertex.canvas_text, fill=vertex.text_color, text=vertex.tag)
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

    def __mst_cost(self, edges):
        cost = 0
        for u,v in edges:
            for edge in self.edges:
                ids = sorted([edge.vertices[0].id, edge.vertices[1].id])
                if ids == [u,v]:
                    cost += edge.weight
        return cost


        