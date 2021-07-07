from tkinter import *


class CollapsibleFrame(Frame):
    """ Creates a collapsible frame, with a button to expand and collapse the frame.
        Frame starts collapsed by default. """
    def __init__(self, top, **kwargs):
        Frame.__init__(self)
        self.bg = kwargs.pop('bg', None)
        self.fg = kwargs.pop('fg', None)
        self.title_color = kwargs.pop('title_color', None)
        self.highlight_color = kwargs.pop('highlight_color', None)
        self.font = kwargs.pop('font', None)
        self.title = kwargs.pop('title', None)
        self.alignment = kwargs.pop('alignment', W)
        self.start_collapsed = kwargs.pop('start_collapsed', True)

        main_frame = Frame(top, bg=self.bg, bd=0, relief=RIDGE)
        main_frame.pack(fill=BOTH, expand=True)
        self.top_frame = Frame(main_frame, bg=self.bg)
        self.top_frame.pack(fill=X)
        title_frame = Frame(self.top_frame, bg=self.title_color)
        title_frame.pack(side=RIGHT, fill=X, expand=True)

        title = Button(title_frame, text=self.title, bg=self.bg, fg=self.fg, cursor='hand2', relief=RIDGE, bd=0,
                       font=self.font, anchor=self.alignment, command=self.collapse, highlightthickness=0,
                       activebackground=self.highlight_color, activeforeground=self.fg)
        self.collapse_frame = Frame(main_frame, bg=self.bg)
        title.pack(side=TOP, fill=X, padx=1, pady=1, ipadx=4, anchor=self.alignment)
        if not self.start_collapsed:
            self.collapse_frame.pack(fill=X)

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
