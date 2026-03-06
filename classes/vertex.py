from constants import VERTEX_TAG, RADIUS

class Vertex:
    identifier = 1
    def __init__(self, app, coords, fill_color, outline_color, text_color, width):
        self.app = app
        self.coords = coords
        self.id = Vertex.identifier
        self.tag = self.id
        self.fill_color = fill_color
        self.outline_color = outline_color
        self.text_color = text_color
        self.width = width
        self.edges = []
        self.canvas_object_id = self.app.canvas.create_oval(coords, fill=self.fill_color, outline=self.outline_color, width=width, tags=VERTEX_TAG)
        self.canvas_text = self.app.canvas.create_text(self.get_center_x(), self.get_center_y(), fill=self.text_color, text=self.tag, font=("Arial", 12), tags=VERTEX_TAG)
        self.dfs_bfs_order = self.app.canvas.create_text(self.get_center_x(), self.get_center_y() - (RADIUS * 1.5), fill="", text="", font=("Arial", 12))
        Vertex.identifier += 1

    def is_clicked(self, x, y):
        return ((x >= self.coords[0] and x <= self.coords[2]) and (y >= self.coords[1] and y <= self.coords[3]))
    
    def get_center_x(self):
        return (self.coords[0] + self.coords[2]) / 2
    
    def get_center_y(self):
        return (self.coords[1] + self.coords[3]) / 2
    
    def move_to(self, nx, ny):
        x1, y1, x2, y2 = self.app.canvas.coords(self.canvas_object_id)
        r = (x2 - x1) / 2

        self.coords = (nx-r, ny-r, nx+r, ny+r)
        self.app.canvas.coords(self.canvas_object_id, self.coords)
        self.app.canvas.coords(self.canvas_text, nx, ny)
        self.app.canvas.coords(self.dfs_bfs_order, nx, ny - (RADIUS * 1.5))

        for edge in self.edges:
            if self in edge.vertices:
                edge.update_position()
    
    def update(self, tag, fill, outline, text):
        self.tag = tag[0:20]
        self.fill_color, self.outline_color, self.text_color = fill, outline, text
        self.app.canvas.itemconfig(self.canvas_object_id, fill=self.fill_color, outline=self.outline_color)
        self.app.canvas.itemconfig(self.canvas_text, fill=self.text_color, text=self.tag)
        if self.app.algorithm_state["steps"]:
            self.app.infobox.clear()
            self.app.infobox.log("Nastala zmena v grafe, mažem pamäť krokov predošlého algoritmu")
            self.app.reset_vertices_and_edges(event=None)
        self.app.clear_algorithm_state()

    def delete(self):
        for edge in self.edges[:]:
            edge.delete()

        self.app.canvas.delete(self.canvas_object_id)
        self.app.canvas.delete(self.canvas_text)

        if self in self.app.vertices:
            self.app.vertices.remove(self)

        for cid in (self.canvas_object_id, self.canvas_text):
            self.app.canvas_id_to_vertex.pop(cid, None)

        if self.app.algorithm_state["steps"]:
            self.app.infobox.clear()
            self.app.infobox.log("Nastala zmena v grafe, mažem pamäť krokov predošlého algoritmu")
            self.app.reset_vertices_and_edges(event=None)
        self.app.clear_algorithm_state()

    @staticmethod
    def validate(app, data):
        try:
            return (
                isinstance(data["id"], int)
                and isinstance(data["coords"], list)
                and len(data["coords"]) == 4
                and all(isinstance(coord, float) for coord in data["coords"])
                and app.is_valid_hexadecimal_code(data["fill_color"])
                and app.is_valid_hexadecimal_code(data["outline_color"])
                and app.is_valid_hexadecimal_code(data["text_color"])
                and (isinstance(data["tag"], str))
            )
        except:
            return False