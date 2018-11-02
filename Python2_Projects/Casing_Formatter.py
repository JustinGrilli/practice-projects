from Tkinter import *
import tkFileDialog
import re


class Window(Tk):

    def __init__(self):
        Tk.__init__(self)

        # Global Elements
        self.main_color = '#333333'
        self.sub_color = '#444444'
        self.the_file = None
        self.upper_list = ['SELECT', 'FROM', 'ORDER', 'GROUP', 'BY', 'IS', 'NULL', 'ISNULL', 'NOTNULL', 'TRUE', 'FALSE',
                           'JOIN', 'LEFT', 'RIGHT', 'WHERE', 'HAVING', 'PARTITION', 'OVER', 'WITH', 'AS', 'NOT', 'AND',
                           'OR', 'ON', 'IN', 'BETWEEN', 'UNBOUNDED', 'PROCEEDING', 'FOLLOWING', 'UNION', 'ALL', 'WITHIN',
                           'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'COALESCE', 'NVL', 'AVG', 'MAX', 'SUM', 'COUNT']

        # Program attributes
        self.state('zoomed')  # starts maximized
        self.title('Casing Formatter')
        self.config(bg=self.main_color)

        # Frames
        self.main_frame = Frame(self, bg=self.main_color, width=600, height=400)
        self.main_frame.pack(side=TOP, fill=BOTH, expand=TRUE)
        self.button_frame = Frame(self.main_frame, bg=self.main_color)
        self.button_frame.pack(side=LEFT, fill=BOTH)
        self.text_frame = Frame(self.main_frame, bg=self.main_color)
        self.text_frame.pack(side=LEFT, fill=BOTH, expand=TRUE,)

        self.text_scrollbar = Scrollbar(self.main_frame)
        self.text_scrollbar.pack(side=RIGHT, fill=BOTH)

        # Buttons
        button_font = 'system 14 bold'
        self.open_file_button = Button(self.button_frame, text='Open File', command=self.open_file, width=16, font=button_font, relief=RAISED, bg='lightblue')
        self.open_file_button.pack(side=TOP, padx=5, pady=4)
        self.upper_button = Button(self.button_frame, text='Upper Case', command=self.cap_file, width=16, font=button_font, relief=RAISED, bg='white')
        self.upper_button.pack(side=TOP, padx=5, pady=4)
        self.lower_button = Button(self.button_frame, text='Lower Case', command=self.lower_file, width=16, font=button_font, relief=RAISED, bg='white')
        self.lower_button.pack(side=TOP, padx=5, pady=4)
        self.semi_lower_button = Button(self.button_frame, text='Semi Lower Case', command=self.semi_lower_file, width=16, font=button_font, relief=RAISED, bg='white')
        self.semi_lower_button.pack(side=TOP, padx=5, pady=4)

        # Text boxes
        self.text_box_before = Text(self.text_frame, relief=SUNKEN, bg=self.sub_color, fg='grey', font='none 10 bold', wrap=WORD, yscrollcommand=self.text_scrollbar.set)
        self.text_box_before.pack(side=LEFT, fill=BOTH, expand=TRUE, padx=2)
        self.text_box_after = Text(self.text_frame, relief=SUNKEN, bg=self.sub_color, fg='grey', font='none 10 bold', wrap=WORD, yscrollcommand=self.text_scrollbar.set)
        self.text_box_after.pack(side=LEFT, fill=BOTH, expand=TRUE, padx=2)
        self.text_scrollbar.config(command=self.yview)

        # Bottom Status bar
        self.status_text = StringVar()
        self.status_text.set('')
        self.status_label = Label(self, textvariable=self.status_text, relief=SUNKEN, font='system 8', fg='#333333')
        self.status_label.pack(side=BOTTOM, fill=X)

    def yview(self, *args):
        # Used to make both text boxes scroll at the same time
        self.text_box_before.yview(*args)
        self.text_box_after.yview(*args)

    def create_output_file(self):
        # This allows you to choose a directory for the output file
        self.savedir = tkFileDialog.askdirectory(title='Select folder to save results')
        if self.savedir != '':
            self.output_file = open(self.savedir + '/' + self.open_file, 'w')
        else:
            self.status_text.set('')
            self.status_label.config(bg='white')

    def cap_file(self):
        if self.the_file != None:
            sql_file = self.the_file.read()
            self.create_output_file()
            self.output_file.write(sql_file.upper())
            self.output_file.close()
            new_sql_file = open(self.savedir+'/'+self.open_file, 'r')

            self.text_box_before.insert(END, sql_file)
            self.text_box_after.insert(END, new_sql_file.read())

            new_sql_file.close()
            self.status_text.set('Saved as: '+self.open_file)
            self.status_label.config(bg='#777777')

    def lower_file(self):
        if self.the_file != None:
            sql_file = self.the_file.read()
            self.create_output_file()
            self.output_file.write(sql_file.lower())
            self.output_file.close()
            new_sql_file = open(self.savedir+'/'+self.open_file, 'r')

            self.text_box_before.insert(END, sql_file)
            self.text_box_after.insert(END, new_sql_file.read())

            new_sql_file.close()
            self.status_text.set('Saved as: '+self.open_file)
            self.status_label.config(bg='#777777')

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

            self.create_output_file()
            self.output_file.write(sql_file_formatted)
            self.output_file.close()
            new_sql_file = open(self.savedir+'/'+self.open_file, 'r')

            self.text_box_before.insert(END, sql_file)
            self.text_box_after.insert(END, new_sql_file.read())

            new_sql_file.close()
            self.status_text.set('Saved as: '+self.open_file)
            self.status_label.config(bg='#777777')

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
app.mainloop()
