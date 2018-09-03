from Tkinter import *
import ttk
# import hang_man as hm

class Startscreen(Tk):

    def __init__(self, game_title):
        Tk.__init__(self)
        Tk.title(self, game_title)

        self.user_name_submit = ''

        self.windowFrame = Frame(self, width=640, height=480, bg='#222222')
        self.windowFrame.grid(row=0, columnspan=3)

        self.welcomeLabel = Label(self.windowFrame, bg='#222222', fg='white', text='\nWelcome to ' + game_title + '\n',
                                  font='none 35 bold')
        self.welcomeLabel.grid(row=0, columnspan=3)

        self.welcomeLabel = Label(self.windowFrame, bg='#222222', fg='white', text='Please enter your user name below',
                                  font='none 20 bold')
        self.welcomeLabel.grid(row=1, columnspan=3)

        self.snLabel = Label(self.windowFrame, text='S/N:', font='none 25 bold', fg='white', bg='#222222')
        self.snLabel.grid(row=2, column=0, sticky=E)

        self.user_name = Entry(self.windowFrame, font='none 25 bold', width=30)
        self.user_name.configure(justify='center')
        self.user_name.grid(row=2, column=1, pady=10, padx=2, sticky=W)

        self.submitButton = Button(self.windowFrame, bg='#333333', fg='white', text='Play', font='none 18 bold',
                                   command=self.kill_welcome)
        self.submitButton.grid(row=2, column=2, pady=10, padx=2, sticky=E)

    def kill_welcome(self):
        self.user_name_submit = self.user_name.get()
        print self.user_name_submit
        self.destroy()



welcome = Startscreen('Your Game')
welcome.mainloop()
