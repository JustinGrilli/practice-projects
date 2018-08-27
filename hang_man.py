from Tkinter import *
import random
import ttk
from random_words import RandomWords

class Hangman(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.mistake_max = 8
        self.mistake_count = self.mistake_max

        self.rw = RandomWords()

        self.top_frame = Frame(bg='lightblue')
        self.top_frame.grid(row=0, column=0)
        self.middle_frame = Frame(bg='lightblue')
        self.middle_frame.grid(row=1, column=0)
        self.bottom_frame = Frame(bg='lightblue')
        self.bottom_frame.grid(row=2, column=0)

        game_font = 'gothic'
        self.submit_button = Button(self.bottom_frame, text='Submit Guess', bg='darkgreen', fg='white', font=game_font+' 20 bold', command=self.been_clicked)
        self.submit_button.grid(row=0, column=0, padx=5, pady=5)
        self.submit_button = Button(self.bottom_frame, text='Reset', bg='#444444', fg='white',
                                    font=game_font + ' 20 bold', command=self.reset)
        self.submit_button.grid(row=0, column=1, padx=5, pady=5)

        all_letters = 'abcdefghijklmnopqrstuvwxyz'

        # User choice radio buttons
        self.user_choice = StringVar()
        self.user_choice.set(None)
        for letter in all_letters:
            self.letter_radio_button = Radiobutton(self.middle_frame, text=letter.upper(), value=letter,
                                                   variable=self.user_choice, width=4, height=2, indicatoron=0,
                                                   font=game_font+' 12 bold')
            if all_letters.index(letter) > (len(all_letters) / 2)-1:
                self.letter_radio_button.grid(row=1, column=all_letters.index(letter)-(len(all_letters) / 2))
            else:
                self.letter_radio_button.grid(row=0, column=all_letters.index(letter))

        # Computer choice from random words
        self.word_list = self.rw.random_words(count=random.randrange(1, 4))
        self.all_words = ' '.join(self.word_list)

        self.reveal_text = StringVar()
        self.starting_text = []
        for letter in self.all_words:
            if letter <> ' ':
                self.starting_text.append('_')
            else:
                self.starting_text.append(' ')
        self.starting_text = ''.join(self.starting_text)
        self.reveal_text.set(self.starting_text)

        self.reveal = Label(self.top_frame, textvariable=self.reveal_text, fg='black', bg='lightblue', font=game_font+' 48 bold')
        self.reveal.grid(row=1, column=0, pady=10)

        self.s = ttk.Style()
        self.s.theme_use('classic')
        self.s.configure('green.Horizontal.TProgressbar', troughcolor='white', background='darkgreen', thickness=38)
        self.progress_bar = ttk.Progressbar(self.top_frame, style='green.Horizontal.TProgressbar', length=600)
        self.progress_bar.grid(row=0, column=0)
        self.progress_bar['value'] = self.mistake_max
        self.progress_bar['maximum'] = self.mistake_max

    def been_clicked(self):
        indexing = 0
        matches = 0
        all_words = []
        for x in self.all_words:
            all_words.append(x)
        for letter in all_words:
            if self.user_choice.get() == letter:
                letter_list = []
                for x in self.starting_text:
                    letter_list.append(x)
                letter_list[indexing] = letter.upper()
                self.starting_text = ''.join(letter_list)
                self.reveal_text.set(self.starting_text)
                matches += 1
            indexing += 1
        if matches == 0:
            self.mistake_count -= 1
            self.progress_bar['value'] = self.mistake_count
            if self.mistake_count <= self.mistake_max * 0.25:
                self.s.configure('green.Horizontal.TProgressbar', troughcolor='white', background='red', thickness=38)
            elif self.mistake_count <= self.mistake_max / 2:
                self.s.configure('green.Horizontal.TProgressbar', troughcolor='white', background='yellow', thickness=38)
        print self.mistake_count

        if self.mistake_count == 0:
            self.reveal_text.set('GAME OVER')
            self.progress_bar['value'] = self.mistake_max
            self.s.configure('green.Horizontal.TProgressbar', troughcolor='white', background='red', thickness=38)

    def reset(self):
        self.mistake_count = 8
        self.progress_bar['value'] = self.mistake_count
        self.s.configure('green.Horizontal.TProgressbar', troughcolor='white', background='darkgreen', thickness=38)

        self.word_list = self.rw.random_words(count=random.randrange(1, 4))
        self.all_words = ' '.join(self.word_list)
        self.starting_text = []
        for letter in self.all_words:
            if letter <> ' ':
                self.starting_text.append('_')
            else:
                self.starting_text.append(' ')
        self.starting_text = ''.join(self.starting_text)
        self.reveal_text.set(self.starting_text)


app = Hangman()
app.title('Hangman')
app.configure(bg='lightblue')
app.mainloop()
