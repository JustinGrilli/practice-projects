from Tkinter import *
import tkFileDialog
import re


class Window(Tk):

    def __init__(self):
        Tk.__init__(self)

        self.the_file = None
        self.top_frame = Frame(self, width=680, bg='DarkGrey')
        self.top_frame.pack(side=TOP)

        self.upper_list = ['SELECT', 'FROM', 'ORDER', 'GROUP', 'BY', 'IS', 'NULL', 'ISNULL', 'NOTNULL', 'TRUE', 'FALSE',
                           'JOIN', 'LEFT', 'RIGHT', 'WHERE', 'HAVING', 'PARTITION', 'OVER', 'WITH', 'AS', 'NOT', 'AND',
                           'OR', 'ON', 'IN', 'BETWEEN', 'UNBOUNDED', 'PROCEEDING', 'FOLLOWING', 'UNION', 'ALL', 'WITHIN',
                           'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'COALESCE', 'NVL', 'AVG', 'MAX', 'SUM', 'COUNT']

        self.open_file_button = Button(self.top_frame, text='Open File', command=self.open_file, width=20, height=2, font='none 20 bold', relief=RAISED, bg='Orange')
        self.open_file_button.pack(side=TOP, padx=10, pady=10)

        self.cap_file_button = Button(self.top_frame, text='Upper Case', command=self.cap_file, width=20, height=2, font='none 20 bold', relief=RAISED)
        self.cap_file_button.pack(side=LEFT, padx=10, pady=10)

        self.cap_file_button = Button(self.top_frame, text='Lower Case', command=self.lower_file, width=20, height=2, font='none 20 bold', relief=RAISED)
        self.cap_file_button.pack(side=LEFT, padx=10, pady=10)

        self.cap_file_button = Button(self.top_frame, text='Semi Lower Case', command=self.semi_lower_file, width=20, height=2, font='none 20 bold', relief=RAISED)
        self.cap_file_button.pack(side=LEFT, padx=10, pady=10)

        self.label_text = StringVar()
        self.label_text.set(self.the_file)
        self.file_label = Label(self, textvariable=self.label_text, relief=SUNKEN)
        self.file_label.pack(side=BOTTOM, fill=X)

    def cap_file(self):
        if self.the_file != None:
            sql_file = self.the_file.read()

            new_sql_file = open('Re-Cased_File.sql', 'w')
            new_sql_file.write(sql_file.upper())
            new_sql_file.close()
            new_sql_file = open('Re-Cased_File.sql', 'r')

            fmt = '{:<8}{:<200}{}'
            print fmt.format('', 'Before', 'After')
            print fmt.format('', '', '')
            for i, (n, g) in enumerate(zip(sql_file.split('\n'), new_sql_file.read().split('\n'))):
                print fmt.format(i, n, g)

            new_sql_file.close()
            self.label_text.set(new_sql_file)

    def lower_file(self):
        if self.the_file != None:
            sql_file = self.the_file.read()

            new_sql_file = open('Re-Cased_File.sql', 'w')
            new_sql_file.write(sql_file.lower())
            new_sql_file.close()
            new_sql_file = open('Re-Cased_File.sql', 'r')

            fmt = '{:<8}{:<200}{}'
            print fmt.format('', 'Before', 'After')
            print fmt.format('', '', '')
            for i, (n, g) in enumerate(zip(sql_file.split('\n'), new_sql_file.read().split('\n'))):
                print fmt.format(i, n, g)

            new_sql_file.close()
            self.label_text.set(new_sql_file)

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

            new_sql_file = open('Re-Cased_File.sql', 'w')
            new_sql_file.write(sql_file_formatted)
            new_sql_file.close()
            new_sql_file = open('Re-Cased_File.sql', 'r')

            fmt = '{:<8}{:<200}{}'
            print fmt.format('', 'Before', 'After')
            print fmt.format('', '', '')
            for i, (n, g) in enumerate(zip(sql_file.split('\n'), new_sql_file.read().split('\n'))):
                print fmt.format(i, n, g)

            new_sql_file.close()
            self.label_text.set(new_sql_file)

    def open_file(self):
        self.the_file = tkFileDialog.askopenfile(parent=self, mode='r', title='Choose a file to CAP')
        self.label_text.set(self.the_file)
        return self.the_file


app = Window()
app.title('Casing formatter')
app.config(bg='DarkGrey')
app.mainloop()
