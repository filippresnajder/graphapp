class UserInterface:
    def __init__(self, buttons, start_x, start_y, gap, dropdown=False):
        self.buttons = buttons
        self.start_x = start_x
        self.start_y = start_y
        self.gap = gap
        self.dropdown = dropdown
        self.expanded = False
        self.__build_ui()

    def __build_ui(self):
        if not self.dropdown:
            for index, button in enumerate(self.buttons):
                button.place(self.start_x+(index * self.gap), self.start_y)
            return
        
        for index, button in enumerate(self.buttons):
            button.place(self.start_x, self.start_y+(index * self.gap))
            if index != 0:
                button.hide()

    def change_dropdown_state(self):
        if self.expanded:
            for index, button in enumerate(self.buttons):
                if index != 0:
                    button.hide()
            self.expanded = False
            return
        
        for index, button in enumerate(self.buttons):
            if index != 0:
                button.show()
        self.expanded = True
    
