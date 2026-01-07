import tkinter as tk
from classes.button import Button

class App:
    def __init__(self):
        self.state = None
        self.selected_vertex = None
        self.vertices = []
        self.edges = []
        self.root = tk.Tk()
        self.root.geometry("1280x720")
        self.root.title("GraphApp")
        self.add_vertex_button = Button(self,"add_vertex","Add Vertex", 1000, 20)
        self.add_edge_button = Button(self,"add_edge", "Add Edge", 1120, 20)
        self.canvas = tk.Canvas(self.root, width=1280, height=640, bg="white")
        self.canvas.place(x=0,y=80)
        self.root.mainloop()

    def create_vertex(self, event):
        if self.state == "add_vertex":
            x, y = event.x, event.y
            start_x, start_y, end_x, end_y = x-10, y-10, x+10, y+10
            self.canvas.create_oval(start_x, start_y, end_x, end_y, fill="black", outline="black", width=4)
            self.vertices.append((start_x, end_x, start_y, end_y))

    def create_edge(self, event):
        if self.state == "add_edge":
            data = self.__check_if_clicked_on_vertex(event.x, event.y)
            if data != None:
                self.selected_vertex = None
                start_x = (data[0][0] + data[0][1]) / 2
                end_x = (data[1][0] + data[1][1]) / 2
                start_y = (data[0][2] + data[0][3]) / 2 
                end_y = (data[1][2] + data[1][3]) / 2
                self.canvas.create_line(start_x, start_y, end_x, end_y, width=4)
                self.edges.append((start_x, end_x, start_y, end_y))
                print("Súradnice vrcholov:", self.vertices)
                print("Súradnice hrán:", self.edges)

    def __check_if_clicked_on_vertex(self, x, y):
        for vertex in self.vertices:
            if (x >= vertex[0] and x <= vertex[1]) and (y >= vertex[2] and y <= vertex[3]):
                if self.selected_vertex == None:
                    self.selected_vertex = vertex
                elif self.selected_vertex != vertex:
                    return ((self.selected_vertex),(vertex))
        return None
        