from tkinter import *
from random import choice


class MemoryMatch(Tk):

    def __init__(self):
        Tk.__init__(self)

        self.title('Memory Match')
        self.count = 0
        self.chances_taken = 0
        self.default_font = "Gothic"
        self.difficulty = None
        self.difficulty_options = {'Normal': {'squares': 4,
                                              'chances': 8},
                                   'Expert': {'squares': 6,
                                              'chances': 18}}
        squares = 4
        possible_colors = [
            # Colors
            'green', 'dark green', 'lime green', 'red', 'maroon', 'pink', 'brown',
            'orange', 'yellow', 'dark blue', 'blue', 'light blue', 'teal', 'purple', 'violet',
            # Shades
            'black', '#444444', '#888888'
            ]
        for d, info in self.difficulty_options.items():
            b = Button(self, text=d, bg='green', fg='white', font=f'{self.default_font} 20 bold')
            b.config(command=lambda x=(possible_colors,
                                       info['squares'],
                                       info['chances'],
                                       b): self.start_app(x[0], x[1], x[2]))
            b.pack(side=LEFT, padx=10, pady=10)

    def start_app(self, possible_colors, squares, chances):
        for info, widget in self.children.items():
            widget.pack_forget()

        self.chances = chances
        self.app_frame = Label(self, bg='white', relief=SUNKEN)
        self.app_frame.pack(expand=True)
        self.status_frame = Frame(self.app_frame)
        self.status_frame.pack(expand=True, fill=X)
        self.main_frame = Label(self.app_frame, bg='light grey', relief=GROOVE)
        self.main_frame.pack(padx=6, pady=6)
        self.status_text = 'You have %s chances left'
        self.status_bar = Label(self.status_frame, text=self.status_text % self.chances,
                                font=f'{self.default_font} 12 bold',
                                bg='white', relief=SUNKEN)
        self.status_bar.pack(side=LEFT, expand=True, fill=BOTH)
        self.restart_button = Button(self.status_frame, text='Restart',
                                     font=f'{self.default_font} 20 bold', bg='green', fg='white',
                                     command=lambda items=(possible_colors, squares): self.restart(items[0], items[1]))
        # Choose a color for every two squares
        chosen_colors = []
        while len(chosen_colors) < squares * squares / 2:
            color_choice = choice(possible_colors)
            if color_choice not in chosen_colors:
                chosen_colors.append(color_choice)
        # Create buttons and assign colors to them from the chosen colors
        assigned_colors = {c: 0 for c in chosen_colors}
        self.buttons_color = {}
        for x, y in [(x, y) for x in range(squares) for y in range(squares)]:
            b_color = choice(chosen_colors)
            while assigned_colors[b_color] == 2:
                b_color = choice(chosen_colors)
            b = Button(self.main_frame, text=' ', width=20, height=8, bg='white', relief=RAISED)
            b.config(command=lambda button=b: self.on_select(button))
            b.grid(row=x, column=y, padx=6, pady=6)
            if b not in self.buttons_color:
                self.buttons_color[b] = {}
            self.buttons_color[b]['color'] = b_color
            self.buttons_color[b]['state'] = NORMAL
            assigned_colors[b_color] += 1

    def on_select(self, button):
        """ Compares the first button selected to the second button selected.
            If the second button selected is the same as the first, the buttons will be disabled and remain.
            If the second button selected is different than the first, the buttons will be reset."""
        button.config(bg=self.buttons_color[button]['color'])
        # First button selected
        if self.count < 1:
            self.first_color = self.buttons_color[button]['color']
            self.first_button = button
            self.count += 1
        # Second button selected
        else:
            self.second_color = self.buttons_color[button]['color']
            self.second_button = button
            self.enable_disable_buttons(state=DISABLED)
            if self.first_color != self.second_color:
                self.after(500, func=self.reset_buttons)
                self.chances_taken += 1
                self.status_bar.config(
                    text=self.status_text % (self.chances - self.chances_taken) + ''.join(['.' for x in range(self.chances_taken)]),
                    font=f'{self.default_font} {12 + self.chances_taken} bold')
                if self.chances - self.chances_taken == 3:
                    self.status_bar.config(fg='#999900')
                elif self.chances - self.chances_taken == 2:
                    self.status_bar.config(fg='dark orange')
                elif self.chances - self.chances_taken == 1:
                    self.status_bar.config(fg='red')
                elif self.chances - self.chances_taken == 0:
                    self.status_bar.config(text='YOU LOSE BRUH', font=f'{self.default_font} 22 bold')
                    self.restart_button.pack(side=LEFT)
                # Game over
                if self.chances_taken == self.chances:
                    for b, info in self.buttons_color.items():
                        self.after(500, func=lambda x=(b, info['color']): x[0].config(bg=x[1], state=DISABLED))
            else:
                for b in [self.first_button, self.second_button]:
                    b.config(state=DISABLED)
                    self.buttons_color[b]['state'] = DISABLED
                if not [x for x, info in self.buttons_color.items() if info['state'] != DISABLED]:
                    # WINNER
                    self.status_bar.config(text='YOU HAVE DONE IT, CONGRATS!!!!',
                                           font=f'{self.default_font} 22 bold', fg='dark green')
                    self.restart_button.pack(side=LEFT)
                else:
                    self.enable_disable_buttons(state=NORMAL)

            self.count = 0

    def reset_buttons(self):
        self.first_button.config(bg='white')
        self.second_button.config(bg='white')
        self.enable_disable_buttons(state=NORMAL)

    def restart(self, options, squares):
        # Choose a color for every two squares
        chosen_colors = []
        while len(chosen_colors) < squares * squares / 2:
            color_choice = choice(options)
            if color_choice not in chosen_colors:
                chosen_colors.append(color_choice)
        # Assign colors to buttons from the chosen colors
        assigned_colors = {c: 0 for c in chosen_colors}
        new_button_color = self.buttons_color
        for button, info in self.buttons_color.items():
            b_color = choice(chosen_colors)
            while assigned_colors[b_color] == 2:
                b_color = choice(chosen_colors)
            assigned_colors[b_color] += 1
            new_button_color[button]['color'] = b_color
            new_button_color[button]['state'] = NORMAL
            button.config(bg='white', state='normal')
        self.buttons_color = new_button_color
        self.restart_button.pack_forget()
        self.status_bar.config(text=self.status_text % self.chances, fg='black', font=f'{self.default_font} 12')
        self.chances_taken = 0

    def enable_disable_buttons(self, state=DISABLED):
        for button in [b for b, info in self.buttons_color.items() if info['state'] != DISABLED]:
            button.config(state=state)


app = MemoryMatch()
app.mainloop()
