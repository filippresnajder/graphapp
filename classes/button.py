import tkinter as tk

button_sizes = {"extra_small": 4,
                "small": 6,
                "medium": 8,
                "large": 12}

class Button:
    def __init__(self, app, btn_type, label, color, size="large"):
        self.app = app
        self.btn_type = btn_type
        self.label = label
        self.size = size
        self.button = tk.Button(self.app.root, bg=color, text=self.label, font=("Arial", 10), width=button_sizes[size], highlightthickness=0, border=0, command=self.onclick)
        self.x = 0
        self.y = 0
        self.visible = True

        # STATE HANDLERS
        self.handlers = {
            "add_vertex": self.__handle_add_vertex,
            "add_edge": self.__handle_add_edge,
            "move_vertex": self.__handle_move_vertex,
            "dijkstra": self.__handle_dijkstra,
            "prim": self.__handle_prim,
            "kruskal": self.__handle_kruskal,
            "dfs": self.__handle_dfs,
            "bfs": self.__handle_bfs,
            "clear_infobox": self.__handle_clear_infobox,
            "prev_step": self.__handle_prev_step,
            "next_step": self.__handle_next_step,
            "show_algorithms": self.__handle_show_algorithms,
            "show_algorithms_info": self.__handle_show_algorithms_info,
            "dijkstra_info": self.__handle_dijkstra_info,
            "prim_info": self.__handle_prim_info,
            "kruskal_info": self.__handle_kruskal_info,
            "dfs_info": self.__handle_dfs_info,
            "bfs_info": self.__handle_bfs_info
        } 

    def place(self, x, y):
        self.x = x
        self.y = y
        if self.visible:
            self.button.place(x=self.x, y=self.y)

    def show(self):
        self.visible = True
        self.button.place(x=self.x, y=self.y)

    def hide(self):
        self.visible = False
        self.button.place_forget()

    def onclick(self):
        self.app.state = self.btn_type

        self.app.canvas.unbind("<B1-Motion>")
        self.app.canvas.unbind("<ButtonRelease-1>")

        self.handlers.get(self.btn_type, lambda: None)()

    # STATE METHODS
    def __handle_add_vertex(self):
        self.app.canvas.bind("<Button-1>", self.app.create_vertex)
    
    def __handle_add_edge(self):
        self.app.canvas.bind("<Button-1>", self.app.create_edge)

    def __handle_move_vertex(self):
        self.app.canvas.bind("<Button-1>", self.app.start_move_vertex)
        self.app.canvas.bind("<B1-Motion>", self.app.move_vertex)
        self.app.canvas.bind("<ButtonRelease-1>", self.app.stop_move_vertex)

    def __handle_dijkstra(self):
        if self.app.vertices and self.app.edges:
            self.app.infobox.clear()
            self.app.infobox.log("Vyber začiatočný a konečný vrchol kliknutím")
            self.app.canvas.bind("<Button-1>", self.app.visualize_dijkstra)
        self.app.close_dropdown(self.app.algorithm_dropdown)
        self.app.close_dropdown(self.app.algorithm_info_dropdown)

    def __handle_prim(self):
        if self.app.vertices and self.app.edges:
            self.app.infobox.clear()
            self.app.infobox.log("Vyber začiatočný vrchol kliknutím")
            self.app.canvas.bind("<Button-1>", self.app.visualize_prim)
        self.app.close_dropdown(self.app.algorithm_dropdown)
        self.app.close_dropdown(self.app.algorithm_info_dropdown)

    def __handle_kruskal(self):
        if self.app.vertices and self.app.edges:
            self.app.visualize_kruskal()
        self.app.close_dropdown(self.app.algorithm_dropdown)
        self.app.close_dropdown(self.app.algorithm_info_dropdown)

    def __handle_dfs(self):
        if self.app.vertices and self.app.edges:
            self.app.infobox.clear()
            self.app.infobox.log("Vyber začiatočný vrchol kliknutím")
            self.app.canvas.bind("<Button-1>", self.app.visualize_dfs)
        self.app.close_dropdown(self.app.algorithm_dropdown)
        self.app.close_dropdown(self.app.algorithm_info_dropdown)

    def __handle_bfs(self):
        if self.app.vertices and self.app.edges:
            self.app.infobox.clear()
            self.app.infobox.log("Vyber začiatočný vrchol kliknutím")
            self.app.canvas.bind("<Button-1>", self.app.visualize_bfs)
        self.app.close_dropdown(self.app.algorithm_dropdown)
        self.app.close_dropdown(self.app.algorithm_info_dropdown)

    def __handle_clear_infobox(self):
        self.app.infobox.clear()

    def __handle_prev_step(self):
        self.app.show_algorithm_step(False)

    def __handle_next_step(self):
        self.app.show_algorithm_step(True)     

    def __handle_show_algorithms(self):
        self.app.algorithm_dropdown.change_dropdown_state()

    def __handle_show_algorithms_info(self):
        self.app.algorithm_info_dropdown.change_dropdown_state()
    
    def __handle_dijkstra_info(self):
        self.app.algorithms.dijkstra_info()
        self.app.close_dropdown(self.app.algorithm_dropdown)
        self.app.close_dropdown(self.app.algorithm_info_dropdown)

    def __handle_prim_info(self):
        self.app.algorithms.prim_info()
        self.app.close_dropdown(self.app.algorithm_dropdown)
        self.app.close_dropdown(self.app.algorithm_info_dropdown)

    def __handle_kruskal_info(self):
        self.app.algorithms.kruskal_info()
        self.app.close_dropdown(self.app.algorithm_dropdown)
        self.app.close_dropdown(self.app.algorithm_info_dropdown)

    def __handle_dfs_info(self):
        self.app.algorithms.dfs_info()
        self.app.close_dropdown(self.app.algorithm_dropdown)
        self.app.close_dropdown(self.app.algorithm_info_dropdown)

    def __handle_bfs_info(self):
        self.app.algorithms.bfs_info()
        self.app.close_dropdown(self.app.algorithm_dropdown)
        self.app.close_dropdown(self.app.algorithm_info_dropdown)