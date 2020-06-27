from tkinter import *


class CollapsibleFrame(Frame):
    def __init__(self, top, **kwargs):
        Frame.__init__(self)
        self.bg = kwargs.pop('bg', None)
        self.fg = kwargs.pop('fg', None)
        self.title_color = kwargs.pop('title_color', None)
        self.font = kwargs.pop('font', None)
        self.title = kwargs.pop('title', None)
        self.alignment = kwargs.pop('alignment', W)

        main_frame = Frame(top, bg=self.bg)
        main_frame.pack(fill=BOTH, expand=True)
        self.top_frame = Frame(main_frame, bg=self.bg)
        self.top_frame.pack(fill=X)
        title_frame = Frame(self.top_frame, bg=self.title_color)
        title_frame.pack(side=RIGHT, fill=X, expand=True)

        title = Button(title_frame, text=self.title, bg=self.bg, fg=self.fg, cursor='hand2', relief=RIDGE,
                       font=self.font, anchor=self.alignment, command=self.collapse)
        self.collapse_frame = Frame(main_frame, bg=self.bg, bd=2, relief=SUNKEN)
        title.pack(side=TOP, fill=X, padx=1, pady=1, ipadx=4, anchor=self.alignment)
        self.collapse_frame.pack(side=TOP, fill=X)

    def collapse(self):
        if self.collapse_frame.winfo_viewable():
            self.collapse_frame.pack_forget()
        else:
            self.collapse_frame.pack(fill=X)


if __name__ == '__main__':
    """ Example """

    app = Tk()
    app.title('Test')
    app.geometry('300x300')

    f = CollapsibleFrame(app, title='Title', bg='black', fg='white', title_color='yellow')
    label = Label(f.collapse_frame, text=' - Test')
    label.pack(side=LEFT)
    button = Button(f.top_frame, text='Add Button')
    button.pack(side=LEFT)

    app.mainloop()
