import tkinter as tk
import os
from PIL import ImageTk, Image

from constants import (DEFAULT_BUTTON_COLOR, NUM_AUTOTEST_QUESTION)

class QuestionBox(tk.Frame):
    def __init__(self, parent, question):
        super().__init__(parent)
        self.parent = parent
        self.img = None

        if question["image"]:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            path = os.path.join(base_dir, "autotest", "questions", "images", question["image"])
            image = Image.open(path)
            resized_image = image.resize((355, 200))
            self.img = ImageTk.PhotoImage(resized_image)

        self.pack(padx=0, pady=80 if self.img else 160)
        show_info_string = "Otázka " + str(self.parent.current_index+1) + "/" + str(NUM_AUTOTEST_QUESTION) + ("\n Test bol ukončený, váš počet bodov je " + str(self.parent.score) + " z " + str(self.parent.maximum_score) + "." if self.parent.is_finished else "")
        self.show_info = tk.Label(self, text=show_info_string)
        self.show_info.pack(padx=0, pady=0)
        self.image = tk.Label(self, image = self.img)
        self.image.pack(padx=0, pady=0)
        self.label = tk.Label(self,
                              text=question["question"],
                              width=50,
                              height=10,
                              wraplength=200,
                              bg=DEFAULT_BUTTON_COLOR)
        self.label.pack(padx=0, pady=0)