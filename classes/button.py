import tkinter as tk

class Button:
    def __init__(self, app, btn_type, label, color, size="normal"):
        self.app = app
        self.btn_type = btn_type
        self.label = label
        self.size = size
        self.button = tk.Button(self.app.root, bg=color, text=self.label, font=("Arial", 10), width=6 if self.size == "small" else 12, highlightthickness=0, border=0, command=self.onclick)
        self.x = 0
        self.y = 0
        self.visible = True

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
        if (self.app.state == "add_vertex"):
            self.app.canvas.bind("<Button-1>", self.app.create_vertex)
        elif (self.app.state == "move_vertex"):
            self.app.canvas.bind("<Button-1>", self.app.start_move_vertex)
            self.app.canvas.bind("<B1-Motion>", self.app.move_vertex)
            self.app.canvas.bind("<ButtonRelease-1>", self.app.stop_move_vertex)
        elif (self.app.state == "add_edge"):
            self.app.canvas.bind("<Button-1>", self.app.create_edge)
        elif (self.app.state == "dijkstra"):
            if self.app.vertices and self.app.edges:
                self.app.infobox.clear()
                self.app.infobox.log("Vyber začiatočný a konečný vrchol kliknutím")
            self.app.canvas.bind("<Button-1>", self.app.visualize_dijkstra)
            self.app.close_dropdown(self.app.algorithm_dropdown)
        elif (self.app.state == "prim"):
            if self.app.vertices and self.app.edges:
                self.app.infobox.clear()
                self.app.infobox.log("Vyber začiatočný vrchol kliknutím")
            self.app.canvas.bind("<Button-1>", self.app.visualize_prim)
            self.app.close_dropdown(self.app.algorithm_dropdown)
        elif (self.app.state == "kruskal"):
            self.app.visualize_kruskal()
            self.app.close_dropdown(self.app.algorithm_dropdown)
        elif (self.app.state == "dfs"):
            if self.app.vertices and self.app.edges:
                self.app.infobox.clear()
                self.app.infobox.log("Vyber začiatočný vrchol kliknutím")
            self.app.canvas.bind("<Button-1>", self.app.visualize_dfs)
            self.app.close_dropdown(self.app.algorithm_dropdown)
        elif (self.app.state == "bfs"):
            if self.app.vertices and self.app.edges:
                self.app.infobox.clear()
                self.app.infobox.log("Vyber začiatočný vrchol kliknutím")
            self.app.canvas.bind("<Button-1>", self.app.visualize_bfs)
            self.app.close_dropdown(self.app.algorithm_dropdown)
        elif (self.app.state == "clear_infobox"):
            self.app.infobox.clear()
        elif (self.app.state == "prev_step"):
            self.app.show_algorithm_step(False)
        elif (self.app.state == "next_step"):
            self.app.show_algorithm_step(True)
        elif (self.app.state == "show_algorithms"):
            self.app.algorithm_dropdown.change_dropdown_state()