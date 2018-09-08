from Tkinter import *
from random_words import RandomWords
import random


def run():
    app.random_word_list = rw.random_words(count=random.randrange(99, 1000))
    app.random_word_list = " ".join(app.random_word_list)
    app.wordlist_len = len(app.random_word_list)
    start()


def start():
    if app.counter < app.wordlist_len:
        listbox.insert(END, app.random_word_list[app.counter])
        app.counter += 1
        listbox.yview_pickplace("end")
        listbox.config(
            fg='#'
               + str(random.randrange(0, 10))
               + str(random.randrange(0, 10))
               + str(random.randrange(0, 10))
               + str(random.randrange(0, 10))
               + str(random.randrange(0, 10))
               + str(random.randrange(0, 10))
        )
        app.after(100, start)
    else:
        app.counter = 0


app = Tk()
app.geometry('800x640')
app.resizable(0, 0)
app.configure(bg='black')
app.title('Party Text')

rw = RandomWords()
app.letter_list = []
app.counter = 0

scroll_bar = Scrollbar(app, orient='vertical')
scroll_bar.pack(side=RIGHT, fill=Y)

listbox = Text(app, yscrollcommand=scroll_bar.set, bg='black', fg='red', font='system 20')
listbox.pack(side=LEFT, fill=BOTH, expand=True)
scroll_bar.config(command=listbox.yview)

menu = Menu(app)
app.config(menu=menu)

sub_menu = Menu(menu)
menu.add_cascade(menu=sub_menu, label='File')
sub_menu.add_cascade(label='Run', command=run)

app.mainloop()