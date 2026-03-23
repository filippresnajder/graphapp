import tkinter as tk

from constants import (DEFAULT_BUTTON_COLOR, DEFAULT_CORRECT_ANSWER,
                       DEFAULT_INCORRECT_ANSWER)

class AnswerBox(tk.Frame):
    def __init__(self, parent, answers, question_type, test_is_finished, user_answers=None):
        super().__init__(parent)
        self.pack(padx=0, pady=10)
        self.answers = answers
        self.question_type = question_type
        self.test_is_finished = test_is_finished

        if self.question_type == "single_choice":
            self.var = tk.IntVar(value=0)
            for ans in self.answers:
                button = tk.Radiobutton(self,
                                        text=ans["text"],
                                        variable = self.var,
                                        value=ans["id"],
                                        width=46,
                                        bg=self.__select_bg_color(ans),
                                        anchor="w",
                                        justify="left",
                                        state=self.__select_state(),
                                        padx=5,
                                    )
                if self.test_is_finished:
                    if ans in user_answers:
                        button.select()
                button.pack(padx=0, pady=1)
        elif self.question_type == "multiple_choice":
            self.vars = []
            for ans in self.answers:
                var = tk.IntVar(value=0)
                button = tk.Checkbutton(
                    self,
                    text=ans["text"],
                    variable=var,
                    width=46,
                    bg=self.__select_bg_color(ans),
                    anchor="w",
                    justify="left",
                    state=self.__select_state(),
                    padx=5
                )
                if self.test_is_finished:
                    if ans in user_answers:
                        button.select()
                button.pack(padx=0, pady=1)
                self.vars.append((ans["id"], var))

    def get_user_answer(self, user_answers):
        if self.test_is_finished:
            return

        if self.question_type == "single_choice":
            answer_id = self.var.get()
            for answer in self.answers:
                if answer["id"] == answer_id:
                    user_answers.append(answer)
        elif self.question_type == "multiple_choice":
            for ans_id, var in self.vars:
                if var.get() == 1:
                    for answer in self.answers:
                        if answer["id"] == ans_id:
                            user_answers.append(answer)

    def __select_bg_color(self, answer):
        if not self.test_is_finished:
            return DEFAULT_BUTTON_COLOR
        
        if answer["correct"]:
            return DEFAULT_CORRECT_ANSWER

        return DEFAULT_INCORRECT_ANSWER

    def __select_state(self):
        if not self.test_is_finished:
            return "normal"
        return "disabled"


