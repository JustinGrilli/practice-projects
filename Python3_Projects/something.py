from tkinter import *


class Window(Tk):

    def __init__(self):
        Tk.__init__(self)

        self.this_button = Button(self, text='Click This', command=quit, height=2, font='none 20 bold')
        self.this_button.grid(row=0, column=0, padx=4, pady=4)


app = Window()
app.geometry('640x480')
app.config(bg='DarkGrey')
app.mainloop()
