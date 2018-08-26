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
        for x in range(0, random.randrange(6, 10)):
            self.computer_choice.append(random.choice(all_letters.upper()))

        print self.computer_choice

        self.cpu_choice_str1 = StringVar()
        self.cpu_choice_str1.set('_')
        self.cpu_choice_str2 = StringVar()
        self.cpu_choice_str2.set('_')
        self.cpu_choice_str3 = StringVar()
        self.cpu_choice_str3.set('_')
        self.cpu_choice_str4 = StringVar()
        self.cpu_choice_str4.set('_')
        self.cpu_choice_str5 = StringVar()
        self.cpu_choice_str5.set('_')
        self.cpu_choice_str6 = StringVar()
        self.cpu_choice_str6.set('_')
        self.cpu_choice_str7 = StringVar()
        self.cpu_choice_str7.set('_')
        self.cpu_choice_str8 = StringVar()
        self.cpu_choice_str8.set('_')
        self.cpu_choice_str9 = StringVar()
        self.cpu_choice_str9.set('_')
        self.cpu_choice_str10 = StringVar()
        self.cpu_choice_str10.set('_')

        self.options = [
            (0, self.cpu_choice_str1),
            (1, self.cpu_choice_str2),
            (2, self.cpu_choice_str3),
            (3, self.cpu_choice_str4),
            (4, self.cpu_choice_str5),
            (5, self.cpu_choice_str6),
            (6, self.cpu_choice_str7),
            (7, self.cpu_choice_str8),
            (8, self.cpu_choice_str9),
            (9, self.cpu_choice_str10),
        ]

        for col, text in self.options[:len(self.computer_choice)]:
            self.reveal = Label(self.top_frame, textvariable=text, fg='black', bg='white', font=game_font+' 20 bold')
            self.reveal.grid(row=0, column=col)

    def been_clicked(self):
        for item in self.computer_choice:
            if self.user_choice.get().upper() == item:
                item_loc = self.computer_choice.index(item)
                self.options[item_loc][1].set(item)



app = Hangman()
app.title('Hangman')
app.mainloop()
