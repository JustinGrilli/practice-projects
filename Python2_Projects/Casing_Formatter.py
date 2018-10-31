from Tkinter import *
import tkFileDialog
import re


class Window(Tk):

    def __init__(self):
        Tk.__init__(self)

        self.the_file = None
        self.top_frame = Frame(self, bg='#333333')
        self.top_frame.pack(side=TOP, fill=BOTH)

        self.upper_list = ['SELECT', 'FROM', 'ORDER', 'GROUP', 'BY', 'IS', 'NULL', 'ISNULL', 'NOTNULL', 'TRUE', 'FALSE',
                           'JOIN', 'LEFT', 'RIGHT', 'WHERE', 'HAVING', 'PARTITION', 'OVER', 'WITH', 'AS', 'NOT', 'AND',
                           'OR', 'ON', 'IN', 'BETWEEN', 'UNBOUNDED', 'PROCEEDING', 'FOLLOWING', 'UNION', 'ALL', 'WITHIN',
                           'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'COALESCE', 'NVL', 'AVG', 'MAX', 'SUM', 'COUNT']

        button_font = 'system 14 bold'
        self.open_file_button = Button(self.top_frame, text='Open File', command=self.open_file, width=16, font=button_font, relief=RAISED, bg='lightblue')
        self.open_file_button.pack(side=TOP, padx=10, pady=5)

        self.cap_file_button = Button(self.top_frame, text='Upper Case', command=self.cap_file, width=16, font=button_font, relief=RAISED, bg='white')
        self.cap_file_button.pack(side=TOP, padx=10, pady=5)

        self.cap_file_button = Button(self.top_frame, text='Lower Case', command=self.lower_file, width=16, font=button_font, relief=RAISED, bg='white')
        self.cap_file_button.pack(side=TOP, padx=10, pady=5)

        self.cap_file_button = Button(self.top_frame, text='Semi Lower Case', command=self.semi_lower_file, width=16, font=button_font, relief=RAISED, bg='white')
        self.cap_file_button.pack(side=TOP, padx=10, pady=5)

        self.label_text = StringVar()
        self.label_text.set('')
        self.file_label = Label(self, textvariable=self.label_text, relief=SUNKEN, font='system 8', fg='#333333')
        self.file_label.pack(side=BOTTOM, fill=X)

    def cap_file(self):
        if self.the_file != None:
            sql_file = self.the_file.read()

            savedir = tkFileDialog.askdirectory(title='Select folder to save results')
            new_sql_file = open(savedir+'/'+self.open_file, 'w')
            new_sql_file.write(sql_file.upper())
            new_sql_file.close()
            new_sql_file = open(savedir+'/'+self.open_file, 'r')

            fmt = '{:<8}{:<200}{}'
            print fmt.format('', 'Before', 'After')
            print fmt.format('', '', '')
            for i, (n, g) in enumerate(zip(sql_file.split('\n'), new_sql_file.read().split('\n'))):
                print fmt.format(i, n, g)

            new_sql_file.close()
            self.label_text.set('Saved as: '+self.open_file)
            self.file_label.config(bg='#777777')

    def lower_file(self):
        if self.the_file != None:
            sql_file = self.the_file.read()

            savedir = tkFileDialog.askdirectory(title='Select folder to save results')
            new_sql_file = open(savedir+'/'+self.open_file, 'w')
            new_sql_file.write(sql_file.lower())
            new_sql_file.close()
            new_sql_file = open(savedir+'/'+self.open_file, 'r')

            fmt = '{:<8}{:<200}{}'
            print fmt.format('', 'Before', 'After')
            print fmt.format('', '', '')
            for i, (n, g) in enumerate(zip(sql_file.split('\n'), new_sql_file.read().split('\n'))):
                print fmt.format(i, n, g)

            new_sql_file.close()
            self.label_text.set('Saved as: '+self.open_file)
            self.file_label.config(bg='#777777')

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
            new_sql_file = open(savedir+'/'+self.open_file, 'w')
            new_sql_file.write(sql_file_formatted)
            new_sql_file.close()
            new_sql_file = open(savedir+'/'+self.open_file, 'r')

            fmt = '{:<8}{:<200}{}'
            print fmt.format('', 'Before', 'After')
            print fmt.format('', '', '')
            for i, (n, g) in enumerate(zip(sql_file.split('\n'), new_sql_file.read().split('\n'))):
                print fmt.format(i, n, g)

            new_sql_file.close()
            self.label_text.set('Saved as: '+self.open_file)
            self.file_label.config(bg='#777777')
            print self.open_file

    def open_file(self):
        self.the_file = tkFileDialog.askopenfile(parent=self, mode='r', title='Choose a file to format...')
        if self.the_file != None:
            self.open_file = re.sub(r'[^A-Za-z0-9._]', '', str(self.the_file).split(' ')[2].split('/')[-1])
            self.label_text.set('Selected: '+self.open_file)
            self.file_label.config(bg='lightblue')
        else:
            self.label_text.set('')
            self.file_label.config(bg='white')
        return self.the_file


app = Window()
app.title('Casing Formatter')
app.config(bg='#333333')
app.mainloop()
