import tkinter as tk

STATE = 0

def set_state(num):
    global STATE
    STATE = num
    if STATE == 1:
        canvas.bind("<Button-1>", create_vertex)
    elif STATE == 2:
        canvas.bind("<Button-1>", create_edge)

def create_vertex(event):
    if STATE == 1:
        x, y = event.x, event.y
        canvas.create_oval(x-10,y-10,x+10,y+10,fill="blue",outline="black")

def create_edge(event):
    if STATE == 2:
        x, y = event.x, event.y
        canvas.create_line(x,y,x+20,y+20,fill="black")

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