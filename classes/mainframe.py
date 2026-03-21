import tkinter as tk

from classes.button import Button
from classes.infobox import Infobox
from classes.user_interface import UserInterface
from constants import (DEFAULT_BUTTON_COLOR, DEFAULT_DROPDOWN_BUTTON_COLOR, 
                       VERTEX_TAG, EDGE_TAG)

class MainFrame(tk.Frame):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.canvas = tk.Canvas(self, width=980, height=640, bg="white")
        self.canvas.place(x=280,y=50)
        self.add_vertex_button = Button(self, self.app, "add_vertex", "Pridať vrchol", DEFAULT_BUTTON_COLOR)
        self.add_edge_button = Button(self, self.app, "add_edge", "Pridať hranu", DEFAULT_BUTTON_COLOR)
        self.move_vertex_button = Button(self, self.app, "move_vertex",
                                         "Posunúť vrchol", DEFAULT_BUTTON_COLOR)
        self.top_right_ui_group = UserInterface([self.add_vertex_button, 
                                                self.add_edge_button,
                                                self.move_vertex_button], 720, 20, 110)
        self.algorithms_button = Button(self, self.app, "show_algorithms", "Algoritmy", DEFAULT_BUTTON_COLOR)
        self.dijkstra_button = Button(self, self.app, "dijkstra", "Dijkstra", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.prim_button = Button(self, self.app, "prim", "Prim", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.kruskal_button = Button(self, self.app, "kruskal", "Kruskal", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.dfs_button = Button(self, self.app, "dfs", "DFS", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.bfs_button = Button(self, self.app, "bfs", "BFS", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.floyd_warshall_button = Button(self, self.app, "floyd_warshall",
                                            "Floyd-Warshall", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.hamilton_cycle_button = Button(self, self.app, "hamilton_cycle",
                                            "Hamilt. kružnica", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.euler_path_button = Button(self, self.app, "euler_path",
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
        self.algorithm_info_button = Button(self, self.app, "show_algorithms_info",
                                            "O algoritmoch", DEFAULT_BUTTON_COLOR)
        self.dijkstra_info_button = Button(self, self.app, "dijkstra_info",
                                           "Dijkstra", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.prim_info_button = Button(self, self.app, "prim_info",
                                       "Prim", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.kruskal_info_button = Button(self, self.app, "kruskal_info",
                                          "Kruskal", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.dfs_info_button = Button(self, self.app, "dfs_info", "DFS", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.bfs_info_button = Button(self, self.app, "bfs_info", "BFS", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.floyd_warshall_info_button = Button(self, self.app, "floyd_warshall_info",
                                                 "Floyd-Warshall", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.hamilton_cycle_info_button = Button(self, self.app, "hamilton_cycle_info",
                                                 "Hamilt. kružnica", DEFAULT_DROPDOWN_BUTTON_COLOR)
        self.euler_path_info_button = Button(self, self.app, "euler_path_info",
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
        self.clear_infobox = Button(self, self.app, "clear_infobox", "Prečisti",
                                    DEFAULT_BUTTON_COLOR, "medium")
        self.infobox_ui_group = UserInterface([self.clear_infobox], 60, 670, 0)
        self.previous_step = Button(self, self.app, "prev_step", "<", DEFAULT_BUTTON_COLOR, "extra_small")
        self.next_step = Button(self, self.app, "next_step", ">", DEFAULT_BUTTON_COLOR, "extra_small")
        self.action_arrows_ui_group = UserInterface([self.previous_step, self.next_step],
                                                    135, 670, 42)
        self.export_graph_button = Button(self, self.app, "export_graph",
                                          "Export grafu", DEFAULT_BUTTON_COLOR)
        self.import_graph_button = Button(self, self.app, "import_graph",
                                          "Import grafu", DEFAULT_BUTTON_COLOR)
        self.autotest_button = Button(self, self.app, "autotest", 
                                      "Autotesty", DEFAULT_BUTTON_COLOR)
        self.top_left_ui_group = UserInterface([self.export_graph_button,
                                                self.import_graph_button,
                                                self.autotest_button], 20, 20, 110)
        self.infobox = Infobox(self.app, 240, 610, 20, 50)
        self.canvas.tag_bind(VERTEX_TAG, "<Button-3>", self.app.edit_vertex)
        self.canvas.tag_bind(EDGE_TAG, "<Button-3>", self.app.edit_edge)