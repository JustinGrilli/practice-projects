from Tkinter import *
import tkFileDialog
import re


class Window(Tk):

    def __init__(self):
        Tk.__init__(self)

        self.geometry(str(int(self.winfo_screenwidth()/1.5))+'x'+str(int(self.winfo_screenheight()/1.5)))

        self.the_file = None
        self.main_frame = Frame(self, bg='#333333', width=600, height=400)
        self.main_frame.pack(side=TOP, fill=BOTH, expand=TRUE)
        self.button_frame = Frame(self.main_frame, bg='#333333')
        self.button_frame.pack(side=LEFT, fill=BOTH)

        self.text_scrollbar = Scrollbar(self.main_frame)
        self.text_scrollbar.pack(side=RIGHT, fill=BOTH)

        self.text_frame = Frame(self.main_frame, bg='#333333')
        self.text_frame.pack(side=LEFT, fill=BOTH, expand=TRUE,)

        self.upper_list = ['SELECT', 'FROM', 'ORDER', 'GROUP', 'BY', 'IS', 'NULL', 'ISNULL', 'NOTNULL', 'TRUE', 'FALSE',
                           'JOIN', 'LEFT', 'RIGHT', 'WHERE', 'HAVING', 'PARTITION', 'OVER', 'WITH', 'AS', 'NOT', 'AND',
                           'OR', 'ON', 'IN', 'BETWEEN', 'UNBOUNDED', 'PROCEEDING', 'FOLLOWING', 'UNION', 'ALL', 'WITHIN',
                           'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'COALESCE', 'NVL', 'AVG', 'MAX', 'SUM', 'COUNT']

        button_font = 'system 14 bold'
        self.open_file_button = Button(self.button_frame, text='Open File', command=self.open_file, width=16, font=button_font, relief=RAISED, bg='lightblue')
        self.open_file_button.pack(side=TOP, padx=5, pady=4)

        self.cap_file_button = Button(self.button_frame, text='Upper Case', command=self.cap_file, width=16, font=button_font, relief=RAISED, bg='white')
        self.cap_file_button.pack(side=TOP, padx=5, pady=4)

        self.cap_file_button = Button(self.button_frame, text='Lower Case', command=self.lower_file, width=16, font=button_font, relief=RAISED, bg='white')
        self.cap_file_button.pack(side=TOP, padx=5, pady=4)

        self.cap_file_button = Button(self.button_frame, text='Semi Lower Case', command=self.semi_lower_file, width=16, font=button_font, relief=RAISED, bg='white')
        self.cap_file_button.pack(side=TOP, padx=5, pady=4)

        self.status_text = StringVar()
        self.status_text.set('')
        self.status_label = Label(self, textvariable=self.status_text, relief=SUNKEN, font='system 8', fg='#333333')
        self.status_label.pack(side=BOTTOM, fill=X)

        self.text_before = StringVar()
        self.text_after = StringVar()

        self.text_box_before = Text(self.text_frame, relief=SUNKEN, bg='#444444', fg='grey', font='none 10 bold', wrap=WORD, yscrollcommand=self.text_scrollbar.set)
        self.text_box_before.pack(side=LEFT, fill=BOTH, expand=TRUE, padx=2)
        self.text_box_after = Text(self.text_frame, relief=SUNKEN, bg='#444444', fg='grey', font='none 10 bold', wrap=WORD, yscrollcommand=self.text_scrollbar.set)
        self.text_box_after.pack(side=LEFT, fill=BOTH, expand=TRUE, padx=2)
        self.text_scrollbar.config(command=self.yview)

    def yview(self, *args):
        self.text_box_before.yview(*args)
        self.text_box_after.yview(*args)

    def cap_file(self):
        if self.the_file != None:
            sql_file = self.the_file.read()

            savedir = tkFileDialog.askdirectory(title='Select folder to save results')
            if savedir != '':
                new_sql_file = open(savedir+'/'+self.open_file, 'w')
                new_sql_file.write(sql_file.upper())
                new_sql_file.close()
                new_sql_file = open(savedir+'/'+self.open_file, 'r')

                self.text_before.set(sql_file)
                self.text_box_before.insert(END, self.text_before.get())
                self.text_after.set(new_sql_file.read())
                self.text_box_after.insert(END, self.text_after.get())

                new_sql_file.close()
                self.status_text.set('Saved as: '+self.open_file)
                self.status_label.config(bg='#777777')
            else:
                self.status_text.set('')
                self.status_label.config(bg='white')

    def lower_file(self):
        if self.the_file != None:
            sql_file = self.the_file.read()

            savedir = tkFileDialog.askdirectory(title='Select folder to save results')
            if savedir != '':
                new_sql_file = open(savedir+'/'+self.open_file, 'w')
                new_sql_file.write(sql_file.lower())
                new_sql_file.close()
                new_sql_file = open(savedir+'/'+self.open_file, 'r')

                self.text_before.set(sql_file)
                self.text_box_before.insert(END, self.text_before.get())
                self.text_after.set(new_sql_file.read())
                self.text_box_after.insert(END, self.text_after.get())

                new_sql_file.close()
                self.status_text.set('Saved as: '+self.open_file)
                self.status_label.config(bg='#777777')
            else:
                self.status_text.set('')
                self.status_label.config(bg='white')

    def semi_lower_file(self):
        if self.the_file != None:
            sql_file = self.the_file.read()
            temp_split = sql_file.split(' ')
            sql_file_formatted = []
            for item in temp_split:
                for word in re.sub(r'[^A-Za-z0-9._]', '\n', item).split('\n'):
                    if word.upper() in self.upper_list:
                        item = item.replace(word, word.upper())
                    else:
                        item = item.replace(word, word.lower())
                sql_file_formatted.append(item)

            sql_file_formatted = ' '.join(sql_file_formatted)

            savedir = tkFileDialog.askdirectory(title='Select folder to save results')


            if savedir != '':
                new_sql_file = open(savedir+'/'+self.open_file, 'w')
                new_sql_file.write(sql_file_formatted)
                new_sql_file.close()
                new_sql_file = open(savedir+'/'+self.open_file, 'r')

                self.text_before.set(sql_file)
                self.text_box_before.insert(END, self.text_before.get())
                self.text_after.set(new_sql_file.read())
                self.text_box_after.insert(END, self.text_after.get())

                new_sql_file.close()
                self.status_text.set('Saved as: '+self.open_file)
                self.status_label.config(bg='#777777')
            else:
                self.status_text.set('')
                self.status_label.config(bg='white')

    def open_file(self):
        self.text_box_before.delete(1.0, END)
        self.text_box_after.delete(1.0, END)
        self.the_file = tkFileDialog.askopenfile(parent=self, mode='r', title='Choose a file to format...')
        if self.the_file != None:
            self.open_file = re.sub(r'[^A-Za-z0-9._]', '', str(self.the_file).split(' ')[2].split('/')[-1])
            self.status_text.set('Selected: '+self.open_file)
            self.status_label.config(bg='lightblue')
        else:
            self.status_text.set('')
            self.status_label.config(bg='white')
        return self.the_file


app = Window()
app.title('Casing Formatter')
app.config(bg='#333333')
app.mainloop()
