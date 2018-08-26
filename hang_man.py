from Tkinter import *
import random
import ttk


class Hangman(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.top_frame = Frame()
        self.top_frame.grid(row=0, column=0)
        self.middle_frame = Frame()
        self.middle_frame.grid(row=1, column=0)
        self.bottom_frame = Frame()
        self.bottom_frame.grid(row=2, column=0)

        game_font = 'gothic'
        self.submit_button = Button(self.bottom_frame, text='Submit Guess', bg='darkgreen', fg='white', font=game_font+' 20 bold', command=self.been_clicked)
        self.submit_button.grid()

        self.user_choice = StringVar()
        self.user_choice.set(None)
        all_letters = 'abcdefghijklmnopqrstuvwxyz'
        for letter in all_letters:
            self.letter_radio_button = Radiobutton(self.middle_frame, text=letter.upper(), value=letter,
                                                   variable=self.user_choice, width=4, height=2, indicatoron=0,
                                                   font=game_font+' 12 bold')
            if all_letters.index(letter) > (len(all_letters) / 2)-1:
                self.letter_radio_button.grid(row=1, column=all_letters.index(letter)-(len(all_letters) / 2))
            else:
                self.letter_radio_button.grid(row=0, column=all_letters.index(letter))

        self.computer_choice = []
        for x in range(0, 6):
            self.computer_choice.append(random.choice(all_letters))

        col = 0
        for x in self.computer_choice:
            self.reveal = Label(self.top_frame, text=x, fg='white', bg='black')
            self.reveal.grid(row=0, column=col)
            col += 1

    def been_clicked(self):
        for item in self.computer_choice:
            if self.user_choice == item:
                self.reveal.configure(bg='white')



app = Hangman()
app.title('Hangman')
app.mainloop()
