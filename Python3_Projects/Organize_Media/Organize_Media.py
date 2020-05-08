import threading
import shutil
import os
import json
from tkinter import *
from tkinter.ttk import Progressbar, Style, Separator
from PIL import Image, ImageTk

from settings.general_functions import tv_show_ep, initcap_file_name, rename_all_media_in_directory
from settings.mo_functions import get_downloads_or_media_path, save_paths_to_json


with open('settings/config.json', 'r') as config:
    configuration = json.load(config)
    media_extensions = configuration['media_extensions']
    required_paths = configuration['required_paths']


class Organize(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.title('Media Organizer 9000')
        self.iconbitmap('Images/organize_media.ico')
        self.resizable(0, 0)

        self.starting_width = self.winfo_width()
        self.starting_height = self.winfo_height()

        self.colors = {
            'main': '#%02x%02x%02x' % (43, 53, 68),
            'sub': '#%02x%02x%02x' % (62, 77, 99),
            'special': '#%02x%02x%02x' % (153, 68, 12),
            'alt': 'white'
        }
        self.configure(bg=self.colors['main'])

        # Frames
        self.left_frame = Frame(self, bg=self.colors['main'])
        self.left_frame.grid(row=0, column=0, sticky=N+S+E+W, padx=2, pady=2)

        self.middle_frame = Frame(self, bg=self.colors['main'])
        self.middle_canvas = Canvas(self.middle_frame, bg=self.colors['main'], bd=0, highlightthickness=0, relief=RIDGE)
        self.canvas_frame = Frame(self.middle_canvas, bg=self.colors['main'])
        self.middle_canvas.create_window((0, 0), window=self.canvas_frame, anchor=NW)
        self.canvas_frame.bind('<Configure>', self.mid_canvas_dim)

        self.right_frame = Frame(self, bg=self.colors['main'])
        self.right_bottom_frame = Frame(self.right_frame, bg=self.colors['main'])

        # Images
        image_width, image_height = 35, 35
        dir_image = Image.open('Images/dir.png')
        dir_image = dir_image.resize((image_width, image_height), Image.ANTIALIAS)
        self.directory_image = ImageTk.PhotoImage(dir_image)
        image_width, image_height = 35, 35
        f_image = Image.open('Images/filter.png')
        f_image = f_image.resize((image_width, image_height), Image.ANTIALIAS)
        self.filter_image = ImageTk.PhotoImage(f_image)

        # Buttons
        organize_button = Button(self.left_frame, text='Organize Media', command=self.organize_media, font='none 14 bold', fg='white', bg=self.colors['special'], width=14)
        organize_button.grid(row=0, column=0, sticky=NW, padx=1, pady=2)
        directory_button = Button(self.left_frame, image=self.directory_image, command=save_paths_to_json, font='none 14 bold', fg='white', bg=self.colors['sub'])
        directory_button.grid(row=0, column=1, sticky=NW, padx=1, pady=2)
        filter_button = Button(self.left_frame, image=self.filter_image, command=self.media_info, font='none 14 bold', fg='white', bg=self.colors['sub'])
        filter_button.grid(row=0, column=2, sticky=NW, padx=1, pady=2)
        rename_button = Button(self.left_frame, text='Rename Media', command=self.rename_media, font='none 14 bold', fg='white', bg=self.colors['sub'], width=14)
        rename_button.grid(row=1, column=0, sticky=NW, padx=1, pady=2)
        flatten_button = Button(self.left_frame, text='Flatten Movies', command=self.flatten_movie_files, font='none 14 bold', fg='white', bg=self.colors['sub'], width=14)
        flatten_button.grid(row=2, column=0, sticky=NW, padx=1, pady=2)
        note_label = Label(self.left_frame, text='- Note about Organize Media -', font='none 11 bold underline', fg='grey', bg=self.colors['main'], width=12, wraplength=220, justify=LEFT)
        note_label.grid(row=3, columnspan=3, sticky=N + S + E + W, pady=2)
        self.label_var = StringVar()
        self.label_var.set('If have a Movies/TV Shows folder with a name other than "Movies" or "TV Shows", in your media folder, you should rename them. Casing matters!\n\nIf you do not have the folders, they will be created for you.')
        note_label = Label(self.left_frame, textvariable=self.label_var, font='none 10 italic', fg='grey', bg=self.colors['main'], width=12, wraplength=260, justify=LEFT)
        note_label.grid(row=4, columnspan=3, sticky=N+S+E+W)

        self.progress_label_text = StringVar()
        self.progress_label_text.set('\n\n')
        progress_label = Label(self.right_frame, textvariable=self.progress_label_text, font='none 16', fg='white', bg=self.colors['main'], justify=LEFT)
        progress_label.pack(side=TOP, anchor=SW)
        self.close_button = Button(self.right_bottom_frame, text='Close', command=self.destroy, font='none 14 bold', fg='white', bg='darkgreen')
        self.s = Style()
        self.s.theme_use('classic')
        self.s.configure('blue.Horizontal.TProgressbar', troughcolor=self.colors['main'], background='darkgreen', thickness=50)
        self.progress_bar = Progressbar(self.right_frame, style='blue.Horizontal.TProgressbar', length=500)

        self.selected_file_header_text = StringVar()
        self.selected_file_header_text.set('')
        selected_files_header = Label(self.middle_frame, textvariable=self.selected_file_header_text, anchor=NW, bg=self.colors['main'], fg='white', font='none 12 bold', justify=LEFT)
        selected_files_header.pack(side=TOP, fill=X)
        self.selected_file_text = StringVar()
        self.selected_file_text.set('')
        selected_files_label = Label(self.canvas_frame, textvariable=self.selected_file_text, anchor=NW, bg=self.colors['main'], fg='white', font='none 10', justify=LEFT)
        selected_files_label.pack(side=TOP, fill=X)
        self.scroll_bar = Scrollbar(self.middle_frame, command=self.middle_canvas.yview)
        self.middle_canvas.config(yscrollcommand=self.scroll_bar.set)
        self.update()
        self.starting_width = self.winfo_width()
        self.starting_height = self.winfo_height()

    @staticmethod
    def get_show_title(tv_show_episode, clean_file_name):
        if tv_show_episode:
            # If the episode is the first part of the file name
            if clean_file_name.split(' ')[0] == tv_show_episode:
                return clean_file_name.replace(tv_show_episode + ' ', '').split('.')[0]
            else:
                return clean_file_name.split(' ' + tv_show_episode)[0]
        return clean_file_name

    @staticmethod
    def rename_media():
        rename_all_media_in_directory(get_downloads_or_media_path(path='media'))

    def mid_canvas_dim(self, *args):
        self.middle_canvas.configure(scrollregion=self.middle_canvas.bbox("all"), width=self.starting_width, height=self.starting_height)

    def media_files_info(self, folder_path='', filtered_media=[]):
        total_count = 0
        media = []
        for path, folders, files in os.walk(folder_path):
            for file in files:
                current_file_path = os.path.join(path, file)
                # If its a media file
                if file.split('.')[-1] in media_extensions and os.path.isfile(current_file_path) and type(file) != list:
                    # If it's a tv show
                    media_file = initcap_file_name(file)
                    tv_show_episode, season = tv_show_ep(media_file)
                    media_file = self.get_show_title(tv_show_episode, media_file)

                    # If there's a list to filter, filter the list
                    if filtered_media:
                        if media_file in filtered_media:
                            total_count += 1
                            if media_file not in media:
                                media.append(media_file)
                    else:
                        total_count += 1
                        if media_file not in media:
                            media.append(media_file)
        return [total_count, sorted(media)]

    def filter_window(self, dl_path):
        """ The filter window that appears to filter the media files to be sorted.

        :param dl_path: The path to the download folder
        :return:
        """
        self.middle_frame.grid_forget()
        self.middle_canvas.pack_forget()
        self.filter_file_list = self.media_files_info(folder_path=dl_path)[-1]

        def upon_select(widget):
            # Add or remove files from list when they are toggled
            if widget.var.get():
                if widget['text'] not in self.filter_file_list:
                    self.filter_file_list.append(widget['text'])
            else:
                if widget['text'] in self.filter_file_list:
                    self.filter_file_list.remove(widget['text'])

        def toggle_all(x):
            button, files_dict = x
            for file, widget in files_dict.items():
                widget.var = BooleanVar(value=False if button.cget('text') == '[   ]' else True)
                widget['variable'] = widget.var
                upon_select(widget)
            if button.cget('text') == '[   ]':
                button['text'] = '[ X ]'
            else:
                button['text'] = '[   ]'

        def final_select():
            self.middle_frame.grid(row=0, column=1, sticky=N+S+E+W, padx=12, pady=12)
            self.middle_canvas.pack(side=LEFT, fill=Y)
            self.scroll_bar.pack(side=RIGHT, fill=Y)
            self.selected_file_header_text.set('Selected Media:')
            self.selected_file_text.set('+ ' + '\n+ '.join(self.filter_file_list))
            top.destroy()

        def canvas_dim(*args):
            top.update()
            w, h = self.starting_width, self.starting_height
            self.top_canvas.configure(scrollregion=self.top_canvas.bbox("all"), width=w, height=h)

        def create_checklist(frame, title, files):
            title_frame = Frame(frame, bg=self.colors['main'])
            title_frame.pack(fill=X)
            label = Label(title_frame, text=title, font='none 12 bold', anchor=NW, bg=self.colors['main'], fg='white',
                          justify=LEFT)
            label.pack(side=LEFT, fill=X)
            dictionary = dict()
            for file in files:
                dictionary[file] = Checkbutton(frame, text=file, onvalue=True, offvalue=False, anchor=NW,
                                         bg=self.colors['main'], fg='white', selectcolor=self.colors['main'])
                dictionary[file].var = BooleanVar(value=True)
                dictionary[file]['variable'] = dictionary[file].var
                dictionary[file]['command'] = lambda w=dictionary[file]: upon_select(w)
                dictionary[file].pack(fill=X)

            toggle_all_button = Button(title_frame, text='[   ]', font='none 10', anchor=NW,
                                       bg=self.colors['main'], fg='white', justify=LEFT)
            toggle_all_button['command'] = lambda d=(toggle_all_button, dictionary): toggle_all(d)
            toggle_all_button.pack(side=RIGHT)

        top = Toplevel(bg=self.colors['main'])
        top.title('Select desired media...')
        top.iconbitmap('images/filter.ico')
        w, h = self.starting_width, self.starting_height
        top.geometry(str(w+20)+'x'+str(h+40))
        top.resizable(0, 0)
        top_frame = Frame(top, bg=self.colors['main'])

        self.top_canvas = Canvas(top_frame, bg=self.colors['main'], bd=0, highlightthickness=0, relief=RIDGE)
        canv_frame = Frame(self.top_canvas, bg=self.colors['main'])
        bottom_frame = Frame(top, bg=self.colors['main'])
        self.top_canvas.create_window((0, 0), window=canv_frame, anchor=NW)
        canv_frame.bind('<Configure>', canvas_dim)
        scroll_bar = Scrollbar(top_frame)

        top_frame.pack(side=TOP, fill=BOTH)
        self.top_canvas.pack(side=LEFT, fill=BOTH)
        bottom_frame.pack(side=BOTTOM, fill=X)
        scroll_bar.pack(side=RIGHT, fill=Y)

        scroll_bar.config(command=self.top_canvas.yview)
        self.top_canvas.config(yscrollcommand=scroll_bar.set)

        # Generate TV Show checklist
        create_checklist(canv_frame, title='TV Shows', files=[file for file in self.filter_file_list if '.' not in file])
        # Add a separator
        Separator(canv_frame).pack(fill=X)
        # Generate Movie Checklist
        create_checklist(canv_frame, title='Movies', files=[file for file in self.filter_file_list if '.' in file])

        Separator(bottom_frame).pack(fill=X)
        button = Button(bottom_frame, text='Select', command=final_select, anchor=SW, bg=self.colors['special'], fg='white', font='none 12 bold')
        button.pack(side=BOTTOM, fill=Y, pady=4)

    def recursively_organize_shows_and_movies(self, dl_path, media_path, filtered_media, delete_folders=True):
        movies_folder = os.path.join(media_path, 'Movies')
        folders_to_delete = []
        progress_count = 0
        total_count = self.media_files_info(folder_path=dl_path, filtered_media=filtered_media)[0]
        self.progress_bar['maximum'] = total_count
        self.progress_bar['value'] = progress_count
        for path, folders, files in os.walk(dl_path):
            for file in files:
                movies_file_path = os.path.join(movies_folder, file)
                current_file_path = os.path.join(path, file)
                extension = file.split('.')[-1] if os.path.isfile(current_file_path) else None
                renamed_file = initcap_file_name(file)
                tv_show_episode, season = tv_show_ep(renamed_file)
                show_title = self.get_show_title(tv_show_episode, renamed_file)
                if extension and extension in media_extensions \
                        and (show_title in filtered_media or renamed_file in filtered_media):
                    # Route for TV Shows
                    if tv_show_episode:
                        show_folder = os.path.join(media_path, 'TV Shows', show_title, 'Season ' + str(season))
                        show_file_path = os.path.join(show_folder, file)
                        renamed_file = renamed_file.split(tv_show_episode)[0] + tv_show_episode + '.' + extension
                        if not os.path.exists(show_folder):
                            os.makedirs(show_folder)
                        shutil.move(current_file_path, show_file_path)
                        os.rename(show_file_path, os.path.join(show_folder, renamed_file))
                        self.progress_label_text.set('Moved & Renamed Show:\nFrom: ' + file + '\nTo: ' + renamed_file)
                    # Route for Movies
                    else:
                        if not os.path.exists(movies_folder):
                            os.makedirs(movies_folder)
                        shutil.move(current_file_path, movies_file_path)
                        os.rename(movies_file_path, os.path.join(movies_folder, renamed_file))
                        self.progress_label_text.set('Moved & Renamed Movie:\nFrom: ' + file + '\nTo: ' + renamed_file)
                    progress_count += 1
                    self.progress_bar['value'] = progress_count
                    if path != dl_path and path not in folders_to_delete:
                        folders_to_delete.append(path)
        # Delete folders that contained media files that were moved
        if delete_folders:
            for folder in folders_to_delete:
                if os.path.exists(folder):
                    shutil.rmtree(folder)
        self.progress_complete()
        return None

    def flatten_movies(self, media_path, delete_folders=True):
        movies_folder = os.path.join(media_path, 'Movies')
        folders_to_delete = []
        total_count = 0
        progress_count = 0
        for path, folders, files in os.walk(media_path):
            for file in files:
                current_file_path = os.path.join(path, file)
                if file.split('.')[-1] in media_extensions and os.path.isfile(current_file_path):
                    total_count += 1
        self.progress_bar['maximum'] = progress_count
        if os.path.exists(movies_folder):
            for path, folders, files in os.walk(movies_folder):
                if path != movies_folder:
                    # Moves Media files NOT in the main folder
                    for file in files:
                        movies_file_path = os.path.join(movies_folder, file)
                        current_file_path = os.path.join(path, file)
                        renamed_file = initcap_file_name(file)
                        tv_show_episode, season = tv_show_ep(renamed_file)
                        # Route for TV Shows
                        if tv_show_episode == [] and file.split('.')[-1] in media_extensions and os.path.isfile(current_file_path):
                            if path not in folders_to_delete:
                                folders_to_delete.append(path)
                            shutil.move(current_file_path, movies_file_path)
                            os.rename(movies_file_path, os.path.join(movies_folder, renamed_file))
                            progress_count += 1
                            self.progress_label_text.set('Moved:\n'+renamed_file)
                            self.progress_bar['value'] = progress_count
            # Delete folders that contained media files that were moved
            if delete_folders:
                for folder in folders_to_delete:
                    if os.path.exists(folder):
                        shutil.rmtree(folder)
            self.progress_complete()
        return None

    def organize_media(self):
        dl_path = get_downloads_or_media_path('downloads')
        m_path = get_downloads_or_media_path('media')
        try:
            self.filter_file_list == None
        except AttributeError:
            self.filter_file_list = self.media_files_info(folder_path=dl_path)
        self.progress_bar_appear()
        tl = threading.Thread(target=self.recursively_organize_shows_and_movies, args=(dl_path, m_path, self.filter_file_list))
        tl.start()

    def flatten_movie_files(self):
            self.progress_bar_appear()
            m_path = get_downloads_or_media_path('media')
            tl = threading.Thread(target=self.flatten_movies, args=(m_path,))
            tl.start()

    def media_info(self):
            dl_path = get_downloads_or_media_path('downloads')
            self.filter_window(dl_path)
            tl = threading.Thread(target=self.media_files_info, kwargs={'folder_path': dl_path})
            tl.start()

    def progress_bar_appear(self):
        self.right_frame.grid(row=0, column=2, sticky=N + S + E + W, padx=12, pady=12)
        self.right_bottom_frame.pack(side=BOTTOM, fill=BOTH)
        self.progress_bar['value'] = 0
        self.progress_bar.pack(side=TOP)
        self.progress_label_text.set('\n\n')
        self.close_button.pack_forget()

    def progress_complete(self):
        self.progress_label_text.set('\nComplete!')
        self.close_button.pack(side=RIGHT, fill=X, anchor=SE, pady=4)


app = Organize()
app.mainloop()
