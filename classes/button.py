import tkinter as tk

class Button:
    def __init__(self, app, btn_type, label, x, y):
        self.app = app
        self.btn_type = btn_type
        self.label = label
        self.x = x
        self.y = y
        self.button = tk.Button(self.app.root, text=self.label, font=("Arial", 16), command=self.onclick)
        self.button.place(x=self.x, y=self.y)

    def onclick(self):
        self.app.state = self.btn_type
        self.app.canvas.unbind("<B1-Motion>")
        self.app.canvas.unbind("<ButtonRelease-1>")
        if (self.app.state == "add_vertex"):
            self.app.canvas.bind("<Button-1>", self.app.create_vertex)
        elif(self.app.state == "move_vertex"):
            self.app.canvas.bind("<Button-1>", self.app.start_move_vertex)
            self.app.canvas.bind("<B1-Motion>", self.app.move_vertex)
            self.app.canvas.bind("<ButtonRelease-1>", self.app.stop_move_vertex)
        elif (self.app.state == "add_edge"):
            self.app.canvas.bind("<Button-1>", self.app.create_edge)
        elif (self.app.state == "dijkstra"):
            self.app.canvas.bind("<Button-1>", self.app.visualize_dijkstra)