from Tkinter import *
import tkFileDialog
from PIL import Image, ImageTk


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

        # Frames
        self.left_frame = Frame(self, bg=aa['main_bg'])
        self.left_frame.pack(side=LEFT, fill=Y)
        self.top_left_frame = Frame(self.left_frame, bg=aa['main_bg'])
        self.top_left_frame.pack(side=TOP, fill=BOTH)
        self.bottom_left_frame = Frame(self.left_frame, bg=aa['main_bg'])
        self.bottom_left_frame.pack(side=BOTTOM, fill=X)

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
        # Images
        image_width, image_height = 30, 30
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
        self.locate_directory_button = Button(self.top_left_frame, image=self.directory_image, command=self.view_directory_locator, fg=ba['fg_color'], bg=ba['bg_color'], font=ba['font'])
        self.locate_directory_button.pack(side=LEFT, padx=ba['padx'], pady=ba['pady'])
        self.toggle_fs_button = Button(self.bottom_left_frame, image=self.fullscreen_image, command=self.toggle_fullscreen, fg=ba['fg_color'], bg=ba['bg_color'], font=ba['font'])
        self.toggle_fs_button.pack(side=LEFT, padx=ba['padx'], pady=ba['pady'])
        self.exit_button = Button(self.bottom_left_frame, image=self.quit_image, command=quit, fg=ba['fg_color'], bg=ba['bg_color'], font=ba['font'])
        self.exit_button.pack(side=LEFT, padx=ba['padx'], pady=ba['pady'])
        # Search bar & button
        self.search_bar = Entry(self.top_left_frame, fg=ta['fg_color'], bg=ta['bg_color'], font=ta['font'], relief=SUNKEN)
        self.search_bar.pack(side=LEFT, fill=BOTH, expand=True, padx=ta['padx'], pady=ta['pady'])
        self.search_button = Button(self.top_left_frame, image=self.search_image, command=self.search_views, fg=ba['fg_color'], bg=ba['bg_color'], font=ba['font'])
        self.search_button.pack(side=RIGHT, padx=ba['padx'], pady=ba['pady'])

    def view_directory_locator(self):
        self.directory_location = tkFileDialog.askdirectory(title='Locate the folder that contains the views you would like to search')

    def search_views(self):
        """ Will be used to search the views for the field written.

        :return: Will probably run other functions that do things like count the views with that field, count the workbooks, etc.
        """
        print self.search_bar.get()

    def toggle_fullscreen(self):
        if self.fs:
            self.fs = False
        else:
            self.fs = True
        self.attributes('-fullscreen', self.fs)


app = Program()
app.mainloop()

# flask
