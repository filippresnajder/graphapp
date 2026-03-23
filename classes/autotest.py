import tkinter as tk

from classes.button import Button
from classes.user_interface import UserInterface
from classes.question_box import QuestionBox
from classes.answer_box import AnswerBox
from constants import (DEFAULT_BUTTON_COLOR)

class Autotest(tk.Frame):
    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.button_gap = 120
        self.back_to_main_menu_button = Button(self,
                                               self.app,
                                               "back_to_main_menu",
                                               "Hlavné menu",
                                               DEFAULT_BUTTON_COLOR,
                                               "extra_large")
        self.next_question_button = Button(self,
                                          self.app,
                                          "next_question",
                                          "Ďalšia otázka",
                                          DEFAULT_BUTTON_COLOR,
                                          "extra_large")
        self.autotest_ui_buttons = UserInterface([self.back_to_main_menu_button,
                                                  self.next_question_button],
                                                  460, 680, 220)
        self.correct_answers = []
        self.user_answers = []
        self.current_index = 0
        self.questions = []
        self.question_box = None
        self.answer_box = None
        self.is_finished = False
        self.score = 0
        self.maximum_score = 0

    def show_question(self):
        if self.question_box:
            self.question_box.destroy()

        question = self.questions[self.current_index]
        self.question_box = QuestionBox(self, question)

        self.__show_answers()

    def __show_answers(self):
        if self.answer_box:
            self.answer_box.destroy()

        answers = self.questions[self.current_index]["answers"]
        question_type = self.questions[self.current_index]["type"]
        self.answer_box = AnswerBox(self.question_box,
                                    answers,
                                    question_type,
                                    self.is_finished,
                                    self.user_answers if self.is_finished else None)
