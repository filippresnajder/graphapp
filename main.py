import tkinter as tk

STATE = 0
RADIUS = 15
selected_vertex = None
vertexes = []
edges = []

def set_state(num):
    global STATE
    STATE = num
    if STATE == 1:
        canvas.bind("<Button-1>", create_vertex)
    elif STATE == 2:
        canvas.bind("<Button-1>", check_if_clicked_on_vertex)

def create_vertex(event):
    if STATE == 1:
        x, y = event.x, event.y
        start_x, start_y, end_x, end_y = x-RADIUS, y-RADIUS, x+RADIUS, y+RADIUS
        canvas.create_oval(start_x, start_y, end_x, end_y, fill="black", outline="black", width=4)
        vertexes.append((start_x, end_x, start_y, end_y))

def create_edge(event, destination_vertex):
    global selected_vertex
    if STATE == 2:
        x, y = event.x, event.y
        canvas.create_line((selected_vertex[0]+selected_vertex[1])/2,(selected_vertex[2]+selected_vertex[3])/2,(destination_vertex[0]+destination_vertex[1])/2,(destination_vertex[2]+destination_vertex[3])/2,fill="black",width=4)
        selected_vertex = None

def check_if_clicked_on_vertex(event):
    global selected_vertex
    x, y = event.x, event.y
    for vertex in vertexes:
        if (event.x >= vertex[0] and event.x <= vertex[1]) and (event.y >= vertex[2] and event.y <= vertex[3]):
            if selected_vertex is None:
                selected_vertex = vertex
            elif selected_vertex == vertex:
                pass
            else:
                create_edge(event, vertex)


# Základné okno
root = tk.Tk()
root.geometry("1280x720")
root.title("GraphApp")

label_selected = tk.Label(root, text="none", font=("Arial", 20))
label_selected.place(x=640, y=360)

button_vertex = tk.Button(root, text="Vrchol", font=("Arial", 16), command=lambda: set_state(1))
button_edge = tk.Button(root, text="Hrana", font=("Arial", 16), command=lambda: set_state(2))

button_vertex.place(x=1000, y=20)
button_edge.place(x=1100, y=20)

canvas = tk.Canvas(root, width=1280, height=640, bg="white")
canvas.place(x=0,y=80)

root.mainloop()