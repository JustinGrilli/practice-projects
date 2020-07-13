from tkinter import *
from tkinter.ttk import Separator


class MenuButton:
    def __init__(self, widget, cascade_window, **kwargs):

        self.text = kwargs.pop('text', None)
        self.font = kwargs.pop('font', None)
        self.bg = kwargs.pop('bg', None)
        self.fg = kwargs.pop('fg', None)
        self.activebackground = kwargs.pop('activebackground', self.bg)
        self.activeforeground = kwargs.pop('activeforeground', self.fg)
        self.cursor = kwargs.pop('cursor', 'hand2')

        self.__cascade_window = cascade_window
        self.__cascade_frame = Frame(self.__cascade_window, bg=self.bg, bd=2, relief=SUNKEN)

        self.__button = Button(widget, text=self.text, command=self.__toggle_cascade_window, cursor=self.cursor,
                               font=self.font, relief=FLAT, bd=0, bg=self.bg, fg=self.fg,
                               activebackground=self.activebackground, activeforeground=self.activeforeground)
        self.__button.pack(side=LEFT, padx=(3, 0), pady=(3, 1))

        self.__button.bind('<Enter>', self.__on_enter_tab)
        self.__button.bind('<Leave>', self.__set_background_default)

    def add_menu_item(self, text=None, image=None, command=None):
        b = Button(self.__cascade_frame, text=text, image=image, compound=LEFT, command=command, cursor=self.cursor,
                   font=self.font, relief=FLAT, bd=0, bg=self.bg, fg=self.fg,
                   activebackground=self.activebackground, activeforeground=self.activeforeground)
        b.pack(side=TOP, fill=X, padx=2, pady=1)
        b.bind('<Leave>', self.__set_background_default)
        b.bind('<Enter>', self.__set_background_highlight)

    def add_separator(self):
        Separator(self.__cascade_frame).pack(fill=X, padx=2, pady=1)

    def __on_enter_tab(self, event):
        self.__set_background_highlight(event)
        # Hid all frames, show the cascade window, and then show the frame we want
        for f in self.__cascade_window.winfo_children():
            f.pack_forget()
        self.__cascade_window.update()
        x, y = self.__button.winfo_rootx(), self.__button.winfo_rooty() + self.__button.winfo_reqheight()
        self.__cascade_window.geometry(f'+{x}+{y}')
        self.__cascade_frame.pack()

    def __toggle_cascade_window(self):
        if self.__cascade_window.winfo_ismapped():
            self.__cascade_window.withdraw()
        else:
            self.__cascade_window.update()
            x, y = self.__button.winfo_rootx(), self.__button.winfo_rooty() + self.__button.winfo_reqheight()
            self.__cascade_window.geometry(f'+{x}+{y}')
            self.__cascade_window.deiconify()

    def __set_background_highlight(self, event):
        event.widget.config(bg=self.activebackground, fg=self.activeforeground)

    def __set_background_default(self, event):
        event.widget.config(bg=self.bg, fg=self.fg)


class MenuBar(Frame):
    def __init__(self, widget, **kwargs):
        Frame.__init__(self, widget)

        def on_click(event):
            """ toggle off the cascade window """
            if self.__cascade_window.winfo_ismapped():
                # Does not turn off right away to give time for selecting options
                self.after(300, self.__cascade_window.withdraw)

        def on_window_adjustment(event):
            """ toggle off the cascade window """
            self.__cascade_window.withdraw()

        self.font = kwargs.pop('font', None)
        self.bg = kwargs.pop('bg', None)
        self.fg = kwargs.pop('fg', None)
        self.activebackground = kwargs.pop('activebackground', self.bg)
        self.activeforeground = kwargs.pop('activeforeground', self.fg)
        self.cursor = kwargs.pop('cursor', 'hand2')

        self.__menu_bar = Frame(widget, bg=self.bg, bd=1, relief=RIDGE, name='menu_bar')
        self.__menu_bar.pack(side=TOP, fill=X)

        self.__cascade_window = Toplevel(widget)
        self.__cascade_window.overrideredirect(True)
        self.__cascade_window.withdraw()
        self.bind_all('<Button-1>', on_click)
        self.master.bind('<Configure>', on_window_adjustment)

    def add_menu_tab(self, text=None):
        b = MenuButton(self.__menu_bar, self.__cascade_window, text=text, cursor=self.cursor,
                       font=self.font, bd=0, bg=self.bg, fg=self.fg,
                       activebackground=self.activebackground, activeforeground=self.activeforeground)
        return b


if __name__ == '__main__':
    def on_save():
        print('Save...')

    def on_open():
        print('Open...')

    def on_copy():
        print('Copy...')

    def on_cut():
        print('Cut...')

    app = Tk()
    app.title('Menu Bar Example')
    app.geometry('300x200')
    app.config(bg='darkgrey')

    menu = MenuBar(app, font=('Helvetica', 12, 'bold'), bg='black', fg='white',
                   activebackground='#444444', activeforeground='white')
    tab1 = menu.add_menu_tab(text='File')
    tab2 = menu.add_menu_tab(text='Edit')
    tab1.add_menu_item(text='Save', command=on_save)
    tab1.add_separator()
    tab1.add_menu_item(text='Exit', command=app.destroy)
    tab2.add_menu_item(text='Copy', command=on_copy)
    tab2.add_menu_item(text='Cut', command=on_cut)

    app.mainloop()
