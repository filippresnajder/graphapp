import tkinter as tk

class Infobox:
    def __init__(self, app, width, height, x, y):
        self.app = app
        self.infobox = tk.Text(self.app.root, wrap="word", font=("Arial", 8))
        self.infobox.place(x=x, y=y, width=width, height=height)
        self.infobox.config(state=tk.DISABLED)

    def log(self, text):
        self.infobox.config(state=tk.NORMAL)
        self.infobox.insert(tk.END, text + "\n")
        self.infobox.config(state=tk.DISABLED)
    
    def clear(self):
        self.infobox.config(state=tk.NORMAL)
        self.infobox.delete('1.0', tk.END)
        self.infobox.config(state=tk.DISABLED)
