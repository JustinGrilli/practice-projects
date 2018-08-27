from Tkinter import *
import tkMessageBox
import random
import PIL
import ttk
import time


class Window(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title('Life Simulator')
        # self.geometry('800x600')
        self.iconbitmap('money.ico')
        self.configure(background='black')
        frame = Frame(self)
        frame.grid()
        frame.configure(background='black')
        menu_bar = Menu(self)
        self.config(menu=menu_bar)
        file_menu = Menu(menu_bar)
        menu_bar.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label='New', command=self.refresh)
        file_menu.add_separator()
        file_menu.add_command(label='Quit', command=quit)

        edit_menu = Menu(menu_bar)
        menu_bar.add_cascade(label='Edit', menu=edit_menu)
        edit_menu.add_command(label='Refresh', command=self.refresh)

        self.badButton = Button(frame, text='Spend', command=self.end_world, bg='darkred', fg='white', width=22)
        self.badButton.grid(row=0, column=0, sticky=W)

        self.goodButton = Button(frame, text='Save', command=self.save_world, bg='forest green', fg='white', width=22)
        self.goodButton.grid(row=0, column=1, sticky=W)

        # self.quitButton = Button(frame, text='Quit', command=frame.quit, bg='darkgrey', fg='white')
        # self.quitButton.grid(row=0, column=2)

        self.progress_bar_value = 100.0
        self.progress_bar_max = 100.0
        self.s = ttk.Style()
        self.s.theme_use('classic')
        self.s.configure('red.Horizontal.TProgressbar', troughcolor='black', background='green', thickness=45)
        self.progress_bar = ttk.Progressbar(frame, style='red.Horizontal.TProgressbar', orient='horizontal', length=330, mode='determinate')
        self.progress_bar['value'] = 100.0
        self.progress_bar['maximum'] = 100.0
        self.progress_bar.grid(row=1, columnspan=3)

        self.money_total = 10000
        self.money = 0
        self.label_text = StringVar()
        self.label_text.set('$' + str(self.money_total))
        self.label1 = Label(frame, textvariable=self.label_text, bg='black', fg='green', font='impact 20')
        self.label1.grid(row=1, columnspan=3)

    def end_world(self):
        self.progress_bar_value -= random.randrange(0, 6)
        self.progress_bar['value'] = self.progress_bar_value
        if self.progress_bar_value > 0:
            self.money = self.money_total * (self.progress_bar_value / self.progress_bar_max)
        else:
            self.money = 0
        self.label_text.set('$' + str(int(self.money)))
        self.s.configure('red.Horizontal.TProgressbar', troughcolor='black', background='green')
        if self.progress_bar_value < self.progress_bar_max / 2:
            self.s.configure('red.Horizontal.TProgressbar', troughcolor='black', background='red')
            self.label1.configure(fg='red')
        if self.progress_bar_value > 0:
            self.after(100, self.end_world)

    def save_world(self):
        self.progress_bar_value += random.randrange(0, 6)
        self.progress_bar['value'] = self.progress_bar_value
        if self.progress_bar_value < self.money_total:
            self.money = self.money_total * (self.progress_bar_value / self.progress_bar_max)
        else:
            self.money = self.money_total
        self.label_text.set('$' + str(int(self.money)))
        if self.progress_bar_value >= self.progress_bar_max / 2:
            self.s.configure('red.Horizontal.TProgressbar', troughcolor='black', background='green')
            self.label1.configure(fg='green')
        if self.progress_bar_value < 100:
            self.after(100, self.save_world)
        else:
            self.label_text.set('Money restored!')

    def refresh(self):
        self.progress_bar_value = self.progress_bar_max
        self.label_text.set('$'+str(self.money_total))
        self.label1.configure(fg='green')
        self.progress_bar['value'] = self.progress_bar_value
        self.s.configure('red.Horizontal.TProgressbar', troughcolor='black', background='green')


app = Window()
app.mainloop()
