from Tix import *
import tkFileDialog
from ttk import Progressbar, Style
from PIL import Image, ImageTk
import xml.etree.cElementTree as ET
import os
import re


class Program(Tk):

    def __init__(self):
        Tk.__init__(self)

        aa = {
            # Application Attributes
            'main_bg': 'deepskyblue4',
            'sub_bg': 'deepskyblue2'
        }
        self.fs = False
        self.title('Field View Searcher')
        self.geometry(str(int(self.winfo_screenwidth()*0.8)) + 'x' + str(int(self.winfo_screenheight()*0.8)))
        self.attributes('-fullscreen', self.fs)  # Fullscreen the program
        # self.state('zoomed')  # Maximize the program
        self.config(bg=aa['sub_bg'])

        self.directory_location = None
        self.tree = None
        self.root = None
        self.total_wb_count = 0
        self.wb_count = 0
        self.total_wb_start = 0
        self.wb_start = 0

        # Frames
        self.left_frame = Frame(self, bg=aa['main_bg'])
        self.left_frame.pack(side=LEFT, fill=Y)
        self.left_top_frame = Frame(self.left_frame, bg=aa['main_bg'])
        self.left_top_frame.pack(side=TOP, fill=BOTH)
        self.left_bottom_frame = Frame(self.left_frame, bg=aa['main_bg'])
        self.left_bottom_frame.pack(side=BOTTOM, fill=BOTH)

        self.right_frame = Frame(self, bg=aa['sub_bg'], relief=SUNKEN)
        self.right_frame.pack(side=LEFT, fill=BOTH, expand=True)
        self.right_top_frame = Frame(self.right_frame, bg=aa['sub_bg'], relief=SUNKEN)
        self.right_top_frame.pack(side=TOP, fill=BOTH)
        self.right_bottom_frame = Frame(self.right_frame, bg=aa['sub_bg'], relief=SUNKEN)
        self.right_bottom_frame.pack(side=TOP, fill=BOTH, expand=True, pady=6, padx=4)


        ba = {
            # Button Attributes
            'padx': 2,
            'pady': 4,
            'font': 'none 12 bold',
            'bg_color': 'white',
            'fg_color': 'deepskyblue4'
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
            'font': 'none 14 bold',
            'bg_color': aa['sub_bg'],
            'fg_color': 'white'
        }
        # Images
        image_width, image_height = 35, 35
        dir_image = Image.open('Images/blue_folder.png')
        dir_image = dir_image.resize((image_width, image_height), Image.ANTIALIAS)
        self.directory_image = ImageTk.PhotoImage(dir_image)
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
        self.locate_directory_button = Button(self.left_top_frame, image=self.directory_image, command=self.view_directory_locator, fg=ba['fg_color'], bg=ba['bg_color'], font=ba['font'])
        self.locate_directory_button.pack(side=LEFT, padx=ba['padx'], pady=ba['pady'])
        self.toggle_fs_button = Button(self.left_bottom_frame, image=self.fullscreen_image, command=self.toggle_fullscreen, fg=ba['fg_color'], bg=ba['bg_color'], font=ba['font'])
        self.toggle_fs_button.pack(side=LEFT, padx=ba['padx'], pady=ba['pady'])
        self.exit_button = Button(self.left_bottom_frame, image=self.quit_image, command=quit, fg=ba['fg_color'], bg=ba['bg_color'], font=ba['font'])
        self.exit_button.pack(side=LEFT, padx=ba['padx'], pady=ba['pady'])
        # Search bar & button
        self.search_bar = Entry(self.left_top_frame, fg=ta['fg_color'], bg=ta['bg_color'], font=ta['font'], relief=SUNKEN)
        self.search_bar.pack(side=LEFT, fill=BOTH, expand=True, padx=ta['padx'], pady=ta['pady'])
        self.search_button = Button(self.left_top_frame, image=self.search_image, command=self.search_views, fg=ba['fg_color'], bg=ba['bg_color'], font=ba['font'])
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

        # Progress Bars Style
        self.s = Style()
        self.s.theme_use('classic')
        self.s.configure('blue.Horizontal.TProgressbar', troughcolor=aa['sub_bg'], background=aa['main_bg'], thickness=45)

        # Right Frame Grid Components -- Labels and Progress Bars
        self.total_wb_desc_label = Label(self.right_top_frame, textvariable=self.total_wb_desc_text, fg=la['fg_color'], bg=la['bg_color'], font=la['font'], anchor=E)
        self.wb_total_progressbar = Progressbar(self.right_top_frame, style='blue.Horizontal.TProgressbar', length=400)
        self.total_wb_count_label = Label(self.right_top_frame, textvariable=self.total_wb_count_text, fg=la['fg_color'], bg=la['bg_color'], font=la['font'], anchor=W)

        self.wb_desc_label = Label(self.right_top_frame, textvariable=self.wb_desc_text, fg=la['fg_color'], bg=la['bg_color'], font=la['font'], anchor=E)
        self.wb_progressbar = Progressbar(self.right_top_frame, style='blue.Horizontal.TProgressbar', length=400)
        self.wb_count_label = Label(self.right_top_frame, textvariable=self.wb_count_text, fg=la['fg_color'], bg=la['bg_color'], font=la['font'], anchor=W)

        self.view_list = Text(self.right_bottom_frame, font='none 12 bold', bg='skyblue1', fg=aa['main_bg'])

        # Tooltips
        self.tooltips = Balloon(self)
        for sub in self.tooltips.subwidgets_all():  # Makes the tooltip background a specified color
            sub.config(bg='white')
        self.tooltips.subwidget('label')['image'] = BitmapImage()  # Removes arrow in the top left corner
        self.tooltips.bind_widget(self.toggle_fs_button, balloonmsg='Fullscreen')
        self.tooltips.bind_widget(self.exit_button, balloonmsg='Exit')
        self.tooltips.bind_widget(self.locate_directory_button, balloonmsg='Locate views directory')
        self.tooltips.bind_widget(self.search_button, balloonmsg='Search')

    def view_directory_locator(self):
        self.directory_location = tkFileDialog.askdirectory(title='Locate the folder that contains the views you would like to search')

    def search_views(self):
        """ Will be used to search the directory's workbooks for the field written in the search bar.

        :return: Will probably run other functions that do things like count the views with that field, count the workbooks, etc.
        """
        self.reset_metrics()

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
                    for column in root.iter('column-instance'):
                        name = str(column.attrib.get('name'))
                        regex = '\:.*?\:'
                        for m in re.finditer(regex, name):
                            if self.search_bar.get() == str(m.group(0)).replace(':', ''):
                                wb_count = 1
                                view_count += 1
                    if wb_count == 1:
                        self.view_list.insert(END, '  ' + the_file + ' - ' + str(view_count) + '/' + str(sheet_count) + ' views\n')

                    self.wb_count += wb_count
                    self.total_wb_count += 1

            self.wb_desc_text.set('Workbooks Using ' + self.search_bar.get())
            self.total_wb_desc_text.set('Workbooks Total')
            self.wb_total_progressbar['maximum'] = self.total_wb_count
            self.wb_progressbar['maximum'] = self.total_wb_count
            self.right_frame_grid()
            self.total_wb_progress_start()
            # self.wb_progress_start()

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
            # Workbook list with view counts
            self.view_list.pack(side=TOP, fill=BOTH, expand=True)

    def reset_metrics(self):
        self.total_wb_count = 0
        self.wb_count = 0
        self.total_wb_start = 0
        self.wb_start = 0
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
        # Row 0 - Total Workbooks
        self.total_wb_desc_label.grid(row=0, column=0, sticky=N + S + E + W)
        self.wb_total_progressbar.grid(row=0, column=1, sticky=N + S + E + W, padx=2, pady=2)
        self.total_wb_count_label.grid(row=0, column=2, sticky=N + S + E + W)

        # Row 1 - Workbooks with searched field
        self.wb_desc_label.grid(row=1, column=0, sticky=N + S + E + W)
        self.wb_progressbar.grid(row=1, column=1, sticky=N + S + E + W, padx=2, pady=2)
        self.wb_count_label.grid(row=1, column=2, sticky=N + S + E + W)


app = Program()
app.mainloop()

# flask
