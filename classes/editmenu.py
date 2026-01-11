import tkinter as tk
from tkinter import colorchooser
from tkinter import messagebox
from constants import (DEFAULT_WIDTH, DEFAULT_BG_COLOR, DEFAULT_UI_TEXT_COLOR, DEFAULT_BUTTON_COLOR,
                        DEFAULT_OUTLINE_COLOR, DEFAULT_TEXT_COLOR)
from classes.edge import Edge

class EditMenu:
    def __init__(self, app):
        self.app = app

    def render_add_edge_menu(self, event, v1, v2):
        popup = tk.Toplevel(self.app.root, background=DEFAULT_BG_COLOR)
        popup.resizable(False, False)
        popup.title("Pridať hranu")
        popup.geometry("250x100+{}+{}".format(event.x_root, event.y_root))

        weight_val_frame = tk.Frame(popup, background=DEFAULT_BG_COLOR)
        weight_val_frame.pack(pady=5)
        tk.Label(weight_val_frame, text="Váha hrany:", background=DEFAULT_BG_COLOR, foreground=DEFAULT_UI_TEXT_COLOR).pack(side="left", padx=3)
        entry = tk.Entry(weight_val_frame, width=5)
        entry.insert(0, "0")
        entry.pack(side="right", padx=3)

        popup.is_oriented = tk.StringVar(value="no")
        edit_all_edges_button = tk.Checkbutton(popup, variable=popup.is_oriented, text="Hrana je orientovaná", 
                                                  onvalue="yes", offvalue="no", background=DEFAULT_BG_COLOR, foreground=DEFAULT_UI_TEXT_COLOR,
                                                  activebackground=DEFAULT_BG_COLOR, selectcolor=DEFAULT_BG_COLOR)
        edit_all_edges_button.pack(pady=5)

        def save():
            try:
                weight = int(entry.get())
            except:
                messagebox.showerror(parent=popup, title="Chyba", message="Váha hrany musí byť číselná hodnota.")
                return

            edge = Edge(self.app, DEFAULT_OUTLINE_COLOR, DEFAULT_OUTLINE_COLOR, DEFAULT_TEXT_COLOR, DEFAULT_WIDTH, weight, popup.is_oriented.get(), v1, v2)
            self.app.edges.append(edge)
            v1.edges.append(edge)
            v2.edges.append(edge)
            self.app.canvas_id_to_edge[edge.canvas_object_id] = edge
            self.app.canvas_id_to_edge[edge.canvas_text] = edge
            self.app.canvas_id_to_edge[edge.canvas_text_bg] = edge
            popup.destroy()
        
        def close():
            popup.destroy()
            return None

        button_frame = tk.Frame(popup, background=DEFAULT_BG_COLOR)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="Zavrieť", command=close, background=DEFAULT_BUTTON_COLOR, foreground=DEFAULT_UI_TEXT_COLOR).pack(side="left", padx=3)
        tk.Button(button_frame, text="Vytvoriť", command=save, background=DEFAULT_BUTTON_COLOR, foreground=DEFAULT_UI_TEXT_COLOR).pack(side="right", padx=3) 

    def render_edge_edit_menu(self, event, edge):
        popup = tk.Toplevel(self.app.root, background=DEFAULT_BG_COLOR)
        popup.resizable(False, False)
        popup.title("Edit")
        popup.geometry("250x220+{}+{}".format(event.x_root, event.y_root))

        # Pomocná funkcia, ktorá využíva tkinter colorchoose na edit farieb
        def change_color(obj_type):
            color = colorchooser.askcolor(parent=popup)[1]
            if obj_type == "line":
                line_col_button["bg"] = color
            elif obj_type == "box":
                box_col_button["bg"] = color
            elif obj_type == "weight":
                text_col_button["bg"] = color

        # Skupina slúžiacia na edit váhy hrany
        weight_val_frame = tk.Frame(popup, background=DEFAULT_BG_COLOR)
        weight_val_frame.pack(pady=5)
        tk.Label(weight_val_frame, text="Váha hrany:", background=DEFAULT_BG_COLOR, foreground=DEFAULT_UI_TEXT_COLOR).pack(side="left", padx=3)
        entry = tk.Entry(weight_val_frame, width=5)
        entry.insert(0, str(edge.weight))
        entry.pack(side="right", padx=3)

        # Skupina slúžiacia na edit farby čiary hrany
        line_col_frame = tk.Frame(popup, background=DEFAULT_BG_COLOR)
        line_col_frame.pack(pady=5)
        line_col_label = tk.Label(line_col_frame, text="Farba čiary:", background=DEFAULT_BG_COLOR, foreground=DEFAULT_UI_TEXT_COLOR)
        line_col_button = tk.Button(line_col_frame, bg=edge.line_color, width=DEFAULT_WIDTH, command=lambda: change_color("line"))
        line_col_label.pack(side="left", padx=3)
        line_col_button.pack(side="right", padx=3)

        # Skupina slúžiacia na edit farby okraja
        box_col_frame = tk.Frame(popup, background=DEFAULT_BG_COLOR)
        box_col_frame.pack(pady=5)
        box_col_label = tk.Label(box_col_frame, text="Farba okraja:", background=DEFAULT_BG_COLOR, foreground=DEFAULT_UI_TEXT_COLOR)
        box_col_button = tk.Button(box_col_frame, bg=edge.box_color, width=DEFAULT_WIDTH, command=lambda: change_color("box"))
        box_col_label.pack(side="left", padx=3)
        box_col_button.pack(side="right", padx=3)

        # Skupina slúžiacia na edit farby textu váhy
        text_col_frame = tk.Frame(popup, background=DEFAULT_BG_COLOR)
        text_col_frame.pack(pady=5)
        text_col_label = tk.Label(text_col_frame, text="Farba textu:", background=DEFAULT_BG_COLOR, foreground=DEFAULT_UI_TEXT_COLOR)
        text_col_button = tk.Button(text_col_frame, bg=edge.weight_color, width=DEFAULT_WIDTH, command=lambda: change_color("weight"))
        text_col_label.pack(side="left", padx=3)
        text_col_button.pack(side="right", padx=3)

        popup.edit_all_edges_var = tk.IntVar(value=0)
        edit_all_edges_button = tk.Checkbutton(popup, variable=popup.edit_all_edges_var, text="Zmeniť farbu pre všetky hrany", 
                                                  onvalue=1, offvalue=0, background=DEFAULT_BG_COLOR, foreground=DEFAULT_UI_TEXT_COLOR,
                                                  activebackground=DEFAULT_BG_COLOR, selectcolor=DEFAULT_BG_COLOR)
        edit_all_edges_button.pack(pady=5)

        # Pomocná funkcia, využívaná pre ukladanie editov na vrchol
        def save():
            try:
                edge.weight = int(entry.get())
            except:
                messagebox.showerror(parent=popup, title="Chyba", message="Váha hrany musí byť číselná hodnota.")
                return
            if popup.edit_all_edges_var.get() == 1:
                for e in self.app.edges:
                    e.line_color, e.box_color, e.weight_color = line_col_button["bg"], box_col_button["bg"], text_col_button["bg"]
                    self.app.canvas.itemconfig(e.canvas_object_id, fill=e.line_color)
                    self.app.canvas.itemconfig(e.canvas_text_bg, outline=e.box_color)
                    self.app.canvas.itemconfig(e.canvas_text, fill=e.weight_color, text=e.weight)
                popup.destroy()
                return
            edge.line_color, edge.box_color, edge.weight_color = line_col_button["bg"], box_col_button["bg"], text_col_button["bg"]
            self.app.canvas.itemconfig(edge.canvas_object_id, fill=edge.line_color)
            self.app.canvas.itemconfig(edge.canvas_text_bg, outline=edge.box_color)
            self.app.canvas.itemconfig(edge.canvas_text, fill=edge.weight_color, text=edge.weight)
            popup.destroy()

        button_frame = tk.Frame(popup, background=DEFAULT_BG_COLOR)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="Zavrieť", command=popup.destroy, background=DEFAULT_BUTTON_COLOR, foreground=DEFAULT_UI_TEXT_COLOR).pack(side="left", padx=3)
        tk.Button(button_frame, text="Uložiť", command=save, background=DEFAULT_BUTTON_COLOR, foreground=DEFAULT_UI_TEXT_COLOR).pack(side="right", padx=3)      

    def render_vertex_edit_menu(self, event, vertex):
        popup = tk.Toplevel(self.app.root, background=DEFAULT_BG_COLOR)
        popup.resizable(False, False)
        popup.title("Edit")
        popup.geometry("250x220+{}+{}".format(event.x_root, event.y_root))

        # Pomocná funkcia, ktorá využíva tkinter colorchoose na edit farieb
        def change_color(obj_type):
            color = colorchooser.askcolor(parent=popup)[1]
            if obj_type == "fill":
                change_fill_color["bg"] = color
            elif obj_type == "outline":
                change_outline_color["bg"] = color
            elif obj_type == "text":
                change_text_color["bg"] = color

        # Vytvorenie skupiny, ktorá drží zmenu názvu vrchola
        tag_frame = tk.Frame(popup, background=DEFAULT_BG_COLOR)
        tag_frame.pack(pady=5)
        tk.Label(tag_frame, text="Názov hrany:", background=DEFAULT_BG_COLOR, foreground=DEFAULT_UI_TEXT_COLOR).pack(side="left", padx=3)
        entry = tk.Entry(tag_frame, width=5)
        entry.insert(0, str(vertex.tag))
        entry.pack(side="right", padx=3)

        # Vytvorenie skupiny, ktorá drží zmenu výplne vrchola
        fill_frame = tk.Frame(popup, background=DEFAULT_BG_COLOR)
        fill_frame.pack(pady=5)
        fill_frame_label = tk.Label(fill_frame, text="Farba výplne:", background=DEFAULT_BG_COLOR, foreground=DEFAULT_UI_TEXT_COLOR)
        change_fill_color = tk.Button(fill_frame, bg=vertex.fill_color, width=DEFAULT_WIDTH, command=lambda: change_color("fill"))
        fill_frame_label.pack(side="left", padx=3)
        change_fill_color.pack(side="right", padx=3)

        # Vytvorenie skupiny, ktorá drží zmenu okraja vrchola
        outline_frame = tk.Frame(popup, background=DEFAULT_BG_COLOR)
        outline_frame.pack(pady=5)
        outline_frame_label = tk.Label(outline_frame, text="Farba okraja:", background=DEFAULT_BG_COLOR, foreground=DEFAULT_UI_TEXT_COLOR)
        change_outline_color = tk.Button(outline_frame, bg=vertex.outline_color, width=DEFAULT_WIDTH, command=lambda: change_color("outline"))
        outline_frame_label.pack(side="left", padx=3)
        change_outline_color.pack(side="right", padx=3)

        # Vytvorenie skupiny, ktorá drží zmenu farby textu vrchola
        text_frame = tk.Frame(popup, background=DEFAULT_BG_COLOR)
        text_frame.pack(pady=5)
        text_frame_label = tk.Label(text_frame, text="Farba textu:", background=DEFAULT_BG_COLOR, foreground=DEFAULT_UI_TEXT_COLOR)
        change_text_color = tk.Button(text_frame, bg=vertex.text_color, width=DEFAULT_WIDTH, command=lambda: change_color("text"))
        text_frame_label.pack(side="left", padx=3)
        change_text_color.pack(side="right", padx=3)

        popup.edit_all_vertices_var = tk.IntVar(value=0)
        edit_all_vertices_button = tk.Checkbutton(popup, variable=popup.edit_all_vertices_var, text="Zmeniť farbu pre všetky vrcholy", 
                                                  onvalue=1, offvalue=0, background=DEFAULT_BG_COLOR, foreground=DEFAULT_UI_TEXT_COLOR,
                                                  activebackground=DEFAULT_BG_COLOR, selectcolor=DEFAULT_BG_COLOR)
        edit_all_vertices_button.pack(pady=5)

        # Pomocná funkcia, využívaná pre ukladanie editov na vrchol
        def save():
            vertex.tag = entry.get()
            if popup.edit_all_vertices_var.get() == 1:
                for v in self.app.vertices:
                    v.fill_color, v.outline_color, v.text_color = change_fill_color["bg"], change_outline_color["bg"], change_text_color["bg"]
                    self.app.canvas.itemconfig(v.canvas_object_id, fill=v.fill_color, outline=v.outline_color)
                    self.app.canvas.itemconfig(v.canvas_text, fill=v.text_color, text=v.tag)
                popup.destroy()
                return
            vertex.fill_color, vertex.outline_color, vertex.text_color = change_fill_color["bg"], change_outline_color["bg"], change_text_color["bg"]
            self.app.canvas.itemconfig(vertex.canvas_object_id, fill=vertex.fill_color, outline=vertex.outline_color)
            self.app.canvas.itemconfig(vertex.canvas_text, fill=vertex.text_color, text=vertex.tag[0:3])
            popup.destroy()

        button_frame = tk.Frame(popup, background=DEFAULT_BG_COLOR)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="Zavrieť", command=popup.destroy, background=DEFAULT_BUTTON_COLOR, foreground=DEFAULT_UI_TEXT_COLOR).pack(side="left", padx=3)
        tk.Button(button_frame, text="Uložiť", command=save, background=DEFAULT_BUTTON_COLOR, foreground=DEFAULT_UI_TEXT_COLOR).pack(side="right", padx=3)      