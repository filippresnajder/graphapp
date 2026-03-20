"""Importovanie knižníc, ktoré použijeme."""
import tkinter as tk
from tkinter import filedialog
import json
import re
import networkx as nx

from classes.button import Button
from classes.vertex import Vertex
from classes.edge import Edge
from classes.editmenu import EditMenu
from classes.algorithms import Algorithms
from classes.infobox import Infobox
from classes.user_interface import UserInterface
from constants import (RADIUS, DEFAULT_OUTLINE_COLOR, DEFAULT_FILL_COLOR, DEFAULT_BG_COLOR,
                       DEFAULT_BUTTON_COLOR, DEFAULT_DROPDOWN_BUTTON_COLOR, DEFAULT_TEXT_COLOR,
                       DEFAULT_ALGORITHM_FILL, DEFAULT_WIDTH, VERTEX_TAG, EDGE_TAG)

# TODO: Refactor code
# TODO: Check for infobox what is written what is not etc make sure info is readable
# TODO: Write info about algorithms in algorithm info
# TODO: Implement test section

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
        self.canvas = tk.Canvas(self.root, width=980, height=640, bg="white")
        self.canvas.place(x=280,y=50)
        self.edit_menu = EditMenu(self)
        self.add_vertex_button = Button(self, "add_vertex", "Pridať vrchol", DEFAULT_BUTTON_COLOR)
        self.add_edge_button = Button(self, "add_edge", "Pridať hranu", DEFAULT_BUTTON_COLOR)
        self.move_vertex_button = Button(self, "move_vertex",
                                         "Posunúť vrchol", DEFAULT_BUTTON_COLOR)
        self.top_right_ui_group = UserInterface([self.add_vertex_button, 
                                                self.add_edge_button,
                                                self.move_vertex_button], 720, 20, 110)
        self.algorithms_button = Button(self, "show_algorithms", "Algoritmy", DEFAULT_BUTTON_COLOR)
        self.dijkstra_button = Button(self, "dijkstra", "Dijkstra", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.prim_button = Button(self, "prim", "Prim", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.kruskal_button = Button(self, "kruskal", "Kruskal", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.dfs_button = Button(self, "dfs", "DFS", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.bfs_button = Button(self, "bfs", "BFS", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.floyd_warshall_button = Button(self, "floyd_warshall",
                                            "Floyd-Warshall", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.hamilton_cycle_button = Button(self, "hamilton_cycle",
                                            "Hamilt. kružnica", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.euler_path_button = Button(self, "euler_path",
                                        "Eulerov ťah", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.algorithm_dropdown = UserInterface([self.algorithms_button,
                                                 self.dijkstra_button,
                                                 self.prim_button,
                                                 self.kruskal_button,
                                                 self.dfs_button,
                                                 self.bfs_button,
                                                 self.floyd_warshall_button,
                                                 self.hamilton_cycle_button,
                                                 self.euler_path_button], 1050, 20, 24, True)
        self.algorithm_info_button = Button(self, "show_algorithms_info",
                                            "O algoritmoch", DEFAULT_BUTTON_COLOR)
        self.dijkstra_info_button = Button(self, "dijkstra_info",
                                           "Dijkstra", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.prim_info_button = Button(self, "prim_info",
                                       "Prim", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.kruskal_info_button = Button(self, "kruskal_info",
                                          "Kruskal", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.dfs_info_button = Button(self, "dfs_info", "DFS", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.bfs_info_button = Button(self, "bfs_info", "BFS", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.floyd_warshall_info_button = Button(self, "floyd_warshall_info",
                                                 "Floyd-Warshall", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.hamilton_cycle_info_button = Button(self, "hamilton_cycle_info",
                                                 "Hamilt. kružnica", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.euler_path_info_button = Button(self, "euler_path_info",
                                             "Eulerov ťah", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.algorithm_info_dropdown = UserInterface([self.algorithm_info_button,
                                                      self.dijkstra_info_button,
                                                      self.prim_info_button,
                                                      self.kruskal_info_button,
                                                      self.dfs_info_button,
                                                      self.bfs_info_button,
                                                      self.floyd_warshall_info_button,
                                                      self.hamilton_cycle_info_button,
                                                      self.euler_path_info_button],
                                                      1160, 20, 24, True)
        self.clear_infobox = Button(self, "clear_infobox", "Prečisti",
                                    DEFAULT_BUTTON_COLOR, "medium")
        self.infobox_ui_group = UserInterface([self.clear_infobox], 60, 670, 0)
        self.previous_step = Button(self, "prev_step", "<", DEFAULT_BUTTON_COLOR, "extra_small")
        self.next_step = Button(self, "next_step", ">", DEFAULT_BUTTON_COLOR, "extra_small")
        self.action_arrows_ui_group = UserInterface([self.previous_step, self.next_step],
                                                    135, 670, 42)
        self.export_graph_button = Button(self, "export_graph",
                                          "Export grafu", DEFAULT_BUTTON_COLOR)
        self.import_graph_button = Button(self, "import_graph",
                                          "Import grafu", DEFAULT_BUTTON_COLOR)
        self.top_left_ui_group = UserInterface([self.export_graph_button,
                                                self.import_graph_button], 20, 20, 110)
        self.infobox = Infobox(self, 240, 610, 20, 50)
        self.algorithms = Algorithms(self)
        self.algorithm_fill = DEFAULT_ALGORITHM_FILL
        self.canvas.tag_bind(VERTEX_TAG, "<Button-3>", self.edit_vertex)
        self.canvas.tag_bind(EDGE_TAG, "<Button-3>", self.edit_edge)
        self.root.bind("<Button-1>", self.__global_click_dropdown_close, add="+")
        self.root.bind("<r>", self.reset_vertices_and_edges)
        self.root.bind("<Control-d>", self.__remove_all_objects)
        self.root.bind("<Control-MouseWheel>", self.__zoom)
        self.root.mainloop()

    def create_vertex(self, event):
        """Metóda slúžiaca na vytvorenie vrcholu na plátno"""

        if self.state != "add_vertex":
            return

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

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
            self.infobox.clear()
            self.infobox.log("Nastala zmena v grafe, mažem pamäť krokov predošlého algoritmu")
            self.reset_vertices_and_edges(event=None)
        self.clear_algorithm_state()

    def create_edge(self, event):
        """Metóda slúžiaca na vytvorenie hrany"""

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

        if self.algorithm_state["steps"]:
            self.infobox.clear()
            self.infobox.log("Nastala zmena v grafe, mažem pamäť krokov predošlého algoritmu")
            self.reset_vertices_and_edges(event=None)
        self.clear_algorithm_state()

    def visualize_dijkstra(self,event):
        """Metóda slúžiaca na vizualizovanie Dijkstrovho algoritmu"""

        if self.state != "dijkstra":
            self.state = None
            return
        
        self.clear_algorithm_state()

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        result = self.__check_if_clicked_on_vertex(x, y)
        if result is None:
            self.state = None
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
            self.infobox.clear()
            self.infobox.log(f"Chyba: {str(e)}")
            return
        
        self.infobox.log("Algoritmus úspešne prebehol")
        self.infobox.log("Porovnávam výsledky z algoritmu s výsledkami z NetworkX")

        if nx_res != own_res:
            self.infobox.clear()
            self.infobox.log("Zlyhanie testu, výstupné údaje nesedia")
            self.infobox.log(f"NetworkX výsledok: {nx_res}")
            self.infobox.log(f"Vlastný výsledok: {own_res}")
            return
        
        self.infobox.log(f"Výsledky sedia - cesta {path_tag}")
        self.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu.")

        for edge in edge_objects:
            v1, v2 = edge.vertices
            self.canvas.itemconfig(edge.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)
            self.canvas.itemconfig(v1.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)
            self.canvas.itemconfig(v2.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)

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
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
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
            self.infobox.log("Chyba: Graf nie je súvislý")
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

        self.infobox.log("Algoritmus úspešne prebehol")
        self.infobox.log("Porovnávam výsledky z algoritmu s výsledkami z NetworkX")

        nx_mst_cost = nx_mst.size(weight="weight")
        if nx_mst_cost != mst_cost:
            self.infobox.log("Chyba: Test medzi vlastným algoritmom a NetworkX algoritmom zlyhal")
            self.infobox.log(f"Váha NetworkX: {nx_mst_cost}")
            self.infobox.log(f"Váha Vlastného algoritmu: {mst_cost}")
            return

        self.infobox.log(f"Výsledky sedia - kostra bola vytvorená, celková váha je {mst_cost}")
        self.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu.")

        self.algorithm_state = {
            "index": -1, 
            "steps": {"logs": logs,
                     "edges": edge_logs,
                     "vertices": vertices_logs},
            "is_bfs_or_dfs": False       
        }

        for edge in mst_edges:
            v1, v2 = edge.vertices
            self.canvas.itemconfig(edge.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)
            self.canvas.itemconfig(v1.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)
            self.canvas.itemconfig(v2.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)

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
            self.infobox.log("Chyba: Graf nie je súvislý")
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

        self.infobox.log("Algoritmus úspešne prebehol")
        self.infobox.log("Porovnávam výsledky z algoritmu s výsledkami z NetworkX")

        nx_mst_cost = nx_mst.size(weight="weight")
        if nx_mst_cost != mst_cost:
            self.infobox.log("Chyba: Test medzi vlastným algoritmom a NetworkX algoritmom zlyhal")
            self.infobox.log(f"Váha NetworkX: {nx_mst_cost}")
            self.infobox.log(f"Váha Vlastného algoritmu: {mst_cost}")
            return

        self.infobox.log(f"Výsledky sedia - kostra bola vytvorená, celková váha je {mst_cost}")
        self.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu.")

        self.algorithm_state = {
            "index": -1, 
            "steps": {"logs": logs,
                     "edges": edge_logs,
                     "vertices": vertices_logs},
            "is_bfs_or_dfs": False       
        }

        for edge in mst_edges:
            self.canvas.itemconfig(edge.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)

        self.state = None

    def visualize_bfs(self, event):
        """Metóda slúžiaca na vizualizovanie BFS algoritmu"""

        if self.state != "bfs":
            self.state = None
            return

        self.clear_algorithm_state()

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

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

        self.infobox.log("Porovnávam výsledky z algoritmu s výsledkami z NetworkX")
        if nx_edges != own_sorted:
            self.infobox.log("Chyba: Test medzi vlastným algoritmom a NetworkX algoritmom zlyhal")
            return

        self.infobox.log("Výsledky sedia")
        self.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu")

        self.algorithm_state = {
            "index": -1, 
            "steps": {"logs": logs,
                     "edges": edge_logs,
                     "vertices": vertices_logs},
            "is_bfs_or_dfs": True       
        }

        for vertex in self.vertices:
            if vertex in vertex_order:
                self.canvas.itemconfig(vertex.canvas_object_id, 
                                       fill=DEFAULT_ALGORITHM_FILL)
                self.canvas.itemconfig(vertex.dfs_bfs_order, 
                                       fill=DEFAULT_ALGORITHM_FILL, 
                                       text=str(vertex_order[vertex]))

        self.state = None

    def visualize_dfs(self, event):
        """Metóda slúžiaca na vizualizovanie DFS algoritmu"""

        if self.state != "dfs":
            self.state = None
            return

        self.clear_algorithm_state()

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

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

        self.infobox.log("Porovnávam výsledky z algoritmu s výsledkami z NetworkX")
        if nx_edges != own_edges:
            self.infobox.log("Chyba: Test medzi vlastným algoritmom a NetworkX algoritmom zlyhal")
            return

        self.infobox.log("Výsledky sedia")
        self.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu")

        self.algorithm_state = {
            "index": -1, 
            "steps": {"logs": logs,
                     "edges": edge_logs,
                     "vertices": vertices_logs},
            "is_bfs_or_dfs": True       
        }

        for vertex in self.vertices:
            if vertex in vertex_order:
                self.canvas.itemconfig(vertex.canvas_object_id,
                                        fill=DEFAULT_ALGORITHM_FILL)
                self.canvas.itemconfig(vertex.dfs_bfs_order,
                                       fill=DEFAULT_ALGORITHM_FILL,
                                       text=str(vertex_order[vertex]))

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

        self.infobox.log("Porovnávam výsledky z algoritmu s výsledkami z NetworkX")
        if nx_results != own_res:
            self.infobox.log("Chyba: Test medzi vlastným algoritmom a NetworkX algoritmom zlyhal")

        self.infobox.log("Výsledky sedia")
        self.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu")

        self.infobox.log("\nMatica vzdialeností:")
        for dv in distances:
            string = f"{dv}: " + ", ".join(f"{du}: {distances[dv][du]}" for du in distances[dv])
            self.infobox.log(string)

        self.infobox.log("\nMatica medzi vrcholov:")
        for nv in prev_vertex:
            string = f"{nv}: " + ", ".join(f"{nu}: {prev_vertex[nv][nu]}" if prev_vertex[nv][nu] is not None else f"{nu}: x" for nu in prev_vertex[nv])
            self.infobox.log(string)

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
            self.infobox.clear()
            self.infobox.log("Chyba: Pre vizualizáciu tohto algoritmu z dôvodu jeho časovej náročnosti je dovolené mať maximálne iba 6 vrcholov")
            self.state = None
            return

        self.clear_algorithm_state()
        self.reset_vertices_and_edges(None)
        logs, edge_logs, vertices_logs, path, used_edges = self.algorithms.hamilton_cycle()

        if path is None or used_edges is None:
            self.infobox.log("Hamiltonova kružnica v danom grafe neexistuje")
            self.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu")
        else:
            self.infobox.log("Hamiltonova kružnica v danom grafe existuje")
            self.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu")
            for vertex in self.vertices:
                self.canvas.itemconfig(vertex.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)
            for edge in used_edges:
                self.canvas.itemconfig(edge.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)

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

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

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
            self.infobox.clear()
            self.infobox.log("Chyba: V grafe nie sú splnené podmienky pre Eulerov ťah")
            self.state = None
            return

        logs, edge_logs, vertices_logs, path, used_edges = self.algorithms.eulerian_path(start_vertex)

        self.infobox.log("V grafe sú splnené podmienky pre Eulerov ťah")
        self.infobox.log(f"Kontrolujem, či existuje Eulerov ťah z počiatočného vrcholu {start_vertex}")

        for vertex in path:
            self.canvas.itemconfig(vertex.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)

        for edge in used_edges:
            self.canvas.itemconfig(edge.canvas_object_id, fill=DEFAULT_ALGORITHM_FILL)

        if len(used_edges) != len(self.edges):
            self.infobox.log(f"Eulerov ťah z vrcholu {start_vertex} neexistuje")
            self.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu")
        else:
            self.infobox.log(f"Eulerov ťah z vrcholu {start_vertex} existuje")
            self.infobox.log("Ukončujem algoritmus, pomocou šípiek nižšie je možné si prezrieť výpočet algoritmu")        

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

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        for vertex in self.vertices:
            if vertex.is_clicked(x, y):
                self.selected_vertex = vertex
                break

    def move_vertex(self, event):
        """Metóda slúžiaca na presun vrcholu"""

        if self.selected_vertex is None:
            return
        new_x = self.canvas.canvasx(event.x)
        new_y = self.canvas.canvasy(event.y)

        self.selected_vertex.move_to(new_x, new_y)

    def stop_move_vertex(self, event):
        """Zastavenie pohybu vrcholu"""

        self.selected_vertex = None

    def edit_vertex(self, event):
        """Upravovanie vrcholov"""

        self.state = None

        item_id = self.canvas.find_withtag("current")[0]
        vertex = self.canvas_id_to_vertex[item_id]

        self.edit_menu.render_vertex_edit_menu(event, vertex)

    def edit_edge(self, event):
        """Upravovanie hrán"""

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

        self.infobox.clear()
        self.__show_algorithm_steps_in_memory()

    def __show_algorithm_steps_in_memory(self):
        """Metóda slúžiaca na zobrazenie jednotlivého kroku algoritmu uloženého v pamäti"""

        self.reset_vertices_and_edges(event=None)

        if not self.algorithm_state["steps"]:
            return

        for data in self.algorithm_state["steps"]["logs"][self.algorithm_state["index"]]:
            self.infobox.log(data)

        if not self.algorithm_state["is_bfs_or_dfs"]:
            edges = self.algorithm_state["steps"]["edges"][self.algorithm_state["index"]]
            for edge, state in edges.items():
                if state:
                    self.canvas.itemconfig(edge.canvas_object_id, 
                                           fill=DEFAULT_ALGORITHM_FILL)
                else:
                    self.canvas.itemconfig(edge.canvas_object_id,
                                           fill="red")

        vertices = self.algorithm_state["steps"]["vertices"][self.algorithm_state["index"]]
        for vertex, state in vertices.items():
            if state:
                self.canvas.itemconfig(vertex.canvas_object_id,
                                       fill=DEFAULT_ALGORITHM_FILL)
                if self.algorithm_state["is_bfs_or_dfs"]:
                    self.canvas.itemconfig(vertex.dfs_bfs_order,
                                           fill=DEFAULT_ALGORITHM_FILL,
                                           text=str(state))

    def reset_vertices_and_edges(self, event):
        """Metóda slúžiaca na resetovanie všetky úprav na hranách a vrcholov po vizualizovaní algoritmu."""

        for vertex in self.vertices:
            self.canvas.itemconfig(vertex.canvas_object_id, fill=vertex.fill_color, outline=vertex.outline_color)
            self.canvas.itemconfig(vertex.canvas_text, fill=vertex.text_color, text=vertex.tag)
            self.canvas.itemconfig(vertex.dfs_bfs_order, fill="", text="")
        for edge in self.edges:
            self.canvas.itemconfig(edge.canvas_object_id, fill=edge.line_color)

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
            self.infobox.log("Chyba: Neexistuje graf, ktorý môžem exportovať")
            return
        
        for vertex in self.vertices:
            x1,y1,x2,y2 = self.canvas.coords(vertex.canvas_object_id)
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
            self.infobox.log("Chyba: Nepodarilo sa exportovať graf")
            return

        with open(file, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4) 

    def import_graph(self):
        """Metóda slúžiaca na importovanie grafu."""

        file = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json")]
        )

        if not file:
            self.infobox.log("Chyba: Nepodarilo sa importovať graf")
            return 
        
        with open(file, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)

        if not data["vertices"] or not data["edges"]:
            self.infobox.log("Chyba: Nepodarilo sa zostaviť graf")
            return 
        
        self.__remove_all_objects(None)
        
        vertex_id_map = {}
        vertex_ids = set()

        for vertex in data["vertices"]:
            if not Vertex.validate(self, vertex):
                self.infobox.log("Chyba: Neplatné údaje v JSON súbore")
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
            self.canvas.itemconfig(imported_vertex.canvas_text,  text=vertex["tag"])
            vertex_id_map[imported_vertex.id] = imported_vertex
            vertex_ids.add(vertex["id"])

        for edge in data["edges"]:
            if not Edge.validate(self, edge, vertex_ids):
                self.infobox.log("Chyba: Neplatné údaje v JSON súbore")
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
            self.infobox.log("Chyba: Nepodarilo sa zostaviť graf")
            return
        
        Vertex.identifier = max(v.id for v in self.vertices) + 1
        Edge.identifier = max(e.id for e in self.edges) + 1

        self.update_layers()

    def __remove_all_objects(self, event, clear_info_box=True):
        """Metóda slúžiaca na rýchle premazanie grafu."""

        self.canvas.delete("all")
        self.edges.clear()
        self.vertices.clear()
        self.canvas_id_to_edge.clear()
        self.canvas_id_to_vertex.clear()
        self.clear_algorithm_state()
        Vertex.identifier = 1
        Edge.identifier = 1
        if clear_info_box:
            self.infobox.clear()

    def __zoom(self, event):
        """Metóda slúžiaca na približovanie a oddialovanie grafu."""

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

        for edge in self.edges:
            edge.update_position()
    
    def clear_algorithm_state(self):
        """Metóda slúžiaca na prečistenie pamäte algoritmu."""

        self.algorithm_state = {"index": None, "steps": [], "is_bfs_or_dfs": False}

    def __global_click_dropdown_close(self, event):
        """Metóda slúžiaca na zatvorenie dropdownov po kliknutí na ľubovoľné miesto."""

        if self.algorithm_dropdown.expanded:
            if event.widget in [b.button for b in self.algorithm_dropdown.buttons]:
                return
            self.algorithm_dropdown.change_dropdown_state()

        if self.algorithm_info_dropdown.expanded:
            if event.widget in [b.button for b in self.algorithm_info_dropdown.buttons]:
                return
            self.algorithm_info_dropdown.change_dropdown_state()

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