"""Importovanie knižníc, ktoré použijeme."""
import tkinter as tk
from tkinter import filedialog
import json
import re
import os
import random
import copy
import networkx as nx

from classes.vertex import Vertex
from classes.edge import Edge
from classes.editmenu import EditMenu
from classes.algorithms import Algorithms
from classes.mainframe import MainFrame
from classes.autotest import Autotest
from constants import (RADIUS, DEFAULT_OUTLINE_COLOR, DEFAULT_FILL_COLOR, DEFAULT_BG_COLOR,
                       DEFAULT_TEXT_COLOR, DEFAULT_ALGORITHM_FILL, DEFAULT_ALGORITHM_NOT_FOCUSED,
                       DEFAULT_ALGORITHM_NOT_SELECTED, DEFAULT_ALGORITHM_TEXT_FILL,
                       DEFAULT_WIDTH)

# TODO: Implement test section
# TODO: Write info about algorithms in algorithm info

# LATER TODO: Zdroje k pseudokodom

class App:
    """Trieda reprezentujúca aplikáciu"""

    def __init__(self):
        self.state = None
        self.selected_vertex = None
        self.zoom = 1
        self.vertices = []
        self.edges = []
        self.algorithm_state = {
            "index": None,
            "steps": [],
            "is_bfs_or_dfs": False
        }
        self.canvas_id_to_vertex = {}
        self.canvas_id_to_edge = {}
        self.root = tk.Tk()
        self.root.geometry("1280x720")
        self.root.title("GraphApp")
        self.root.config(background=DEFAULT_BG_COLOR)
        self.root.resizable(False, False)
        self.edit_menu = EditMenu(self)
        self.algorithms = Algorithms(self)
        self.root.bind("<Button-1>", self.__global_click_dropdown_close, add="+")
        self.root.bind("<r>", self.reset_vertices_and_edges)
        self.root.bind("<Control-d>", self.__remove_all_objects)
        self.root.bind("<Control-MouseWheel>", self.__zoom)
        self.main_view = MainFrame(self)
        self.autotest_view = Autotest(self)
        self.views = {
            "main": self.main_view,
            "test": self.autotest_view
        }
        self.current_view = None
        self.load_view("main")
        self.root.mainloop()

    def create_vertex(self, event):
        """Metóda slúžiaca na vytvorenie vrcholu na plátno"""

        if self.state != "add_vertex":
            return

        x = self.main_view.canvas.canvasx(event.x)
        y = self.main_view.canvas.canvasy(event.y)

        vertex = Vertex(self, 
                        (x - (RADIUS * self.zoom), y - (RADIUS * self.zoom),
                        x + (RADIUS * self.zoom), y + (RADIUS * self.zoom)),
                        DEFAULT_FILL_COLOR,
                        DEFAULT_OUTLINE_COLOR,
                        DEFAULT_TEXT_COLOR,
                        DEFAULT_WIDTH)
        self.vertices.append(vertex)
        self.canvas_id_to_vertex[vertex.canvas_object_id] = vertex
        self.canvas_id_to_vertex[vertex.canvas_text] = vertex

        if self.algorithm_state["steps"]:
            self.main_view.infobox.clear()
            self.main_view.infobox.log("Nastala zmena v grafe, mažem pamäť krokov predošlého algoritmu")
            self.reset_vertices_and_edges(event=None)
        self.clear_algorithm_state()

    def create_edge(self, event):
        """Metóda slúžiaca na vytvorenie hrany"""

        if self.state != "add_edge":
            return
           
        x = self.main_view.canvas.canvasx(event.x)
        y = self.main_view.canvas.canvasy(event.y)

        result = self.__check_if_clicked_on_vertex(x, y)
        if result is None:
            return

        self.selected_vertex = None
        start_vertex, end_vertex = result

        self.edit_menu.render_add_edge_menu(event, start_vertex, end_vertex)

        if self.algorithm_state["steps"]:
            self.main_view.infobox.clear()
            self.main_view.infobox.log("Nastala zmena v grafe, mažem pamäť krokov predošlého algoritmu")
            self.reset_vertices_and_edges(event=None)
        self.clear_algorithm_state()

    def visualize_dijkstra(self,event):
        """Metóda slúžiaca na vizualizovanie Dijkstrovho algoritmu"""

        if self.state != "dijkstra":
            self.state = None
            return
        
        self.clear_algorithm_state()

        x = self.main_view.canvas.canvasx(event.x)
        y = self.main_view.canvas.canvasy(event.y)
        result = self.__check_if_clicked_on_vertex(x, y)
        if result is None:
            return
        
        self.reset_vertices_and_edges(event)
        self.selected_vertex = None
        start_vertex, end_vertex = result

        nx_g = self.build_nx_graph()

        own_result = self.algorithms.dijkstra(start_vertex, end_vertex)
        if not own_result:
            return

        own_res, path_tag, edge_objects, logs, edge_logs, vertices_logs = own_result

        try:
            nx_res = nx.dijkstra_path(nx_g, start_vertex.id, end_vertex.id)
        except nx.NetworkXException as e:
            self.main_view.infobox.clear()
            self.main_view.infobox.log(f"Chyba: {str(e)}")
            return
        
        self.main_view.infobox.log("Algoritmus úspešne prebehol")
        self.main_view.infobox.log("Porovnávam výsledky z algoritmu s výsledkami z NetworkX")

        if nx_res != own_res:
            self.main_view.infobox.clear()
            self.main_view.infobox.log("Zlyhanie testu, výstupné údaje nesedia")
            self.main_view.infobox.log(f"NetworkX výsledok: {nx_res}")
            self.main_view.infobox.log(f"Vlastný výsledok: {own_res}")
            return
        
        self.main_view.infobox.log(f"Výsledky sedia - cesta {path_tag}")
        self.main_view.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu.")

        for edge in self.edges:
            if edge in edge_objects:
                v1, v2 = edge.vertices
                self.main_view.canvas.itemconfig(edge.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)
                self.main_view.canvas.itemconfig(v1.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)
                self.main_view.canvas.itemconfig(v2.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)
                self.main_view.canvas.itemconfig(v1.canvas_text, fill=DEFAULT_ALGORITHM_TEXT_FILL)
                self.main_view.canvas.itemconfig(v2.canvas_text, fill=DEFAULT_ALGORITHM_TEXT_FILL)
            else:
                self.main_view.canvas.itemconfig(edge.canvas_object_id, fill=DEFAULT_ALGORITHM_NOT_FOCUSED)

        self.algorithm_state = {
            "index": -1, 
            "steps": {"logs": logs,
                     "edges": edge_logs,
                     "vertices": vertices_logs},
            "is_bfs_or_dfs": False   
        }

        self.state = None

    def visualize_prim(self, event):
        """Metóda slúžiaca na vizualizovanie Primovho algoritmu"""

        if self.state != "prim":
            self.state = None
            return
        
        self.clear_algorithm_state()
        
        x = self.main_view.canvas.canvasx(event.x)
        y = self.main_view.canvas.canvasy(event.y)
        start_vertex = None

        for vertex in self.vertices:
            if vertex.is_clicked(x, y):
                start_vertex = vertex
                break

        if start_vertex is None:
            self.state = None
            return
        
        nx_g = self.build_nx_graph()

        try:
            mst_edges, mst_cost, logs, edge_logs, vertices_logs = self.algorithms.prim(start_vertex)
        except TypeError:
            self.state = None
            return

        if not nx.is_connected(nx_g):
            self.main_view.infobox.log("Chyba: Graf nie je súvislý")
            self.state = None
            return

        try:
            nx_mst = nx.minimum_spanning_tree(nx_g, algorithm="prim")
        except nx.NetworkXNotImplemented:
            self.state = None
            return
        
        if not mst_edges:
            self.state = None
            return
        
        self.reset_vertices_and_edges(None)

        self.main_view.infobox.log("Algoritmus úspešne prebehol")
        self.main_view.infobox.log("Porovnávam výsledky z algoritmu s výsledkami z NetworkX")

        nx_mst_cost = nx_mst.size(weight="weight")
        if nx_mst_cost != mst_cost:
            self.main_view.infobox.log("Chyba: Test medzi vlastným algoritmom a NetworkX algoritmom zlyhal")
            self.main_view.infobox.log(f"Váha NetworkX: {nx_mst_cost}")
            self.main_view.infobox.log(f"Váha Vlastného algoritmu: {mst_cost}")
            return

        self.main_view.infobox.log(f"Výsledky sedia - kostra bola vytvorená, celková váha je {mst_cost}")
        self.main_view.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu.")

        self.algorithm_state = {
            "index": -1, 
            "steps": {"logs": logs,
                     "edges": edge_logs,
                     "vertices": vertices_logs},
            "is_bfs_or_dfs": False       
        }

        for edge in self.edges:
            if edge in mst_edges:
                v1, v2 = edge.vertices
                self.main_view.canvas.itemconfig(edge.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)
                self.main_view.canvas.itemconfig(v1.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)
                self.main_view.canvas.itemconfig(v2.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)
                self.main_view.canvas.itemconfig(v1.canvas_text, fill=DEFAULT_ALGORITHM_TEXT_FILL)
                self.main_view.canvas.itemconfig(v2.canvas_text, fill=DEFAULT_ALGORITHM_TEXT_FILL)
            else:
                self.main_view.canvas.itemconfig(edge.canvas_object_id, fill=DEFAULT_ALGORITHM_NOT_FOCUSED)

        self.state = None

    def visualize_kruskal(self):
        """Metóda slúžiaca na vizualizovanie Kruskalovho algoritmu"""

        if self.state != "kruskal":
            self.state = None
            return
        
        self.clear_algorithm_state()
        nx_g = self.build_nx_graph()

        try:
            mst_edges, mst_cost, logs, edge_logs, vertices_logs = self.algorithms.kruskal()
        except TypeError:
            self.state = None
            return

        if not nx.is_connected(nx_g):
            self.main_view.infobox.log("Chyba: Graf nie je súvislý")
            self.state = None
            return

        try:
            nx_mst = nx.minimum_spanning_tree(nx_g, algorithm="prim")
        except nx.NetworkXNotImplemented:
            self.state = None
            return
        
        if not mst_edges:
            self.state = None
            return
        
        self.reset_vertices_and_edges(None)

        self.main_view.infobox.log("Algoritmus úspešne prebehol")
        self.main_view.infobox.log("Porovnávam výsledky z algoritmu s výsledkami z NetworkX")

        nx_mst_cost = nx_mst.size(weight="weight")
        if nx_mst_cost != mst_cost:
            self.main_view.infobox.log("Chyba: Test medzi vlastným algoritmom a NetworkX algoritmom zlyhal")
            self.main_view.infobox.log(f"Váha NetworkX: {nx_mst_cost}")
            self.main_view.infobox.log(f"Váha Vlastného algoritmu: {mst_cost}")
            return

        self.main_view.infobox.log(f"Výsledky sedia - kostra bola vytvorená, celková váha je {mst_cost}")
        self.main_view.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu.")

        self.algorithm_state = {
            "index": -1, 
            "steps": {"logs": logs,
                     "edges": edge_logs,
                     "vertices": vertices_logs},
            "is_bfs_or_dfs": False       
        }

        for edge in self.edges:
            if edge in mst_edges:
                self.main_view.canvas.itemconfig(edge.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)
            else:
                self.main_view.canvas.itemconfig(edge.canvas_object_id, fill=DEFAULT_ALGORITHM_NOT_FOCUSED)

        self.state = None

    def visualize_bfs(self, event):
        """Metóda slúžiaca na vizualizovanie BFS algoritmu"""

        if self.state != "bfs":
            self.state = None
            return

        self.clear_algorithm_state()

        x = self.main_view.canvas.canvasx(event.x)
        y = self.main_view.canvas.canvasy(event.y)

        start_vertex = None

        for vertex in self.vertices:
            if vertex.is_clicked(x, y):
                start_vertex = vertex
                break

        if start_vertex is None:
            self.state = None
            return

        self.reset_vertices_and_edges(event)

        nx_g = self.build_nx_graph()
        nx_tree = nx.bfs_tree(nx_g, start_vertex.id)
        nx_edges = sorted(sorted(edge) for edge in nx_tree.edges())

        own_tree_edges, vertex_order, logs, edge_logs, vertices_logs = self.algorithms.bfs(start_vertex)
        own_sorted = sorted(sorted(edge) for edge in own_tree_edges)

        self.main_view.infobox.log("Porovnávam výsledky z algoritmu s výsledkami z NetworkX")
        if nx_edges != own_sorted:
            self.main_view.infobox.log("Chyba: Test medzi vlastným algoritmom a NetworkX algoritmom zlyhal")
            return

        self.main_view.infobox.log("Výsledky sedia")
        self.main_view.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu")

        self.algorithm_state = {
            "index": -1, 
            "steps": {"logs": logs,
                     "edges": edge_logs,
                     "vertices": vertices_logs},
            "is_bfs_or_dfs": True       
        }

        for vertex in self.vertices:
            if vertex in vertex_order:
                self.main_view.canvas.itemconfig(vertex.canvas_object_id, 
                                       fill=DEFAULT_ALGORITHM_FILL)
                self.main_view.canvas.itemconfig(vertex.dfs_bfs_order, 
                                       fill=DEFAULT_ALGORITHM_FILL, 
                                       text=str(vertex_order[vertex]))
                self.main_view.canvas.itemconfig(vertex.canvas_text,
                                        fill=DEFAULT_ALGORITHM_TEXT_FILL)

        self.state = None

    def visualize_dfs(self, event):
        """Metóda slúžiaca na vizualizovanie DFS algoritmu"""

        if self.state != "dfs":
            self.state = None
            return

        self.clear_algorithm_state()

        x = self.main_view.canvas.canvasx(event.x)
        y = self.main_view.canvas.canvasy(event.y)

        start_vertex = None

        for vertex in self.vertices:
            if vertex.is_clicked(x, y):
                start_vertex = vertex
                break

        if start_vertex is None:
            self.state = None
            return

        self.reset_vertices_and_edges(event)

        nx_g = self.build_nx_graph()
        nx_tree = nx.dfs_tree(nx_g, start_vertex.id)
        nx_edges = {tuple(sorted(edge)) for edge in nx_tree.edges()}

        own_tree_edges, vertex_order, logs, edge_logs, vertices_logs = self.algorithms.dfs(start_vertex)
        own_edges = {tuple(sorted(edge)) for edge in own_tree_edges}

        self.main_view.infobox.log("Porovnávam výsledky z algoritmu s výsledkami z NetworkX")
        if nx_edges != own_edges:
            self.main_view.infobox.log("Chyba: Test medzi vlastným algoritmom a NetworkX algoritmom zlyhal")
            return

        self.main_view.infobox.log("Výsledky sedia")
        self.main_view.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu")

        self.algorithm_state = {
            "index": -1, 
            "steps": {"logs": logs,
                     "edges": edge_logs,
                     "vertices": vertices_logs},
            "is_bfs_or_dfs": True       
        }

        for vertex in self.vertices:
            if vertex in vertex_order:
                self.main_view.canvas.itemconfig(vertex.canvas_object_id,
                                        fill=DEFAULT_ALGORITHM_FILL)
                self.main_view.canvas.itemconfig(vertex.dfs_bfs_order,
                                       fill=DEFAULT_ALGORITHM_FILL,
                                       text=str(vertex_order[vertex]))
                self.main_view.canvas.itemconfig(vertex.canvas_text, 
                                       fill=DEFAULT_ALGORITHM_TEXT_FILL)

        self.state = None

    def visualize_floyd_warshall(self):
        """Metóda slúžiaca na vizualizovanie Floyd-Warshallovho algoritmu"""

        if self.state != "floyd_warshall":
            self.state = None
            return
        
        self.clear_algorithm_state()
        self.reset_vertices_and_edges(None)

        nx_g = self.build_nx_graph()
        nx_fw = nx.floyd_warshall(nx_g, weight="weight")
        nx_results = {a: dict(b) for a,b in nx_fw.items()}
        own_res, distances, prev_vertex, logs, edge_logs, vertices_logs = self.algorithms.floyd_warshall()

        self.main_view.infobox.log("Porovnávam výsledky z algoritmu s výsledkami z NetworkX")
        if nx_results != own_res:
            self.main_view.infobox.log("Chyba: Test medzi vlastným algoritmom a NetworkX algoritmom zlyhal")

        self.main_view.infobox.log("Výsledky sedia")
        self.main_view.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu")

        self.main_view.infobox.log("\nMatica vzdialeností:")
        for dv in distances:
            string = f"{dv}: " + ", ".join(f"{du}: {distances[dv][du]}" for du in distances[dv])
            self.main_view.infobox.log(string)

        self.main_view.infobox.log("\nMatica medzi vrcholov:")
        for nv in prev_vertex:
            string = f"{nv}: " + ", ".join(f"{nu}: {prev_vertex[nv][nu]}" if prev_vertex[nv][nu] is not None else f"{nu}: x" for nu in prev_vertex[nv])
            self.main_view.infobox.log(string)

        self.algorithm_state = {
            "index": -1, 
            "steps": {"logs": logs,
                     "edges": edge_logs,
                     "vertices": vertices_logs},
            "is_bfs_or_dfs": False       
        }

        self.state = None

    def visualize_hamilton(self):
        """   
            Metóda slúžiaca na vizualizovanie Hamiltonovej kružnice
            Nepoužívame tu test NetworkX, nakoľko táto knižnice neposkytuje
            plhodnotnú implementáciu tohto algoritmu, nakoľko jeho
            časová náročnosť je O(n!), práve preto aj vizualizácia
            tohto algoritmu prijme maximálne 6 vrcholov.

        """

        if self.state != "hamilton_cycle":
            self.state = None
            return

        if len(self.vertices) > 6:
            self.main_view.infobox.clear()
            self.main_view.infobox.log("Chyba: Pre vizualizáciu tohto algoritmu z dôvodu jeho časovej náročnosti je dovolené mať maximálne iba 6 vrcholov")
            self.state = None
            return

        self.clear_algorithm_state()
        self.reset_vertices_and_edges(None)
        logs, edge_logs, vertices_logs, path, used_edges = self.algorithms.hamilton_cycle()

        if path is None or used_edges is None:
            self.main_view.infobox.log("Hamiltonova kružnica v danom grafe neexistuje")
            self.main_view.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu")
        else:
            self.main_view.infobox.log("Hamiltonova kružnica v danom grafe existuje")
            self.main_view.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu")
            for vertex in self.vertices:
                self.main_view.canvas.itemconfig(vertex.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)
                self.main_view.canvas.itemconfig(vertex.canvas_text, fill=DEFAULT_ALGORITHM_TEXT_FILL)
            for edge in self.edges:
                if edge in used_edges:
                    self.main_view.canvas.itemconfig(edge.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)
                else:
                    self.main_view.canvas.itemconfig(edge.canvas_object_id, fill=DEFAULT_ALGORITHM_NOT_FOCUSED)

        self.algorithm_state = {
            "index": -1, 
            "steps": {"logs": logs,
                     "edges": edge_logs,
                     "vertices": vertices_logs},
            "is_bfs_or_dfs": False       
        }

        self.state = None

    def visualize_eulerian_path(self, event):
        """Metóda slúžiaca na vizualizovanie Eulerovho ťahu"""

        if self.state != "euler_path":
            self.state = None
            return

        self.clear_algorithm_state()

        x = self.main_view.canvas.canvasx(event.x)
        y = self.main_view.canvas.canvasy(event.y)

        start_vertex = None

        for vertex in self.vertices:
            if vertex.is_clicked(x, y):
                start_vertex = vertex
                break

        if start_vertex is None:
            self.state = None
            return

        self.reset_vertices_and_edges(event)

        nx_g = self.build_nx_graph()

        if not nx.has_eulerian_path(nx_g):
            self.main_view.infobox.clear()
            self.main_view.infobox.log("Chyba: V grafe nie sú splnené podmienky pre Eulerov ťah")
            self.state = None
            return

        logs, edge_logs, vertices_logs, path, used_edges = self.algorithms.eulerian_path(start_vertex)

        self.main_view.infobox.log("V grafe sú splnené podmienky pre Eulerov ťah")
        self.main_view.infobox.log(f"Kontrolujem, či existuje Eulerov ťah z počiatočného vrcholu {start_vertex}")

        for vertex in path:
            self.main_view.canvas.itemconfig(vertex.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)
            self.main_view.canvas.itemconfig(vertex.canvas_text, fill=DEFAULT_ALGORITHM_TEXT_FILL)

        for edge in self.edges:
            if edge in used_edges:
                self.main_view.canvas.itemconfig(edge.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)
            else:
                self.main_view.canvas.itemconfig(edge.canvas_object_id, fill=DEFAULT_ALGORITHM_NOT_FOCUSED)

        if len(used_edges) != len(self.edges):
            self.main_view.infobox.log(f"Eulerov ťah z vrcholu {start_vertex} neexistuje")
            self.main_view.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu")
        else:
            self.main_view.infobox.log(f"Eulerov ťah z vrcholu {start_vertex} existuje")
            self.main_view.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu")        

        self.algorithm_state = {
            "index": -1, 
            "steps": {"logs": logs,
                     "edges": edge_logs,
                     "vertices": vertices_logs},
            "is_bfs_or_dfs": False       
        }

        self.state = None

    def __check_if_clicked_on_vertex(self, x, y):
        """Metóda slúžiaca na vybranie dvoch vrcholov, na ktoré bolo kliknuté"""

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
        """Metóda slúžiaca na začiatok pohybu vrcholu"""

        if self.state != "move_vertex":
            return

        x = self.main_view.canvas.canvasx(event.x)
        y = self.main_view.canvas.canvasy(event.y)

        for vertex in self.vertices:
            if vertex.is_clicked(x, y):
                self.selected_vertex = vertex
                break

    def move_vertex(self, event):
        """Metóda slúžiaca na presun vrcholu"""

        if self.selected_vertex is None:
            return
        new_x = self.main_view.canvas.canvasx(event.x)
        new_y = self.main_view.canvas.canvasy(event.y)

        self.selected_vertex.move_to(new_x, new_y)

    def stop_move_vertex(self, event):
        """Zastavenie pohybu vrcholu"""

        self.selected_vertex = None

    def edit_vertex(self, event):
        """Upravovanie vrcholov"""

        self.state = None

        item_id = self.main_view.canvas.find_withtag("current")[0]
        vertex = self.canvas_id_to_vertex[item_id]

        self.edit_menu.render_vertex_edit_menu(event, vertex)

    def edit_edge(self, event):
        """Upravovanie hrán"""

        self.state = None

        item_id = self.main_view.canvas.find_withtag("current")[0]
        edge = self.canvas_id_to_edge[item_id]

        self.edit_menu.render_edge_edit_menu(event, edge)

    def update_layers(self):
        """Aktualizácie vrstiev po pridaní hrany."""

        self.main_view.canvas.tag_lower("edge")
        self.main_view.canvas.tag_raise("vertex")
        self.main_view.canvas.tag_raise("edge_label")

    def build_nx_graph(self):
        """Metóda slúžiaca na vytvorenie grafu NetworkX pre testovacie účely."""

        oriented = False

        for edge in self.edges:
            if edge.orientation == "yes":
                oriented = True
                break

        G = nx.MultiDiGraph() if oriented else nx.MultiGraph()

        for edge in self.edges:
            if oriented:
                if edge.orientation == "yes":
                    v1, v2 = edge.vertices
                    G.add_edge(v1.id, v2.id, weight=edge.weight)
                else:
                    v1, v2 = edge.vertices
                    G.add_edge(v1.id, v2.id, weight=edge.weight)
                    G.add_edge(v2.id, v1.id, weight=edge.weight)
            else:
                v1, v2 = edge.vertices
                G.add_edge(v1.id, v2.id, weight=edge.weight)

        return G

    def show_algorithm_step(self, go_to_next_step):
        """Pomocná metóda na zobrazenie jednotlivého kroku pomocou kliknutia na šípku v UI."""

        if not self.algorithm_state["steps"]:
            return
        
        if self.algorithm_state["index"] is None:
            self.algorithm_state["index"] = 0
            return
        
        self.algorithm_state["index"] += 1 if go_to_next_step else -1

        if self.algorithm_state["index"] < 0 or self.algorithm_state["index"] > len(self.algorithm_state["steps"]["logs"])-1:
            self.algorithm_state["index"] = 0

        self.main_view.infobox.clear()
        self.__show_algorithm_steps_in_memory()

    def __show_algorithm_steps_in_memory(self):
        """Metóda slúžiaca na zobrazenie jednotlivého kroku algoritmu uloženého v pamäti"""

        self.reset_vertices_and_edges(event=None)

        if not self.algorithm_state["steps"]:
            return

        for data in self.algorithm_state["steps"]["logs"][self.algorithm_state["index"]]:
            self.main_view.infobox.log(data)

        if not self.algorithm_state["is_bfs_or_dfs"]:
            edges = self.algorithm_state["steps"]["edges"][self.algorithm_state["index"]]
            for edge in self.edges:
                self.main_view.canvas.itemconfig(edge.canvas_object_id,
                                       fill=DEFAULT_ALGORITHM_NOT_FOCUSED)
            for edge, state in edges.items():
                if state:
                    self.main_view.canvas.itemconfig(edge.canvas_object_id, 
                                           fill=DEFAULT_ALGORITHM_FILL)
                else:
                    self.main_view.canvas.itemconfig(edge.canvas_object_id,
                                           fill=DEFAULT_ALGORITHM_NOT_SELECTED)
                    
            

        vertices = self.algorithm_state["steps"]["vertices"][self.algorithm_state["index"]]
        for vertex, state in vertices.items():
            if state:
                self.main_view.canvas.itemconfig(vertex.canvas_object_id,
                                       fill=DEFAULT_ALGORITHM_FILL)
                self.main_view.canvas.itemconfig(vertex.canvas_text,
                                       fill=DEFAULT_ALGORITHM_TEXT_FILL)
                if self.algorithm_state["is_bfs_or_dfs"]:
                    self.main_view.canvas.itemconfig(vertex.dfs_bfs_order,
                                           fill=DEFAULT_ALGORITHM_FILL,
                                           text=str(state))

    def reset_vertices_and_edges(self, event):
        """Metóda slúžiaca na resetovanie všetky úprav na hranách a vrcholov po vizualizovaní algoritmu."""

        if self.current_view != self.main_view:
            return

        for vertex in self.vertices:
            self.main_view.canvas.itemconfig(vertex.canvas_object_id, fill=vertex.fill_color, outline=vertex.outline_color)
            self.main_view.canvas.itemconfig(vertex.canvas_text, fill=vertex.text_color, text=vertex.tag)
            self.main_view.canvas.itemconfig(vertex.dfs_bfs_order, fill="", text="")
        for edge in self.edges:
            self.main_view.canvas.itemconfig(edge.canvas_object_id, fill=edge.line_color)

    def update_all_edges(self, line, box, text):
        """Aktualizácia všetkých hrán."""

        for edge in self.edges:
            edge.update(edge.weight, line, box, text)

    def update_all_vertices(self, fill, outline, text):
        """Aktualizácia všetkých vrcholov."""

        for vertex in self.vertices:
            vertex.update(str(vertex.tag), fill, outline, text)

    def export_graph(self):
        """Metóda slúžiaca na exportovanie grafu."""

        data = {
            "vertices": [],
            "edges": []
        }

        if not self.vertices or not self.edges:
            self.main_view.infobox.log("Chyba: Neexistuje graf, ktorý môžem exportovať")
            return
        
        for vertex in self.vertices:
            x1,y1,x2,y2 = self.main_view.canvas.coords(vertex.canvas_object_id)
            fill_color = vertex.fill_color
            outline_color = vertex.outline_color
            text_color = vertex.text_color
            tag = str(vertex.tag)

            data["vertices"].append({
                "id": vertex.id,
                "coords": (x1, y1, x2, y2),
                "fill_color": fill_color,
                "outline_color": outline_color,
                "text_color": text_color,
                "tag": tag
            })

        for edge in self.edges:
            fill_color = edge.line_color
            box_color = edge.box_color
            weight_color = edge.weight_color
            weight = edge.weight
            orientation = edge.orientation
            u, v = edge.vertices
            edge_id = edge.id

            data["edges"].append({
                "fill_color": fill_color,
                "box_color": box_color,
                "weight_color": weight_color,
                "weight": weight,
                "orientation": orientation,
                "first_vertex": u.id,
                "second_vertex": v.id,
                "id": edge_id
            })

        file = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")]
        )

        if not file:
            self.main_view.infobox.log("Chyba: Nepodarilo sa exportovať graf")
            return

        with open(file, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4) 

    def import_graph(self):
        """Metóda slúžiaca na importovanie grafu."""

        file = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json")]
        )

        if not file:
            self.main_view.infobox.log("Chyba: Nepodarilo sa importovať graf")
            return 
        
        with open(file, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)

        if not data["vertices"] or not data["edges"]:
            self.main_view.infobox.log("Chyba: Nepodarilo sa zostaviť graf")
            return 
        
        self.__remove_all_objects(None)
        
        vertex_id_map = {}
        vertex_ids = set()

        for vertex in data["vertices"]:
            if not Vertex.validate(self, vertex):
                self.main_view.infobox.log("Chyba: Neplatné údaje v JSON súbore")
                self.__remove_all_objects(None, False)
                return
            x, y = vertex["coords"][0], vertex["coords"][1]
            imported_vertex = Vertex(self, (x - (RADIUS * self.zoom), y - (RADIUS * self.zoom), x + (RADIUS * self.zoom), y + (RADIUS * self.zoom)),
                            vertex["fill_color"], vertex["outline_color"], vertex["text_color"], DEFAULT_WIDTH)
            imported_vertex.id = vertex["id"]
            imported_vertex.tag = vertex["tag"]
            self.vertices.append(imported_vertex)
            self.canvas_id_to_vertex[imported_vertex.canvas_object_id] = imported_vertex
            self.canvas_id_to_vertex[imported_vertex.canvas_text] = imported_vertex
            self.main_view.canvas.itemconfig(imported_vertex.canvas_text,  text=vertex["tag"])
            vertex_id_map[imported_vertex.id] = imported_vertex
            vertex_ids.add(vertex["id"])

        for edge in data["edges"]:
            if not Edge.validate(self, edge, vertex_ids):
                self.main_view.infobox.log("Chyba: Neplatné údaje v JSON súbore")
                self.__remove_all_objects(None, False)
                return
            u, v = vertex_id_map[edge["first_vertex"]], vertex_id_map[edge["second_vertex"]]

            imported_edge = Edge(self,
                        edge["fill_color"],
                        edge["box_color"],
                        edge["weight_color"],
                        DEFAULT_WIDTH,
                        edge["weight"],
                        edge["orientation"],
                        u, v)
            
            imported_edge.id = edge["id"]        

            self.edges.append(imported_edge)
            u.edges.append(imported_edge)
            v.edges.append(imported_edge)  
            self.canvas_id_to_edge[imported_edge.canvas_object_id] = imported_edge
            self.canvas_id_to_edge[imported_edge.canvas_text] = imported_edge
            self.canvas_id_to_edge[imported_edge.canvas_text_bg] = imported_edge

        if not self.vertices or not self.edges:
            self.main_view.infobox.log("Chyba: Nepodarilo sa zostaviť graf")
            return
        
        Vertex.identifier = max(v.id for v in self.vertices) + 1
        Edge.identifier = max(e.id for e in self.edges) + 1

        self.update_layers()

    def __remove_all_objects(self, event, clear_info_box=True):
        """Metóda slúžiaca na rýchle premazanie grafu."""

        if self.current_view != self.main_view:
            return

        self.main_view.canvas.delete("all")
        self.edges.clear()
        self.vertices.clear()
        self.canvas_id_to_edge.clear()
        self.canvas_id_to_vertex.clear()
        self.clear_algorithm_state()
        Vertex.identifier = 1
        Edge.identifier = 1
        if clear_info_box:
            self.main_view.infobox.clear()

    def __zoom(self, event):
        """Metóda slúžiaca na približovanie a oddialovanie grafu."""

        if self.current_view != self.main_view:
            return

        if event.delta > 0:
            factor = 1.05
        else:
            factor = 0.95
            
        new_zoom = self.zoom * factor

        if new_zoom > 2 or new_zoom < 0.4:
            return
        
        self.zoom = new_zoom
        self.main_view.canvas.scale("all", self.main_view.canvas.winfo_width() / 2, self.main_view.canvas.winfo_height() / 2, factor, factor)

        for vertex in self.vertices:
            vertex.coords = self.main_view.canvas.coords(vertex.canvas_object_id)

        for edge in self.edges:
            edge.update_position()
    
    def clear_algorithm_state(self):
        """Metóda slúžiaca na prečistenie pamäte algoritmu."""

        self.algorithm_state = {"index": None, "steps": [], "is_bfs_or_dfs": False}

    def __global_click_dropdown_close(self, event):
        """Metóda slúžiaca na zatvorenie dropdownov po kliknutí na ľubovoľné miesto."""

        if self.current_view != self.main_view:
            return

        if self.main_view.algorithm_dropdown.expanded:
            if event.widget in [b.button for b in self.main_view.algorithm_dropdown.buttons]:
                return
            self.main_view.algorithm_dropdown.change_dropdown_state()

        if self.main_view.algorithm_info_dropdown.expanded:
            if event.widget in [b.button for b in self.main_view.algorithm_info_dropdown.buttons]:
                return
            self.main_view.algorithm_info_dropdown.change_dropdown_state()

    def close_dropdown(self, dropdown):
        """Metóda slúžiaca na zatvorenie dropdownu kliknutím na tlačidlo."""

        if not dropdown or not dropdown.expanded:
            return
        dropdown.change_dropdown_state()
        
    # https://www.geeksforgeeks.org/dsa/check-if-a-given-string-is-a-valid-hexadecimal-color-code-or-not/
    def is_valid_hexadecimal_code(self, string):
        """Metóda slúžiaca na validovanie hexadecimálneho kódu."""

        hexa_code = re.compile(r'^#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$')
        return bool(re.match(hexa_code, string))
    
    def load_view(self, view):
        """Metóda slúžiaca na načítanie pohľadu."""

        if self.current_view:
            self.current_view.place_forget()
        self.current_view = self.views[view]
        self.current_view.place(x=0, y=0, relwidth=1, relheight=1)

    def validate_questions(self, data):
        """"Metóda slúžiaca na validovanie otázok v JSON súbore autotestov"""

        for question in data["questions"]:
            if not isinstance(question, dict):
                return f"Nemôžem spustiť test, lebo otázka {question} obsahuje chybu vo formáte, skontroluje JSON súbor s otázkami"
            if not isinstance(question.get("id"), int):
                return f"Nemôžem spustiť test, lebo otázka {question} obsahuje chybu v ID, skontroluje JSON súbor s otázkami"
            if question.get("type") not in ["single_choice", "multiple_choice"]:
                return f"Nemôžem spustiť test, lebo otázka {question} obsahuje chybu v možnostiach, skontroluje JSON súbor s otázkami"
            if not isinstance(question.get("question"), str):
                return f"Nemôžem spustiť test, lebo otázka {question} obsahuje chybu v otázke, skontroluje JSON súbor s otázkami"
            image = question.get("image")
            if image is not None and not isinstance(image, str):
                return f"Nemôžem spustiť test, lebo otázka {question} obsahuje chybu v obrázku, skontroluje JSON súbor s otázkami"
            
            answers = question.get("answers")
            if not isinstance(answers, list) or len(answers) == 0:
                return f"Nemôžem spustiť test, lebo otázka {question} obsahuje chybu vo formáte odpovedí, skontroluje JSON súbor s otázkami"
            correct_answers_count = 0
            for answer in answers:
                if not isinstance(answer, dict):
                    return f"Nemôžem spustiť test, lebo otázka {question} obsahuje chybu vo formáte odpovede, skontroluje JSON súbor s otázkami"
                if not isinstance(answer.get("id"), int):
                    return f"Nemôžem spustiť test, lebo otázka {question} obsahuje chybu v id odpovedi, skontroluje JSON súbor s otázkami"
                if not isinstance(answer.get("text"), str):
                    return f"Nemôžem spustiť test, lebo otázka {question} obsahuje chybu v texte odpovedi, skontroluje JSON súbor s otázkami"
                if not isinstance(answer.get("correct"), bool):
                    return f"Nemôžem spustiť test, lebo otázka {question} obsahuje chybu v boolovskej hodnote odpovede, skontroluje JSON súbor s otázkami"
                if answer.get("correct"):
                    correct_answers_count += 1

            if question["type"] == "single_choice" and correct_answers_count != 1:
                return f"Nemôžem spustiť test, lebo otázka {question} obsahuje chybu, skontroluje JSON súbor s otázkami"
            
            if question["type"] == "multiple_choice" and correct_answers_count < 1:
                return f"Nemôžem spustiť test, lebo otázka {question} obsahuje chybu, skontroluje JSON súbor s otázkami"

        return True

    def load_questions(self):
        """Metóda slúžiaca na načítanie otázok."""

        if self.autotest_view.question_box:
            self.autotest_view.question_box.destroy()
        if self.autotest_view.answer_box:
            self.autotest_view.answer_box.destroy()
        self.autotest_view.correct_answers.clear()
        self.autotest_view.user_answers.clear()
        self.autotest_view.questions.clear()
        self.autotest_view.current_index = 0
        self.autotest_view.is_finished = False
        self.autotest_view.score = 0
        self.autotest_view.maximum_score = 0

        base_dir = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(base_dir, "autotest", "questions", "questions.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        validation_response = self.validate_questions(data)
        if validation_response is not True:
            self.main_view.infobox.clear()
            self.main_view.infobox.log(validation_response)
            return False
        
        self.autotest_view.questions = copy.deepcopy(data["questions"])
        random.shuffle(self.autotest_view.questions)

        for q in self.autotest_view.questions:
            random.shuffle(q["answers"])

        self.autotest_view.questions = self.autotest_view.questions[:5]

        for question in self.autotest_view.questions:
            for answer in question["answers"]:
                if answer["correct"]:
                    self.autotest_view.correct_answers.append(answer)
                    self.autotest_view.maximum_score += 1

        self.autotest_view.show_question()

        return True


    def go_to_next_question(self):
        """Metóda slúžiaca na presunutie sa na ďalšiu otázku v autoteste."""

        if self.current_view is not self.autotest_view:
            return

        if self.autotest_view.current_index < 5:
            self.autotest_view.current_index += 1
            if self.autotest_view.current_index == 4 and not self.autotest_view.is_finished:
                self.autotest_view.next_question_button.button["text"] = "Ukonči test"
            self.autotest_view.answer_box.get_user_answer(self.autotest_view.user_answers)
            if self.autotest_view.current_index < 5:
                self.autotest_view.show_question()
            else:
                self.finish_autotest()

    def finish_autotest(self):
        """"Metóda slúžiaca na vyhodnotenie autotestu."""

        if self.current_view is not self.autotest_view:
            return

        if self.autotest_view.is_finished:
            return
        
        self.autotest_view.next_question_button.button["text"] = "Ďalšia otázka"
        self.autotest_view.is_finished = True
        self.autotest_view.current_index = 0
        for answer in self.autotest_view.user_answers:
            if answer["correct"]:
                self.autotest_view.score += 1
        if len(self.autotest_view.user_answers) > len(self.autotest_view.correct_answers):
            penalty = (len(self.autotest_view.user_answers) - len(self.autotest_view.correct_answers)) / 2
            self.autotest_view.score -= penalty
        self.autotest_view.show_question()
