import threading
import shutil
import os
import json
from tkinter import *
from tkinter.ttk import Progressbar, Style, Separator
from PIL import Image, ImageTk
from imdb import IMDb
from copy import deepcopy
from pprint import pprint

from settings.general_functions import tv_show_ep, initcap_file_name, rename_all_media_in_directory
from settings.mo_functions import get_downloads_or_media_path, save_paths_to_json


with open('settings/config.json', 'r') as config:
    configuration = json.load(config)
    media_extensions = configuration['media_extensions']
    required_paths = configuration['required_paths']


class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info', bg='#ffffff', fg='#000000'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.bg = bg
        self.fg = fg
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left',
                       background=self.bg, foreground=self.fg, relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()


class Organize(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.title('Media Organizer 9000')
        self.iconbitmap('Images/organize_media.ico')
        self.resizable(0, 0)

        self.starting_width = self.winfo_width()
        self.starting_height = self.winfo_height()

        self.colors = {
            'main': '#%02x%02x%02x' % (33, 33, 33),
            'sub': '#%02x%02x%02x' % (84, 84, 84),
            'special': '#%02x%02x%02x' % (135, 36, 36),
            'alt': 'white'
        }
        self.configure(bg=self.colors['main'])
        self.filtered_media = None
        self.all_media_info = None
        self.imdb_info = {}

        # Frames
        self.left_frame = Frame(self, bg=self.colors['main'])
        self.left_frame.grid(row=0, column=0, sticky=N+S+E+W, padx=2, pady=2)
        self.status_bar = Label(self, text='\n', font='none 10 italic', bg=self.colors['main'], fg=self.colors['alt'], relief=SUNKEN)
        self.status_bar.grid(row=1, column=0, columnspan=3, sticky=N+S+E+W, padx=2, pady=2)

        self.middle_frame = Label(self, bg=self.colors['main'], relief=SUNKEN)
        self.middle_canvas = Canvas(self.middle_frame, bg=self.colors['sub'], bd=0, highlightthickness=0, relief=RIDGE)
        self.canvas_frame = Frame(self.middle_canvas, bg=self.colors['sub'])
        self.middle_canvas.create_window((0, 0), window=self.canvas_frame, anchor=NW)
        self.canvas_frame.bind('<Configure>', self.mid_canvas_dim)

        self.right_frame = Frame(self, bg=self.colors['main'])
        self.right_bottom_frame = Frame(self.right_frame, bg=self.colors['main'])

        # Images
        image_width, image_height = 35, 35
        dir_image = Image.open('Images/red_dir.png')
        dir_image = dir_image.resize((image_width, image_height), Image.ANTIALIAS)
        self.directory_image = ImageTk.PhotoImage(dir_image)
        f_image = Image.open('Images/filter.png')
        f_image = f_image.resize((image_width, image_height), Image.ANTIALIAS)
        self.filter_image = ImageTk.PhotoImage(f_image)
        deselect_image = Image.open('Images/deselect.png')
        deselect_image = deselect_image.resize((image_width, image_height), Image.ANTIALIAS)
        self.deselect_image = ImageTk.PhotoImage(deselect_image)
        select_image = Image.open('Images/select.png')
        select_image = select_image.resize((image_width, image_height), Image.ANTIALIAS)
        self.select_image = ImageTk.PhotoImage(select_image)

        note_text = 'If you have a Movies/TV Shows folder with a name other than "Movies" or "TV Shows",' \
                    ' in your media folder, you should rename them. Casing matters!\n\n' \
                    'If you do not have the folders, they will be created for you.'

        # Buttons
        organize_button = Button(self.left_frame, text='Organize Media', command=self.organize_media,
                                 font='none 14 bold', cursor="hand2", fg=self.colors['alt'], bg=self.colors['special'], width=14)
        organize_button.grid(row=0, column=0, sticky=NW, padx=1, pady=2)
        directory_button = Button(self.left_frame, image=self.directory_image, command=save_paths_to_json,
                                  cursor="hand2", bg=self.colors['main'], relief=FLAT)
        directory_button.grid(row=0, column=1, sticky=NW, padx=1, pady=2)
        filter_button = Button(self.left_frame, image=self.filter_image, command=self.start_filter_window,
                               cursor="hand2", bg=self.colors['main'], relief=FLAT)
        filter_button.grid(row=0, column=2, sticky=NW, padx=1, pady=2)
        rename_button = Button(self.left_frame, text='Rename Media', command=self.rename_media, font='none 14 bold',
                               fg=self.colors['alt'], bg=self.colors['sub'], cursor="hand2", width=14)
        rename_button.grid(row=1, column=0, sticky=NW, padx=1, pady=2)
        flatten_button = Button(self.left_frame, text='Flatten Movies', command=self.flatten_movie_files,
                                font='none 14 bold', cursor="hand2", fg=self.colors['alt'], bg=self.colors['sub'], width=14)
        flatten_button.grid(row=2, column=0, sticky=NW, padx=1, pady=2)

        # Tooltips
        CreateToolTip(organize_button, f'Organize your media into Movies/TV Shows folders:\n\n{note_text}',
                      bg=self.colors['main'], fg=self.colors['alt'])
        CreateToolTip(directory_button, 'Select your downloads folder and media folder; Your media folder will contain'
                                        ' your "Movies" and "TV Shows" folders',
                      bg=self.colors['main'], fg=self.colors['alt'])
        CreateToolTip(filter_button, 'Gathers a list of media files from your downloads folder, and'
                                     ' allows you to filter which files to organize',
                      bg=self.colors['main'], fg=self.colors['alt'])
        CreateToolTip(rename_button, 'Renames all media files in your Media folder; I.e. all files in the'
                                     ' "Movies" and "TV Shows" folders',
                      bg=self.colors['main'], fg=self.colors['alt'])
        CreateToolTip(flatten_button, 'Moves all movies from sub folders in the "Movies" folder to the'
                                      ' main "Movies" folder',
                      bg=self.colors['main'], fg=self.colors['alt'])

        self.progress_label = Label(self.right_frame, text='\n\n', font='none 16', fg=self.colors['alt'], bg=self.colors['main'], justify=LEFT)
        self.progress_label.pack(side=TOP, anchor=SW)
        self.close_button = Button(self.right_bottom_frame, text='Close', command=self.destroy, cursor='hand2',
                                   font='none 14 bold', fg=self.colors['alt'], bg='darkgreen')
        self.s = Style()
        self.s.theme_use('classic')
        self.s.configure('blue.Horizontal.TProgressbar', troughcolor=self.colors['main'], background='darkgreen', thickness=50)
        self.progress_bar = Progressbar(self.right_frame, style='blue.Horizontal.TProgressbar', length=500)

        self.selected_files_header = Label(self.middle_frame, text='Selected Media', anchor=NW, bg=self.colors['main'],
                                           fg=self.colors['alt'], relief=RAISED, font='none 12 bold')
        self.selected_files_header.pack(side=TOP, fill=X)
        self.selected_files_label = Label(self.canvas_frame, text='', anchor=NW, bg=self.colors['sub'], fg=self.colors['alt'],
                                          font='none 10', justify=LEFT)
        self.selected_files_label.pack(side=TOP, fill=BOTH, expand=True)
        self.scroll_bar = Scrollbar(self.middle_frame, command=self.middle_canvas.yview)
        self.middle_canvas.config(yscrollcommand=self.scroll_bar.set)
        self.update()
        self.starting_width = self.winfo_width()
        self.starting_height = self.winfo_height()

    @staticmethod
    def get_media_title(tv_show_episode, clean_file_name):
        if tv_show_episode:
            # If the episode is the first part of the file name
            if clean_file_name.split(' ')[0] == tv_show_episode:
                clean_file_name = clean_file_name.replace(tv_show_episode + ' ', '').split('.')[0]
                return re.findall(r'^[a-zA-Z ]+\d{0,2}[^\d]|^\d{1,2}[^\d]', clean_file_name)[0].strip()
            else:
                return clean_file_name.split(' ' + tv_show_episode)[0]
        else:
            title = re.findall(r'[a-zA-Z: ]+\d?[^\d]', clean_file_name)
            year = re.findall(r'19\d\d|20\d\d', clean_file_name)
            new_file_name = f'{title[0].strip()} ({year[0]})' if year else title[0]
            return new_file_name

    @staticmethod
    def rename_media():
        rename_all_media_in_directory(get_downloads_or_media_path(path='media'))

    def mid_canvas_dim(self, *args):
        self.middle_canvas.configure(scrollregion=self.middle_canvas.bbox("all"), width=self.starting_width, height=self.starting_height)

    def media_files_info(self, folder_path=''):
        """ Gets information about each media file in a path, from IMDb.

        Output sample:
            'house.s01e01.avi': {'title': 'House (2004)',
                                 'episode_title': 'Pilot',
                                 'file_name': 'House - S01E01 - Pilot',
                                 'kind': 'tv series',
                                 'season': 1,
                                 'episode': 1,
                                 'genres': ['Drama', 'Comedy'],
                                 'path': 'C:/USER/Downloads/house.s01e01.avi'}

        :param folder_path: The path to your media files
        :return: A dictionary of information about each file
        """
        file_list = []
        media_dict = {}
        db = IMDb()

        for path, folders, files in os.walk(folder_path):
            for file in files:
                current_file_path = os.path.join(path, file)
                extension = file.split('.')[-1]
                # If its a media file
                if extension in media_extensions and os.path.isfile(current_file_path) and type(file) != list:
                    renamed_file = initcap_file_name(file)
                    tv_show_episode, season, episode = tv_show_ep(renamed_file)
                    title = self.get_media_title(tv_show_episode, renamed_file)
                    kind = 'tv series' if tv_show_episode else 'movie'
                    year = re.findall(r'20\d\d|19\d\d', file)
                    year = int(year[0]) if year else None

                    if file not in file_list:
                        file_list.append(file)

                    if title not in self.imdb_info:
                        self.status_bar['text'] = f'Gathering {kind.title()} info from IMDb...\n{title}'
                        self.status_bar.update()
                        possible_titles = [x for x in db.search_movie(title, results=1)
                                           if (not year or x['year'] == year) and x['kind'] == kind]
                        info = db.get_movie(possible_titles[0].movieID) if possible_titles \
                            else {'long imdb title': title, 'genres': []}
                        self.imdb_info[title] = {
                            'info':  info,
                            'episodes': db.get_movie_episodes(possible_titles[0].movieID)['data']['episodes'] \
                                if kind == 'tv series' and possible_titles else None
                        }
                    new_title = self.imdb_info[title]['info']['long imdb title'].replace('"', '')
                    # Show Title S01E01 - Episode Name
                    ep_title = f" - {self.imdb_info[title]['episodes'][season][episode]['title']}" \
                        if kind == 'tv series' and self.imdb_info[title]['episodes'] else ''
                    file_name = f'{title} S{0 if season < 10 else ""}{season}' \
                                f'E{0 if episode < 10 else ""}{episode}' \
                                f'{ep_title}' if kind == 'tv series' else new_title

                    media_dict[file] = {
                        'title': new_title,
                        'episode_title': ep_title,
                        'file_name': file_name,
                        'kind': kind,
                        'season': season,
                        'episode': episode,
                        'genres': self.imdb_info[title]['info']['genres'],
                        'path': current_file_path}

        self.status_bar['text'] = f'\n...'
        self.status_bar.update()
        return {t: media_dict[t] for t in sorted(file_list)}

    def filter_window(self, dl_path):
        """ The filter window that appears to filter the media files to be sorted.

        :param dl_path: The path to the download folder
        :return:
        """
        self.middle_frame.grid_forget()
        self.middle_canvas.pack_forget()
        self.all_media_info = self.media_files_info(folder_path=dl_path)
        self.filtered_media = deepcopy(self.all_media_info)

        def upon_select(widget):
            # Add or remove files from list when they are toggled
            if widget.var.get():
                if widget['text'] not in self.filtered_media:
                    self.filtered_media[widget['text']] = deepcopy(self.all_media_info[widget['text']])
                    widget['bg'] = self.colors['sub']
            else:
                if widget['text'] in self.filtered_media:
                    del self.filtered_media[widget['text']]
                    widget['bg'] = self.colors['main']

        def toggle_all(x):
            button, files_dict, toggle = x
            for file, widget in files_dict.items():
                widget.var = BooleanVar(value=toggle.get())
                widget['variable'] = widget.var
                upon_select(widget)
            if toggle.get():
                button['image'] = self.deselect_image
                toggle.set(False)
            else:
                button['image'] = self.select_image
                toggle.set(True)

        def collapse_show(x):
            button, checklist_frame = x
            if button['text'].startswith('-'):
                button['text'] = button['text'].replace('-', '+')
                checklist_frame.pack_forget()
            elif button['text'].startswith('+'):
                button['text'] = button['text'].replace('+', '-')
                checklist_frame.pack(fill=X)

        def final_select():
            self.middle_frame.grid(row=0, column=1, sticky=N+S+E+W, padx=12, pady=12)
            self.middle_canvas.pack(side=LEFT, fill=BOTH)
            self.scroll_bar.pack(side=RIGHT, fill=Y)
            selected_text = ''
            for kind in sorted(list(set([v['kind'] for v in self.filtered_media.values()])), reverse=True):
                selected_text += f'{kind.title()}:\n'
                for title in sorted(list(set([v['title'] for k, v in self.filtered_media.items() if v['kind'] == kind]))):
                    if kind == 'tv series':
                        selected_text += f'   + {title}:\n'
                    for file in sorted(list(set([k for k, v in self.filtered_media.items() if v['title'] == title]))):
                        if kind == 'movie':
                            selected_text += f'   + {file}\n'
                        else:
                            selected_text += f'      + {file}\n'

            self.selected_files_label['text'] = selected_text
            top.destroy()

        def canvas_dim(*args):
            top.update()
            w, h = self.starting_width, self.starting_height
            self.top_canvas.configure(scrollregion=self.top_canvas.bbox("all"), width=w+100, height=h+200)

        def create_checklist(frame, files):
            kind_mapping = {'tv series': 'TV Shows', 'movie': 'Movies'}
            sections = sorted(list(set([i['kind'] for f, i in files.items()])), reverse=True)
            for kind in sections:
                dictionary = dict()
                if sections.index(kind) > 0:
                    # Add a separator between shows and movies
                    Separator(frame).pack(fill=X, expand=True, pady=8)
                media_type_frame = Frame(frame, bg=self.colors['main'])
                media_type_frame.pack(fill=X, expand=True)
                media_type_label = Label(media_type_frame, text=kind_mapping[kind], font='none 12 bold', anchor=NW,
                                         width=32, bg=self.colors['main'], fg=self.colors['alt'], justify=LEFT)
                media_type_label.pack(side=LEFT, fill=X, expand=True)
                for t in set([v['title'] for k, v in files.items() if v['kind'] == kind]):
                    if kind == 'tv series':
                        show_frame = Frame(frame, bg=self.colors['main'])
                        show_frame.pack(fill=X, expand=True)
                        show_title_button = Button(show_frame, text='- ' + t, font='none 10 bold', anchor=NW,
                                                   cursor='hand2', bg=self.colors['special'], fg=self.colors['alt'],
                                                   justify=LEFT)
                        show_title_button.pack(fill=X, expand=True)
                        show_checklist_frame = Frame(show_frame, bg=self.colors['sub'])
                        show_checklist_frame.pack(fill=X, expand=True)
                        show_title_button['command'] = lambda x=(show_title_button, show_checklist_frame): collapse_show(x)
                    for file in [f for f, i in files.items() if i['title'] == t]:
                        if kind == 'tv series':
                            dictionary[file] = Checkbutton(show_checklist_frame)
                        else:
                            dictionary[file] = Checkbutton(frame)
                        dictionary[file].config(text=file, onvalue=True, offvalue=False, anchor=NW,
                                                bg=self.colors['sub'], fg=self.colors['alt'], relief=SUNKEN,
                                                selectcolor=self.colors['sub'])
                        dictionary[file].var = BooleanVar(value=True)
                        dictionary[file]['variable'] = dictionary[file].var
                        dictionary[file]['command'] = lambda w=dictionary[file]: upon_select(w)
                        dictionary[file].pack(fill=X, expand=True)

                toggle = BooleanVar(value=False)
                toggle_all_button = Button(media_type_frame, image=self.deselect_image, text='deselect', anchor=NW,
                                           cursor='hand2', bg=self.colors['special'], justify=LEFT)
                toggle_all_button['command'] = lambda d=(toggle_all_button, dictionary, toggle): toggle_all(d)
                toggle_all_button.pack(side=RIGHT)

        top = Toplevel(bg=self.colors['main'])
        top.title('Select desired media...')
        top.iconbitmap('images/filter.ico')
        w, h = self.starting_width, self.starting_height
        top.geometry(str(w+120)+'x'+str(h+240))
        top.resizable(0, 0)
        top_frame = Frame(top, bg=self.colors['main'])
        bottom_frame = Frame(top_frame, bg=self.colors['main'])

        self.top_canvas = Canvas(top_frame, bg=self.colors['main'], bd=0, highlightthickness=0, relief=RIDGE)
        canv_frame = Frame(self.top_canvas, bg=self.colors['main'])
        self.top_canvas.create_window((0, 0), window=canv_frame, anchor=NW)
        canv_frame.bind('<Configure>', canvas_dim)
        y_scroll_bar = Scrollbar(top_frame)
        x_scroll_bar = Scrollbar(top_frame, orient=HORIZONTAL)

        top_frame.pack(side=TOP, fill=BOTH)
        bottom_frame.pack(side=BOTTOM, fill=X)
        x_scroll_bar.pack(side=BOTTOM, fill=X)
        self.top_canvas.pack(side=LEFT, fill=BOTH)
        y_scroll_bar.pack(side=RIGHT, fill=Y)

        y_scroll_bar.config(command=self.top_canvas.yview)
        x_scroll_bar.config(command=self.top_canvas.xview)
        self.top_canvas.config(yscrollcommand=y_scroll_bar.set, xscrollcommand=x_scroll_bar.set)

        create_checklist(canv_frame, files=self.filtered_media)

        Separator(bottom_frame).pack(fill=X, expand=True)
        select_button = Button(bottom_frame, text='Select', command=final_select, anchor=SW, cursor='hand2',
                               bg=self.colors['special'], fg=self.colors['alt'], font='none 12 bold')
        select_button.pack(side=BOTTOM, pady=4)

    def recursively_organize_shows_and_movies(self, dl_path, media_path, media_info, delete_folders=True):
        folders_to_delete = []
        progress_count = 0
        self.progress_bar['maximum'] = len(media_info.keys())
        self.progress_bar['value'] = progress_count

        for file, info in media_info.items():
            path = os.path.dirname(info['path'])
            extension = file.split('.')[-1]
            # Route for TV Shows
            if info['kind'] == 'tv series':
                output_folder = os.path.join(media_path,
                                             'TV Shows',
                                             info['title'],
                                             f'Season {info["season"]}')
            # Route for Movies
            else:
                output_folder = os.path.join(media_path, 'Movies')
            output_path = os.path.join(output_folder, file)
            renamed_file = media_info[file]['file_name'] + '.' + extension
            # Create output folder if it does not exist
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            # Move and then rename file
            shutil.move(info['path'], output_path)
            os.rename(output_path, os.path.join(output_folder, renamed_file))
            # Update status and increment progress bar to show that the file has moved
            self.progress_label['text'] = f'Moved & Renamed {info["kind"].title()}:\nFrom: {file}\nTo: {renamed_file}'
            progress_count += 1
            self.progress_bar['value'] = progress_count
            # Add the moved file's folder path to the list of folders to delete
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
                            self.progress_label['text'] = 'Moved:\n'+renamed_file
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
        # If the filter file list has not been created, it will create it with all media files in the download location
        if not self.filtered_media:
            self.filtered_media = self.media_files_info(folder_path=dl_path)
        self.progress_bar_appear()
        tl = threading.Thread(target=self.recursively_organize_shows_and_movies,
                              args=(dl_path, m_path, self.filtered_media))
        tl.start()

    def flatten_movie_files(self):
            self.progress_bar_appear()
            m_path = get_downloads_or_media_path('media')
            tl = threading.Thread(target=self.flatten_movies, args=(m_path,))
            tl.start()

    def start_filter_window(self):
            dl_path = get_downloads_or_media_path('downloads')
            self.filter_window(dl_path)

    def progress_bar_appear(self):
        self.right_frame.grid(row=0, column=2, sticky=N + S + E + W, padx=12, pady=12)
        self.right_bottom_frame.pack(side=BOTTOM, fill=BOTH)
        self.progress_bar['value'] = 0
        self.progress_bar.pack(side=TOP)
        self.progress_label['text'] = '\n\n'
        self.close_button.pack_forget()

    def progress_complete(self):
        self.progress_label['text'] = '\nComplete!'
        self.close_button.pack(side=RIGHT, fill=X, anchor=SE, pady=4)


app = Organize()
app.mainloop()
