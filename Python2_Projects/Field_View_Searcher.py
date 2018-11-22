from Tkinter import *
from ttk import Progressbar, Style
from PIL import Image, ImageTk
from pprint import pprint
import xml.etree.cElementTree as ET, os, re, operator, tkFileDialog


class Program(Tk):

    def __init__(self):
        Tk.__init__(self)

        self.default_colors = {
            # The common colors used throughout the application
            'main_bg': '#%02x%02x%02x' % (23, 46, 71),
            'sub_bg': '#%02x%02x%02x' % (39, 78, 119),
            'sub_sub_bg': '#%02x%02x%02x' % (62, 123, 188),
            'fg': '#%02x%02x%02x' % (255, 255, 255)
        }
        self.fs = False
        self.title('Field View Searcher')
        self.geometry(str(int(self.winfo_screenwidth()*0.8)) + 'x' + str(int(self.winfo_screenheight()*0.8)))
        self.attributes('-fullscreen', self.fs)  # Fullscreen the program
        # self.state('zoomed')  # Maximize the program
        self.config(bg=self.default_colors['sub_bg'])

        self.directory_location = None
        self.tree = None
        self.root = None
        self.total_wb_count = 0
        self.wb_count = 0
        self.total_wb_start = 0
        self.wb_start = 0
        self.total_view_count = 0
        self.total_view_start = 0
        self.view_count = 0
        self.view_start = 0

        # Frames
        self.left_frame = Frame(self, bg=self.default_colors['main_bg'])
        self.left_frame.pack(side=LEFT, fill=Y)
        self.left_top_frame = Frame(self.left_frame, bg=self.default_colors['main_bg'])
        self.left_top_frame.pack(side=TOP, fill=BOTH)
        self.left_top_frame1 = Frame(self.left_frame, bg=self.default_colors['main_bg'])
        self.left_top_frame1.pack(side=TOP, fill=BOTH)
        self.left_bottom_frame = Frame(self.left_frame, bg=self.default_colors['main_bg'])
        self.left_bottom_frame.pack(side=BOTTOM, fill=BOTH)

        self.right_frame = Frame(self, bg=self.default_colors['sub_bg'], relief=SUNKEN)
        self.right_frame.pack(side=LEFT, fill=BOTH, expand=True)
        self.right_top_frame = Frame(self.right_frame, bg=self.default_colors['sub_bg'], relief=SUNKEN)
        self.right_bottom_frame = Frame(self.right_frame, bg=self.default_colors['sub_bg'], relief=SUNKEN)

        # Scrollbar / Canvas
        self.right_top_canvas = Canvas(self.right_bottom_frame, bg=self.default_colors['sub_bg'], bd=0, highlightthickness=0, relief=RIDGE, scrollregion=(0, 0, 500, 500))
        self.scrollbar = Scrollbar(self.right_bottom_frame, orient=VERTICAL)

        ba = {
            # Button Attributes
            'padx': 2,
            'pady': 4,
            'font': 'none 12 bold',
            'bg_color': 'white'
        }
        ta = {
            # Text Attributes
            'padx': 2,
            'pady': 4,
            'font': 'none 12',
            'bg_color': 'white',
            'fg_color': 'black'
        }
        la = {
            # Label Attributes
            'padx': 2,
            'pady': 4,
            'font': 'none 12 bold',
            'fg_color': 'white'
        }
        # Images
        image_width, image_height = 35, 35
        dir_image = Image.open('Images/blue_folder.png')
        dir_image = dir_image.resize((image_width, image_height), Image.ANTIALIAS)
        self.directory_image = ImageTk.PhotoImage(dir_image)
        s_folder_image = Image.open('Images/search_folder.png')
        s_folder_image = s_folder_image.resize((image_width, image_height), Image.ANTIALIAS)
        self.search_folder_image = ImageTk.PhotoImage(s_folder_image)
        s_image = Image.open('Images/search.png')
        s_image = s_image.resize((image_width, image_height), Image.ANTIALIAS)
        self.search_image = ImageTk.PhotoImage(s_image)
        fs_image = Image.open('Images/fullscreen.png')
        fs_image = fs_image.resize((image_width, image_height), Image.ANTIALIAS)
        self.fullscreen_image = ImageTk.PhotoImage(fs_image)
        q_image = Image.open('Images/quit.png')
        q_image = q_image.resize((image_width, image_height), Image.ANTIALIAS)
        self.quit_image = ImageTk.PhotoImage(q_image)

        # Buttons
        self.locate_directory_button = Button(self.left_top_frame, image=self.directory_image, command=self.view_directory_locator, bg=ba['bg_color'], font=ba['font'])
        self.locate_directory_button.pack(side=LEFT, padx=ba['padx'], pady=ba['pady'])
        self.toggle_fs_button = Button(self.left_bottom_frame, image=self.fullscreen_image, command=self.toggle_fullscreen, bg=ba['bg_color'], font=ba['font'])
        self.toggle_fs_button.pack(side=LEFT, padx=ba['padx'], pady=ba['pady'])
        self.exit_button = Button(self.left_bottom_frame, image=self.quit_image, command=quit, bg=ba['bg_color'], font=ba['font'])
        self.exit_button.pack(side=LEFT, padx=ba['padx'], pady=ba['pady'])
        self.search_directory_button = Button(self.left_top_frame1, image=self.search_folder_image, command=self.general_search, bg=ba['bg_color'], font=ba['font'])
        self.search_directory_button.pack(side=LEFT, padx=ba['padx'], pady=ba['pady'])
        self.var = BooleanVar()
        self.var.set(True)
        self.sort_toggle_button = Checkbutton(self.left_top_frame1, text='Descending', variable=self.var, bg=self.default_colors['sub_sub_bg'], fg=self.default_colors['main_bg'], font=la['font'])
        self.sort_toggle_button.pack(side=LEFT, padx=ba['padx'], pady=ba['pady'])
        # Search bar & button
        self.search_bar = Entry(self.left_top_frame, fg=ta['fg_color'], bg=ta['bg_color'], font=ta['font'], relief=SUNKEN)
        self.search_bar.pack(side=LEFT, fill=BOTH, expand=True, padx=ta['padx'], pady=ta['pady'])
        self.search_button = Button(self.left_top_frame, image=self.search_image, command=self.search_views, bg=ba['bg_color'], font=ba['font'])
        self.search_button.pack(side=RIGHT, padx=ba['padx'], pady=ba['pady'])

        # Label Text
        self.wb_count_text = StringVar()
        self.wb_count_text.set('')
        self.wb_desc_text = StringVar()
        self.wb_desc_text.set('')
        self.total_wb_count_text = StringVar()
        self.total_wb_count_text.set('')
        self.total_wb_desc_text = StringVar()
        self.total_wb_desc_text.set('')
        self.total_view_count_text = StringVar()
        self.total_view_count_text.set('')
        self.total_view_desc_text = StringVar()
        self.total_view_desc_text.set('')
        self.view_count_text = StringVar()
        self.view_count_text.set('')
        self.view_desc_text = StringVar()
        self.view_desc_text.set('')

        # Progress Bars Style
        self.s = Style()
        self.s.theme_use('classic')
        self.s.configure('blue.Horizontal.TProgressbar', troughcolor=self.default_colors['sub_bg'], background=self.default_colors['main_bg'], thickness=25)

        # Right Frame Grid Components -- Labels and Progress Bars
        self.total_wb_desc_label = Label(self.right_top_frame, textvariable=self.total_wb_desc_text, fg=self.default_colors['fg'], bg=self.default_colors['sub_bg'], font=la['font'], anchor=E)
        self.wb_total_progressbar = Progressbar(self.right_top_frame, style='blue.Horizontal.TProgressbar', length=600)
        self.total_wb_count_label = Label(self.right_top_frame, textvariable=self.total_wb_count_text, fg=self.default_colors['fg'], bg=self.default_colors['sub_bg'], font=la['font'], anchor=W)

        self.wb_desc_label = Label(self.right_top_frame, textvariable=self.wb_desc_text, fg=self.default_colors['fg'], bg=self.default_colors['sub_bg'], font=la['font'], anchor=E)
        self.wb_progressbar = Progressbar(self.right_top_frame, style='blue.Horizontal.TProgressbar', length=600)
        self.wb_count_label = Label(self.right_top_frame, textvariable=self.wb_count_text, fg=self.default_colors['fg'], bg=self.default_colors['sub_bg'], font=la['font'], anchor=W)

        self.total_view_desc_label = Label(self.right_top_frame, textvariable=self.total_view_desc_text, fg=self.default_colors['fg'], bg=self.default_colors['sub_bg'], font=la['font'], anchor=E)
        self.total_view_progressbar = Progressbar(self.right_top_frame, style='blue.Horizontal.TProgressbar', length=600)
        self.total_view_count_label = Label(self.right_top_frame, textvariable=self.total_view_count_text, fg=self.default_colors['fg'], bg=self.default_colors['sub_bg'], font=la['font'], anchor=W)

        self.view_desc_label = Label(self.right_top_frame, textvariable=self.view_desc_text, fg=self.default_colors['fg'], bg=self.default_colors['sub_bg'], font=la['font'], anchor=E)
        self.view_progressbar = Progressbar(self.right_top_frame, style='blue.Horizontal.TProgressbar', length=600)
        self.view_count_label = Label(self.right_top_frame, textvariable=self.view_count_text, fg=self.default_colors['fg'], bg=self.default_colors['sub_bg'], font=la['font'], anchor=W)

        self.view_list = Text(self.right_bottom_frame, font='none 12 bold', bg=self.default_colors['sub_sub_bg'], fg=self.default_colors['main_bg'], yscrollcommand=self.scrollbar.set)

    def view_directory_locator(self):
        self.directory_location = tkFileDialog.askdirectory(title='Locate the folder that contains the views you would like to search')

    def search_views(self):
        """ Will be used to search the directory's workbooks for the field written in the search bar.

        :return: Will probably run other functions that do things like count the views with that field, count the workbooks, etc.
        """
        # Clears everything on the right frame when the function first runs
        self.reset_metrics()
        self.right_frame_forget()

        if self.directory_location != None and self.search_bar.get() != '':
            for the_file in os.listdir(self.directory_location):
                if the_file.split('.')[-1] == 'twb':
                    # set the path to the file
                    path = self.directory_location + '/' + the_file
                    # set the tree and root
                    tree = ET.parse(path)
                    root = tree.getroot()
                    sheet_count = 0
                    view_count = 0
                    wb_count = 0
                    for sheet in root.iter("worksheet"):
                        sheet_count += 1
                        self.total_view_count += 1
                    for column in root.iter('column-instance'):
                        name = str(column.attrib.get('name'))
                        regex = '\:.*?\:'
                        for m in re.finditer(regex, name):
                            if self.search_bar.get() == str(m.group(0)).replace(':', ''):
                                wb_count = 1
                                view_count += 1
                                self.view_count += 1
                    if wb_count == 1:
                        self.view_list.insert(END, '  ' + str(view_count) + '/' + str(sheet_count) + ' views - ' + the_file + '\n')

                    self.wb_count += wb_count
                    self.total_wb_count += 1

            # Sets the labels that come before the bars
            self.wb_desc_text.set('Workbooks Using ' + self.search_bar.get())
            self.total_wb_desc_text.set('Workbooks Total')
            self.view_desc_text.set('Views Using ' + self.search_bar.get())
            self.total_view_desc_text.set('Views Total')
            # Sets the maximum values for each bar
            self.wb_total_progressbar['maximum'] = self.total_wb_count
            self.wb_progressbar['maximum'] = self.total_wb_count
            self.total_view_progressbar['maximum'] = self.total_view_count
            self.view_progressbar['maximum'] = self.total_view_count
            # Runs the function that spawns the bars and labels, and starts the bar animations
            self.right_frame_grid()
            self.total_wb_progress_start()

    def general_search(self):
        """ Used to search all workbooks in the directory for general stats, such as a list of all fields and how many times they are used.

        :return:
        """
        # Clears everything on the right frame when the function first runs
        self.reset_metrics()
        self.right_frame_forget()

        if self.directory_location != None:
            sheet_count = 0
            unique_fields = {}
            self.right_bottom_frame.pack(side=BOTTOM, fill=BOTH)
            self.scrollbar.pack(side=RIGHT, fill=Y)
            self.scrollbar.config(command=self.right_top_canvas.yview)
            self.right_top_canvas.config(yscrollcommand=self.scrollbar.set)
            self.right_top_canvas.pack(side=LEFT, expand=True, fill=BOTH)
            # Counts how many views each field is used in, in all workbooks
            for the_file in os.listdir(self.directory_location):
                if the_file.split('.')[-1] == 'twb':
                    # set the path to the file
                    path = self.directory_location + '/' + the_file
                    # set the tree and root
                    tree = ET.parse(path)
                    root = tree.getroot()
                    for sheet in root.iter("worksheet"):
                        sheet_count += 1
                    for column in root.iter('column-instance'):
                        name = str(column.attrib.get('name'))
                        regex = '\:.*?\:'
                        for m in re.finditer(regex, name):
                            field = str(m.group(0)).replace(':', '')
                            if field in unique_fields and 'Calculation_' not in field and '(copy' not in field and field != 'usr' and field != 'qk':
                                unique_fields[field] = unique_fields[field] + 1
                            elif 'Calculation_' not in field and '(copy' not in field and field != 'usr' and field != 'qk':
                                unique_fields[field] = 1
            sorted_unique_fields = sorted(unique_fields.items(), key=operator.itemgetter(1), reverse=self.var.get())
            row = 0
            max_bar_value = max(unique_fields.iteritems(), key=operator.itemgetter(1))[1]
            # Creates the bar visual for the list of fields and their view counts
            for tup in sorted_unique_fields:
                self.bar_field = Label(self.right_top_canvas, text=tup[0], font='none 12 bold', bg=self.default_colors['sub_bg'], fg=self.default_colors['fg'], anchor=E)
                self.bar_field.grid(row=row, column=0, sticky=N + S + E + W, pady=1)
                self.bar = Progressbar(self.right_top_canvas, style='blue.Horizontal.TProgressbar', length=600)
                self.bar['maximum'] = max_bar_value
                self.bar['value'] = tup[1]
                self.bar.grid(row=row, column=1, sticky=N + S + E + W, pady=1)
                self.bar_count = Label(self.right_top_canvas, text=str(tup[1]), font='none 12 bold', bg=self.default_colors['sub_bg'], fg=self.default_colors['fg'], anchor=W)
                self.bar_count.grid(row=row, column=2, sticky=N + S + E + W, pady=1)
                row += 1

            pprint(sorted_unique_fields)

    def total_wb_progress_start(self):
        if self.total_wb_start < self.total_wb_count:
            self.total_wb_start += (self.total_wb_count * 0.05)
            self.wb_total_progressbar['value'] = self.total_wb_start
            self.after(1, self.total_wb_progress_start)
        else:
            self.total_wb_count_text.set(str(self.total_wb_count))
            self.wb_progress_start()

    def wb_progress_start(self):
        if self.wb_start < self.wb_count:
            self.wb_start += (self.wb_count * 0.05)
            self.wb_progressbar['value'] = self.wb_start
            self.after(1, self.wb_progress_start)
        else:
            self.wb_count_text.set(str(self.wb_count))
            self.total_view_progress_start()

    def total_view_progress_start(self):
        if self.total_view_start < self.total_view_count:
            self.total_view_start += (self.total_view_count * 0.05)
            self.total_view_progressbar['value'] = self.total_view_start
            self.after(1, self.total_view_progress_start)
        else:
            self.total_view_count_text.set(str(self.total_view_count))
            self.view_progress_start()

    def view_progress_start(self):
        if self.view_start < self.view_count:
            self.view_start += (self.view_count * 0.05)
            self.view_progressbar['value'] = self.view_start
            self.after(1, self.view_progress_start)
        else:
            self.view_count_text.set(str(self.view_count))
            # Workbook list with view counts
            self.view_list.pack(side=TOP, fill=BOTH, expand=True)

    def reset_metrics(self):
        self.total_wb_count = 0
        self.total_wb_start = 0
        self.wb_count = 0
        self.wb_start = 0
        self.total_view_count = 0
        self.total_view_start = 0
        self.view_count = 0
        self.view_start = 0
        self.wb_desc_text.set('')
        self.total_wb_desc_text.set('')
        self.wb_count_text.set('')
        self.total_wb_count_text.set('')
        self.wb_progressbar['value'] = 0
        self.wb_total_progressbar['value'] = 0
        self.view_list.delete(1.0, END)

    def toggle_fullscreen(self):
        if self.fs:
            self.fs = False
        else:
            self.fs = True
        self.attributes('-fullscreen', self.fs)

    def right_frame_grid(self):
        self.right_top_frame.pack(side=TOP, fill=BOTH)
        self.right_bottom_frame.pack(side=TOP, fill=BOTH, expand=True, pady=6, padx=4)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.scrollbar.config(command=self.view_list.yview)
        # Row 0 - Total Workbooks
        self.total_wb_desc_label.grid(row=0, column=0, sticky=N + S + E + W)
        self.wb_total_progressbar.grid(row=0, column=1, sticky=N + S + E + W, padx=2, pady=2)
        self.total_wb_count_label.grid(row=0, column=2, sticky=N + S + E + W)

        # Row 1 - Workbooks with searched field
        self.wb_desc_label.grid(row=1, column=0, sticky=N + S + E + W)
        self.wb_progressbar.grid(row=1, column=1, sticky=N + S + E + W, padx=2, pady=2)
        self.wb_count_label.grid(row=1, column=2, sticky=N + S + E + W)

        # Row 2 - Total Views
        self.total_view_desc_label.grid(row=2, column=0, sticky=N + S + E + W)
        self.total_view_progressbar.grid(row=2, column=1, sticky=N + S + E + W, padx=2, pady=2)
        self.total_view_count_label.grid(row=2, column=2, sticky=N + S + E + W)

        # Row 3 - Views with searched fields
        self.view_desc_label.grid(row=3, column=0, sticky=N + S + E + W)
        self.view_progressbar.grid(row=3, column=1, sticky=N + S + E + W, padx=2, pady=2)
        self.view_count_label.grid(row=3, column=2, sticky=N + S + E + W)

    def right_frame_forget(self):
        self.view_list.pack_forget()
        self.right_top_frame.pack_forget()
        self.right_bottom_frame.pack_forget()
        self.right_top_canvas.pack_forget()
        self.scrollbar.pack_forget()
        # Row 0 - Total Workbooks
        self.total_wb_desc_label.grid_forget()
        self.wb_total_progressbar.grid_forget()
        self.total_wb_count_label.grid_forget()

        # Row 1 - Workbooks with searched field
        self.wb_desc_label.grid_forget()
        self.wb_progressbar.grid_forget()
        self.wb_count_label.grid_forget()

        # Row 2 - Total Views
        self.total_view_desc_label.grid_forget()
        self.total_view_progressbar.grid_forget()
        self.total_view_count_label.grid_forget()

        # Row 3 - Views with searched fields
        self.view_desc_label.grid_forget()
        self.view_progressbar.grid_forget()
        self.view_count_label.grid_forget()


app = Program()
app.mainloop()

# flask
