from Tkinter import *
import os


class Window(Tk):

    def __init__(self):
        Tk.__init__(self)

        # self.new_file_path = 'C:\\Users\\Justango\\Documents\\' + 'testing_something.txt'
        self.new_file_path = os.path.join(os.environ.get('TMP').replace('AppData', 'Documents').split('Local')[0], 'testing_something.txt')
        self.score = 0

        self.save_button = Button(self, text='Save', command=self.save_file)
        self.save_button.pack()

    def save_file(self):
        self.score += 1
        print self.score
        self.new_file = open(self.new_file_path, 'w+')
        self.new_file.write(str(self.score))
        self.new_file.close()


app = Window()
app.mainloop()
