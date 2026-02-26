"""Importovanie knižníc, ktoré použijeme."""
import tkinter as tk
import networkx as nx

from classes.button import Button
from classes.vertex import Vertex
from classes.edge import Edge
from classes.editmenu import EditMenu
from classes.algorithms import Algorithms
from classes.infobox import Infobox
from constants import (RADIUS, DEFAULT_OUTLINE_COLOR, DEFAULT_FILL_COLOR, DEFAULT_BG_COLOR,
                       DEFAULT_TEXT_COLOR, DEFAULT_ALGORITHM_FILL, DEFAULT_WIDTH, VERTEX_TAG, EDGE_TAG)

# TODO: Implement new button design
# TODO: Implement algorithm info
# TODO: Implement export and import to graphs



# LATER TODO: Check two graphs not connected to one another causing Prim and Kruskal to fail (NetworkX test FAILS)
# Os. poznámka - Spýtať sa na konzultáciach ohľadom Prima a Kruskala

class App:
    def __init__(self):
        self.state = None
        self.selected_vertex = None
        self.zoom = 1
        self.vertices = []
        self.edges = []
        self.algorithm_state = {
            "steps": [],
            "type": None,
            "index": None,
        }
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
        self.clear_infobox = Button(self, "clear_infobox", "CL", 20, 670)
        self.previous_step = Button(self, "prev_step", "PS", 80, 670)
        self.next_step = Button(self, "next_step", "NS", 140, 670)
        self.infobox = Infobox(self)
        self.algorithms = Algorithms(self)
        self.algorithm_fill = DEFAULT_ALGORITHM_FILL
        self.canvas = tk.Canvas(self.root, width=980, height=610, bg="white")
        self.canvas.place(x=280,y=80)
        self.canvas.tag_bind(VERTEX_TAG, "<Button-3>", self.edit_vertex)
        self.canvas.tag_bind(EDGE_TAG, "<Button-3>", self.edit_edge)
        self.root.bind("<r>", self.reset_vertices_and_edges)
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

        if (self.algorithm_state["steps"]):
            self.infobox.clear()
            self.infobox.log("Nastala zmena v grafe, mažem pamäť krokov predošlého algoritmu")
            self.reset_vertices_and_edges(event=None)
        self.clear_algorithm_state()

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

        if (self.algorithm_state["steps"]):
            self.infobox.clear()
            self.infobox.log("Nastala zmena v grafe, mažem pamäť krokov predošlého algoritmu")
            self.reset_vertices_and_edges(event=None)
        self.clear_algorithm_state()

    def visualize_dijkstra(self,event):
        if self.state != "dijkstra":
            return
        
        self.clear_algorithm_state()

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        result = self.__check_if_clicked_on_vertex(x, y)
        if result is None:
            return
        
        self.reset_vertices_and_edges(event)
        self.selected_vertex = None
        start_vertex, end_vertex = result

        nx_G = self.build_nx_graph()

        own_result = self.algorithms.dijkstra(start_vertex, end_vertex)
        if not own_result:
            return

        own_res, edge_ids, path_tag, logs = own_result

        try:
            nx_res = nx.dijkstra_path(nx_G, start_vertex.id, end_vertex.id)
        except Exception as e:
            self.infobox.clear()
            self.infobox.log(f"Chyba: {str(e)}")
            return

        logs.append("Porovnávam výsledky z algoritmu s výsledkami z NetworkX")

        if nx_res != own_res:
            self.infobox.clear()
            self.infobox.log("Zlyhanie testu, výstupné údaje nesedia")
            self.infobox.log(f"NetworkX výsledok: {nx_res}")
            self.infobox.log(f"Vlastný výsledok: {own_res}")
            return
        
        logs.append(f"Výsledky sedia - cesta {path_tag}")
        logs.append("Ukončujem algoritmus")


        self.algorithm_state = {
            "steps": edge_ids,      
            "type": "edges",     
            "index": len(edge_ids),       
        }
        self.__show_algorithm_steps_in_memory()  

        for data in logs:
            self.infobox.log(data)  

        self.state = None

    def visualize_prim(self, event):
        if self.state != "prim":
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
            return
        
        self.reset_vertices_and_edges(event)

        try:
            mst_edges, logs = self.algorithms.prim(start_vertex)
        except Exception:
            return
        
        if not mst_edges:
            return

        nx_G = self.build_nx_graph()
        try:
            nx_mst = nx.minimum_spanning_tree(nx_G, algorithm="prim")
        except Exception as e:
            self.infobox.clear()
            self.infobox.log(f"Chyba: {str(e)}")
            return
        nx_cost = nx_mst.size(weight="weight")
        own_cost = self.__mst_cost_self(mst_edges)

        logs.append("Porovnávam výsledky z algoritmu s výsledkami z NetworkX")
        if (nx_cost != own_cost):
            self.infobox.log("Chyba: Test medzi vlastným algoritmom a NetworkX algoritmom zlyhal")
            self.infobox.log(f"Váha NetworkX: {nx_cost}")
            self.infobox.log(f"Váha Vlastného algoritmu: {own_cost}")
            return

        logs.append(f"Výsledky sedia - kostra bola vytvorená, celková váha je {own_cost}")
        logs.append("Ukončujem algoritmus\n")  

        self.algorithm_state = {
            "steps": mst_edges,      
            "type": "edges",     
            "index": len(mst_edges),       
        }
        self.__show_algorithm_steps_in_memory()

        for data in logs:
            self.infobox.log(data)  

        self.state = None

    def visualize_kruskal(self):
        if self.state != "kruskal":
            return
        
        self.clear_algorithm_state()

        self.reset_vertices_and_edges(None)
        try:
            mst_edges, logs = self.algorithms.kruskal()
        except Exception:
            return
        
        if not mst_edges:
            return
        
        nx_G = self.build_nx_graph()
        try:
            nx_mst = nx.minimum_spanning_tree(nx_G, algorithm="prim")
        except Exception as e:
            self.infobox.clear()
            self.infobox.log(f"Chyba: {str(e)}")
            return
        nx_cost = nx_mst.size(weight="weight")
        own_cost = self.__mst_cost_self(mst_edges)

        logs.append("Porovnávam výsledky z algoritmu s výsledkami z NetworkX")
        if (nx_cost != own_cost):
            self.infobox.log("Chyba: Test medzi vlastným algoritmom a NetworkX algoritmom zlyhal")
            self.infobox.log(f"Váha NetworkX: {nx_cost}")
            self.infobox.log(f"Váha Vlastného algoritmu: {own_cost}")
            return  

        logs.append(f"Výsledky sedia - kostra bola vytvorená, celková váha je {own_cost}")
        logs.append("Ukončujem algoritmus")

        self.algorithm_state = {
            "steps": mst_edges,      
            "type": "edges",     
            "index": len(mst_edges),       
        }
        self.__show_algorithm_steps_in_memory()

        for data in logs:
            self.infobox.log(data)  

        self.state = None

    def visualize_bfs(self, event):
        if self.state != "bfs":
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
            return
        
        self.reset_vertices_and_edges(event)

        nx_G = self.build_nx_graph()
        nx_tree = nx.bfs_tree(nx_G, start_vertex.id)
        nx_edges = sorted(sorted(edge) for edge in nx_tree.edges())

        own_order, own_tree_edges, logs = self.algorithms.bfs(start_vertex)
        own_sorted = sorted(sorted(edge) for edge in own_tree_edges)

        logs.append("Porovnávam výsledky z algoritmu s výsledkami z NetworkX")
        if nx_edges != own_sorted:
            self.infobox.log("Chyba: Test medzi vlastným algoritmom a NetworkX algoritmom zlyhal")
            return

        logs.append("Výsledky sedia, ukončujem algoritmus")

        self.algorithm_state = {
            "steps": own_order,      
            "type": "vertices",     
            "index": len(own_order),       
        }
        self.__show_algorithm_steps_in_memory()

        for data in logs:
            self.infobox.log(data)  

        self.state = None

    def visualize_dfs(self, event):
        if self.state != "dfs":
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
            return
        
        self.reset_vertices_and_edges(event)

        nx_G = self.build_nx_graph()
        nx_tree = nx.dfs_tree(nx_G, start_vertex.id, sort_neighbors=sorted)
        nx_edges = {tuple(sorted(edge)) for edge in nx_tree.edges()}

        own_order, own_tree_edges, logs = self.algorithms.dfs(start_vertex)
        own_edges = {tuple(sorted(edge)) for edge in own_tree_edges}

        logs.append("Porovnávam výsledky z algoritmu s výsledkami z NetworkX")
        if nx_edges != own_edges:
            self.infobox.log("Chyba: Test medzi vlastným algoritmom a NetworkX algoritmom zlyhal")
            return
        
        logs.append("Výsledky sedia, ukončujem algoritmus")

        self.algorithm_state = {
            "steps": own_order,      
            "type": "vertices",     
            "index": len(own_order),       
        }
        self.__show_algorithm_steps_in_memory()

        for data in logs:
            self.infobox.log(data)  

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
        if not self.algorithm_state["steps"]:
            return
        
        if self.algorithm_state["index"] is None:
            self.algorithm_state["index"] = 0
            return
        
        self.algorithm_state["index"] += 1 if go_to_next_step else -1

        if self.algorithm_state["index"] < 0 or self.algorithm_state["index"] > len(self.algorithm_state["steps"]):
            self.algorithm_state["index"] = 0

        self.__show_algorithm_steps_in_memory()

    def __show_algorithm_steps_in_memory(self):
        self.reset_vertices_and_edges(event=None)

        if not self.algorithm_state["steps"] or self.algorithm_state["type"] is None:
            return

        if self.algorithm_state["type"] == "edges":
            for edge in self.edges:
                if edge.id in self.algorithm_state["steps"][:self.algorithm_state["index"]]:
                    self.canvas.itemconfig(edge.canvas_object_id, fill=self.algorithm_fill)
        elif self.algorithm_state["type"] == "vertices":
            for index, vertex_id in enumerate(self.algorithm_state["steps"][:self.algorithm_state["index"]], start=1):
                for vertex in self.vertices:
                    if vertex.id == vertex_id:
                        self.canvas.itemconfig(vertex.canvas_object_id, fill=self.algorithm_fill)
                        self.canvas.itemconfig(vertex.canvas_text, text=str(index), fill="white")
        


    def reset_vertices_and_edges(self, event):
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
        self.infobox.clear()
        self.clear_algorithm_state()
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

        for edge in self.edges:
            edge.update_position()
    
    def __mst_cost_self(self, edges):
        cost = 0
        for edge in self.edges:
            if edge.id in edges:
                cost += edge.weight
        return cost
    
    def clear_algorithm_state(self):
        self.algorithm_state = {"steps": [], "type": None, "index": None}
    


        