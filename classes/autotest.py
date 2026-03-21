import tkinter as tk

from classes.button import Button
from classes.user_interface import UserInterface
from constants import (DEFAULT_BUTTON_COLOR)

class Autotest(tk.Frame):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.back_to_main_menu_button = Button(self, self.app, "back_to_main_menu", "Choď späť", DEFAULT_BUTTON_COLOR)
        self.top_left_ui_group = UserInterface([self.back_to_main_menu_button],
                                               20, 20, 110)