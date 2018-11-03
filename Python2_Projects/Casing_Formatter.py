from Tkinter import *
from ttk import Combobox, Style
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
                           'OR', 'ON', 'IN', 'BETWEEN', 'UNBOUNDED', 'PROCEEDING', 'FOLLOWING', 'UNION', 'ALL', 'CASE',
                           'WHEN', 'THEN', 'ELSE', 'END', 'COALESCE', 'NVL', 'AVG', 'MAX', 'SUM', 'COUNT', 'WITHIN',
                           'LISTAGG']
        text_box_font_options = {'name': ['none', 'Courier', 'Georgia', 'Gothic',
                                          'Impact', 'System', 'Tahoma', 'Times', 'Verdana'],
                                 'size': []}
        for num in range(6, 101):
            text_box_font_options['size'].append(num)

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

        # Scrollbar
        self.text_scrollbar = Scrollbar(self.main_frame)
        self.text_scrollbar.pack(side=RIGHT, fill=BOTH)

        # Buttons
        button_font = 'helvetica 18 bold'
        self.open_file_button = Button(self.button_frame, text='Open File', command=self.open_file, font='helvetica 14', relief=RAISED, bg='deepskyblue4', fg='white')
        self.open_file_button.pack(side=TOP, padx=5, pady=4)
        self.upper_button = Button(self.button_frame, text='A', width=3, command=self.cap_file, font=button_font, relief=RAISED, bg=self.sub_color, fg='white')
        self.upper_button.pack(side=TOP, padx=5, pady=4)
        self.lower_button = Button(self.button_frame, text='a', width=3, command=self.lower_file, font=button_font, relief=RAISED, bg=self.sub_color, fg='white')
        self.lower_button.pack(side=TOP, padx=5, pady=4)
        self.semi_lower_button = Button(self.button_frame, text='Ab', width=3, command=self.semi_lower_file, font=button_font, relief=RAISED, bg=self.sub_color, fg='white')
        self.semi_lower_button.pack(side=TOP, padx=5, pady=4)
        self.semi_lower_button = Button(self.button_frame, text='Apply Font', command=self.text_box_font, font='helvetica 14', relief=RAISED, bg=self.sub_color, fg='white')
        self.semi_lower_button.pack(side=BOTTOM, padx=5, pady=4)

        # Font drop-down menus
        self.font_name_dropdown = Combobox(self.button_frame, values=text_box_font_options['name'], justify='center')
        self.font_name_dropdown.set(text_box_font_options['name'][0])
        self.font_name_dropdown.pack(side=BOTTOM, padx=5, pady=4)
        self.font_style = self.font_name_dropdown.get()

        self.font_size_dropdown = Combobox(self.button_frame, values=text_box_font_options['size'], justify='center')
        self.font_size_dropdown.set(12)
        self.font_size_dropdown.pack(side=BOTTOM, padx=5, pady=4)
        self.text_font_size = self.font_size_dropdown.get()

        # Text boxes
        self.text_box_before = Text(self.text_frame, relief=SUNKEN, bg=self.sub_color, fg='grey', font=(self.font_style, self.text_font_size), wrap=WORD, yscrollcommand=self.text_scrollbar.set)
        self.text_box_before.pack(side=LEFT, fill=BOTH, expand=TRUE, padx=2)
        self.text_box_after = Text(self.text_frame, relief=SUNKEN, bg=self.sub_color, fg='grey', font=(self.font_style, self.text_font_size), wrap=WORD, yscrollcommand=self.text_scrollbar.set)
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

            self.text_color()

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

            self.text_color()

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

            self.text_color()

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

    def text_color(self):
        # Colors the words in the before and after text boxes, for the words that are in the upper list
        temp_split = self.text_box_after.get(1.0, END)
        temp_split = temp_split.split('\n')
        line_count = 0
        for line in temp_split:
            line_count += 1
            temp_list = re.sub(r'[^A-Za-z0-9._]', ' ', line).split(' ')
            recon = []
            for item in temp_list:
                recon.append(item)
                letter = len(' '.join(recon))
                if item.upper() in self.upper_list:
                    self.text_box_after.tag_add("start", str(line_count) + "." + str(letter - len(item)), str(line_count) + "." + str(letter))
                    self.text_box_after.tag_config("start", foreground='orange', font=(self.font_style, self.text_font_size, ' bold'))
                    self.text_box_before.tag_add("start", str(line_count) + "." + str(letter - len(item)), str(line_count) + "." + str(letter))
                    self.text_box_before.tag_config("start", foreground='orange', font=(self.font_style, self.text_font_size, ' bold'))

    def text_box_font(self):
        self.text_box_after.tag_add("font", 1.0, END)
        self.text_box_after.tag_config("font", font=(self.font_name_dropdown.get(), self.font_size_dropdown.get()))
        self.text_box_before.tag_add("font", 1.0, END)
        self.text_box_before.tag_config("font", font=(self.font_name_dropdown.get(), self.font_size_dropdown.get()))


app = Window()
app.mainloop()
