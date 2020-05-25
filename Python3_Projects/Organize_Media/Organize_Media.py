import threading
import shutil
import os
import json
from tkinter import *
from tkinter.ttk import Progressbar, Style, Separator
from PIL import Image, ImageTk
from imdb import IMDb
from copy import deepcopy

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
                      wraplength=self.wraplength)
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
        self.filtered_media = {}
        self.all_media_info = {}
        self.imdb_info = {}
        self.disable_buttons = False

        # Frames
        self.left_frame = Frame(self, bg=self.colors['main'])
        self.left_frame.grid(row=0, column=0, sticky=N+S+E+W, padx=14, pady=14)
        self.status_bar = Label(self, text='\n\n', font='none 10 italic', bg=self.colors['sub'],
                                fg=self.colors['alt'], relief=SUNKEN)
        self.status_bar.grid(row=1, column=0, columnspan=3, sticky=N+S+E+W, padx=2, pady=2)

        middle_frame = Frame(self, bg=self.colors['main'], bd=2, relief=SUNKEN)
        middle_frame.grid(row=0, column=1, sticky=NSEW, padx=12, pady=12)
        selected_files_header = Label(middle_frame, text='Selected Media', anchor=N, bg=self.colors['main'],
                                      fg=self.colors['alt'], relief=RAISED, font='none 12 bold')
        selected_files_header.pack(side=TOP, fill=X)
        self.middle_canvas = Canvas(middle_frame, bg=self.colors['sub'], bd=0, highlightthickness=0, relief=RIDGE)
        canvas_frame = Frame(self.middle_canvas, bg=self.colors['sub'])
        self.middle_canvas.create_window((0, 0), window=canvas_frame, anchor=NW)
        canvas_frame.bind('<Configure>', self.mid_canvas_dim)
        y_scroll_bar = Scrollbar(middle_frame, command=self.middle_canvas.yview, orient=VERTICAL)
        x_scroll_bar = Scrollbar(middle_frame, command=self.middle_canvas.xview, orient=HORIZONTAL)
        self.middle_canvas.config(yscrollcommand=y_scroll_bar.set, xscrollcommand=x_scroll_bar.set)
        self.selected_files_label = Label(canvas_frame, text='', anchor=NW, bg=self.colors['sub'],
                                          fg=self.colors['alt'], font='none 10', justify=LEFT)
        y_scroll_bar.pack(side=RIGHT, fill=Y)
        x_scroll_bar.pack(side=BOTTOM, fill=X)
        self.middle_canvas.pack(side=LEFT, fill=BOTH)
        self.selected_files_label.pack(side=TOP, fill=BOTH)

        # Images -- Used later by the filter window
        image_width, image_height = 32, 32
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
        self.buttons_config = {
            'Organize': {'image': 'organize_media.png', 'command': self.organize_media,
                         'tooltip': f'Organize your media into Movies/TV Shows folders:\n\n{note_text}'},
            'Locate Media': {'image': 'red_dir.png', 'command': save_paths_to_json,
                             'tooltip': 'Select your downloads folder and media folder; Your media folder will contain'
                                        ' your "Movies" and "TV Shows" folders'},
            'Select Media': {'image': 'filter.png', 'command': self.start_filter_window,
                             'tooltip': 'Gathers a list of media files from your downloads folder, and'
                                        ' allows you to filter which files to organize'},
            'Rename Media': {'image': 'rename.png', 'command': self.rename_media,
                             'tooltip': 'Renames all media files in your Media folder; I.e. all files in the'
                                        ' "Movies" and "TV Shows" folders'},
            'Flatten': {'image': 'flatten.png', 'command': self.flatten_movie_files,
                        'tooltip': 'Moves all movies from sub folders in the "Movies" folder to the'
                                   ' main "Movies" folder'}
        }
        # Create a button for each button in the config
        image_width, image_height = 64, 64
        for label, cfg in self.buttons_config.items():
            # Put each button in a frame for padding purposes
            padding_frame = Frame(self.left_frame, bg=self.colors['main'])
            padding_frame.pack(side=TOP, padx=10, pady=10, fill=X)
            # row += 1
            # Button image
            with Image.open(f'Images/{cfg["image"]}') as img:
                image = img.resize((image_width, image_height), Image.ANTIALIAS)
                self.buttons_config[label]['image_obj'] = ImageTk.PhotoImage(image)
            # Button
            button = Button(padding_frame, image=self.buttons_config[label]['image_obj'], command=cfg['command'],
                            cursor="hand2", bg=self.colors['main'], relief=FLAT, anchor=CENTER,
                            state=DISABLED if label == 'Organize' else NORMAL)
            button.pack(fill=X)
            self.buttons_config[label]['button'] = button
            # Button label
            Label(padding_frame, text=label, font='none 10 bold',
                  bg=self.colors['main'], fg=self.colors['alt']).pack(fill=X)
            # Button tooltip
            CreateToolTip(button, cfg['tooltip'], bg=self.colors['main'], fg=self.colors['alt'])

        # Progress Bar
        self.s = Style()
        self.style = 'text.Horizontal.TProgressbar'
        self.s.theme_use('classic')
        # Add label in the layout
        self.s.layout(self.style,
                      [('Horizontal.Progressbar.trough',
                        {'children': [('Horizontal.Progressbar.pbar',
                                       {'side': 'left', 'sticky': 'ns'})],
                         'sticky': 'nsew'}),
                       ('Horizontal.Progressbar.label', {'sticky': ''})])
        # Set initial progress bar text
        self.s.configure(self.style, text='\n\n', troughcolor=self.colors['sub'],
                         background=self.colors['special'], foreground=self.colors['alt'],
                         font='none 10 bold', thickness=45)

        w = self.winfo_width()
        self.progress_bar = Progressbar(self.status_bar, style=self.style, length=w-8)

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

    def mid_canvas_dim(self, event):
        w, h = self.starting_width*2, self.starting_height*2
        self.middle_canvas.configure(scrollregion=self.middle_canvas.bbox("all"), width=w, height=h)

    def append_imdb_info(self, db, title, kind, year):
        possible_titles = [x for x in db.search_movie(title, results=1)
                           if (not year or x['year'] == year) and x['kind'] == kind]
        imdb_info = db.get_movie(possible_titles[0].movieID) if possible_titles \
            else {'long imdb title': title, 'genres': []}

        self.imdb_info[title]['info'] = imdb_info
        self.imdb_info[title]['episodes'] = db.get_movie_episodes(possible_titles[0].movieID)['data']['episodes'] \
            if kind == 'tv series' and possible_titles else None

        self.s.configure(style=self.style, text=f'Gathering info from IMDb...\n{kind.title()}: {title}\n')
        self.progress_bar['value'] += 1
        if self.progress_bar['value'] == self.progress_bar['maximum']:
            file_list = []
            # Get info for each file from IMDb
            for file, info in self.all_media_info.items():
                season = info['season']
                episode = info['episode']
                title = info['file_title']
                kind = info['kind']

                if file not in file_list:
                    file_list.append(file)

                new_title = self.imdb_info[title]['info']['long imdb title'].replace('"', '')
                # Show Title S01E01 - Episode Name
                ep_title = f" - {self.imdb_info[title]['episodes'][season][episode]['title']}" \
                    if kind == 'tv series' and self.imdb_info[title]['episodes'] else ''
                file_name = f'{title} S{0 if season < 10 else ""}{season}' \
                            f'E{0 if episode < 10 else ""}{episode}' \
                            f'{ep_title}' if kind == 'tv series' else new_title

                self.all_media_info[file]['title'] = new_title
                self.all_media_info[file]['file_name'] = file_name
                self.all_media_info[file]['episode_title'] = ep_title
                self.all_media_info[file]['genres'] = self.imdb_info[title]['info']['genres']

            self.all_media_info = {t: self.all_media_info[t] for t in sorted(file_list)}
            self.filter_window()
            self.progress_complete()

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
        db = IMDb()
        temp = {}
        # Get a list of files to gather info for, and extract info from the local file
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

                    if title not in self.imdb_info:
                        self.imdb_info[title] = {'info': None, 'episodes': None, 'year': year, 'kind': kind}
                    elif not self.imdb_info[title]['year'] and year:
                        self.imdb_info[title]['year'] = year

                    temp[file] = {'title': None, 'episode_title': None, 'file_name': None,
                                  'genres': None, 'file_title': title, 'kind': kind, 'year': year,
                                  'season': season, 'episode': episode, 'path': current_file_path}

        if not temp:
            self.progress_complete()
            self.s.configure(style=self.style, text='\nNo Media Detected\n')

        elif [f for f in temp.keys() if f not in self.all_media_info.keys()]:
            copy_info = deepcopy(self.all_media_info)
            for k, v in temp.items():
                if k not in self.all_media_info:
                    copy_info[k] = v
            self.all_media_info = deepcopy(copy_info)
            del copy_info

            # Set progress bar based on files we will be getting info for
            self.progress_bar['maximum'] = len(self.imdb_info.keys())
            self.progress_bar['value'] = 0

            for imdb_title, imdb_info in {k: v for k, v in self.imdb_info.items() if not v['info']}.items():
                threading.Thread(target=self.append_imdb_info,
                                 args=(db, imdb_title, imdb_info['kind'], imdb_info['year'])).start()

        else:
            self.filter_window()
            self.progress_complete()

    def filter_window(self):
        """ The filter window that appears to filter the media files to be sorted.

        :param dl_path: The path to the download folder
        :return:
        """
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

        def canvas_dim(event):
            # top.update()
            w, h = top.winfo_width(), top.winfo_height()
            self.top_canvas.configure(scrollregion=self.top_canvas.bbox("all"), width=w, height=h)

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
                                         width=40, bg=self.colors['main'], fg=self.colors['alt'], justify=LEFT)
                media_type_label.pack(side=LEFT, fill=X, expand=True)
                if kind == 'movie':
                    movie_frame = Frame(frame, bg=self.colors['sub'], bd=2, relief=SUNKEN)
                    movie_frame.pack(fill=X, expand=True)
                for t in set([v['title'] for k, v in files.items() if v['kind'] == kind]):
                    if kind == 'tv series':
                        show_frame = Frame(frame, bg=self.colors['main'])
                        show_frame.pack(fill=X, expand=True)
                        show_title_button = Button(show_frame, text='- ' + t, font='none 10 bold', anchor=NW,
                                                   cursor='hand2', bg=self.colors['special'], fg=self.colors['alt'],
                                                   justify=LEFT)
                        show_title_button.pack(fill=X, expand=True)
                        show_checklist_frame = Frame(show_frame, bg=self.colors['sub'], bd=2, relief=SUNKEN)
                        show_checklist_frame.pack(fill=X, expand=True)
                        show_title_button['command'] = lambda x=(show_title_button,
                                                                 show_checklist_frame): collapse_show(x)
                    for file in [f for f, i in files.items() if i['title'] == t]:
                        if kind == 'tv series':
                            dictionary[file] = Checkbutton(show_checklist_frame)
                        else:
                            dictionary[file] = Checkbutton(movie_frame)
                        dictionary[file].config(text=file, onvalue=True, offvalue=False, anchor=NW,
                                                bg=self.colors['sub'], fg=self.colors['alt'],
                                                selectcolor=self.colors['sub'])
                        dictionary[file].var = BooleanVar(value=True)
                        dictionary[file]['variable'] = dictionary[file].var
                        dictionary[file]['command'] = lambda w=dictionary[file]: upon_select(w)
                        dictionary[file].pack(fill=X, expand=True)

                toggle = BooleanVar(value=False)
                toggle_all_button = Button(media_type_frame, image=self.deselect_image, text='deselect', anchor=NW,
                                           cursor='hand2', relief=FLAT, bg=self.colors['main'], justify=LEFT)
                toggle_all_button['command'] = lambda d=(toggle_all_button, dictionary, toggle): toggle_all(d)
                toggle_all_button.pack(side=RIGHT)

        top = Toplevel(bg=self.colors['main'])
        top.title('Select desired media...')
        top.iconbitmap('images/filter.ico')
        w, h = self.winfo_width(), self.winfo_height()
        top.geometry(str(w)+'x'+str(h))
        bottom_frame = Frame(top, bg=self.colors['main'])

        self.top_canvas = Canvas(top, bg=self.colors['main'], bd=0, highlightthickness=0, relief=RIDGE)
        canv_frame = Frame(self.top_canvas, bg=self.colors['main'])
        self.top_canvas.create_window((0, 0), window=canv_frame, anchor=NW)
        top.bind('<Configure>', canvas_dim)
        y_scroll_bar = Scrollbar(top, orient=VERTICAL)
        x_scroll_bar = Scrollbar(top, orient=HORIZONTAL)

        bottom_frame.pack(side=BOTTOM, fill=X)
        x_scroll_bar.pack(side=BOTTOM, fill=X)
        y_scroll_bar.pack(side=RIGHT, fill=Y)
        self.top_canvas.pack(side=LEFT, fill=BOTH, expand=True)

        y_scroll_bar.config(command=self.top_canvas.yview)
        x_scroll_bar.config(command=self.top_canvas.xview)
        self.top_canvas.config(yscrollcommand=y_scroll_bar.set, xscrollcommand=x_scroll_bar.set)

        create_checklist(canv_frame, files=self.filtered_media)

        Separator(bottom_frame).pack(fill=X, expand=True)
        select_button = Button(bottom_frame, text='Select', command=final_select, anchor=SW, cursor='hand2',
                               bg=self.colors['special'], fg=self.colors['alt'], font='none 12 bold')
        select_button.pack(side=BOTTOM, pady=4)

    def rename_media(self):
        if not self.filtered_media:
            self.filtered_media = self.media_files_info(get_downloads_or_media_path(path='media'))
        rename_all_media_in_directory(self.filtered_media)

    def recursively_organize_shows_and_movies(self, delete_folders=True):
        dl_path = get_downloads_or_media_path('downloads')
        media_path = get_downloads_or_media_path('media')
        folders_to_delete = []
        self.progress_bar['maximum'] = len(self.filtered_media.keys())
        self.progress_bar['value'] = 0

        for file, info in self.filtered_media.items():
            path = os.path.dirname(info['path'])
            extension = file.split('.')[-1]
            skip = False
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
            renamed_file = info['file_name'] + '.' + extension
            renamed_file_path = os.path.join(output_folder, renamed_file)
            # Create output folder if it does not exist
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            # Move and then rename file
            if not os.path.exists(output_path) and not os.path.exists(renamed_file_path):
                shutil.move(info['path'], output_path)
                os.rename(output_path, renamed_file_path)
                status_message = f'Moved & Renamed {info["kind"].title()}:\nFrom: {file}\nTo: {renamed_file}'
                # Update status and increment progress bar to show that the file has moved

            elif not os.path.exists(renamed_file_path):
                os.rename(output_path, renamed_file_path)
                # Update status and increment progress bar to show that the file has moved
                status_message = f'File exists in {output_folder},' \
                                 f' Renamed {info["kind"].title()}:\nFrom: {file}\nTo: {renamed_file}'
            else:
                skip = True
                status_message = f'Skipping: {file}\nFile exists in {output_folder}:\n{renamed_file_path}'
            self.progress_bar['value'] += 1
            self.s.configure(style=self.style, text=status_message)
            # Add the moved file's folder path to the list of folders to delete
            if path != dl_path and path not in folders_to_delete and not skip:
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
                            self.s.configure(style=self.style, text=f'Moved:\n{renamed_file}\n')
                            self.progress_bar['value'] = progress_count
            # Delete folders that contained media files that were moved
            if delete_folders:
                for folder in folders_to_delete:
                    if os.path.exists(folder):
                        shutil.rmtree(folder)
            self.progress_complete()
        return None

    def organize_media(self):
        self.progress_bar_appear()
        tl = threading.Thread(target=self.recursively_organize_shows_and_movies)
        tl.start()

    def flatten_movie_files(self):
            self.progress_bar_appear()
            m_path = get_downloads_or_media_path('media')
            tl = threading.Thread(target=self.flatten_movies, args=(m_path,))
            tl.start()

    def start_filter_window(self):
        self.progress_bar_appear()
        dl_path = get_downloads_or_media_path('downloads')
        self.media_files_info(folder_path=dl_path)

    def progress_bar_appear(self):
        self.toggle_buttons_enabled()
        w = self.winfo_width()
        self.progress_bar.config(length=w-8)
        self.progress_bar['value'] = 0
        self.progress_bar.pack(side=LEFT)
        self.s.configure(style=self.style, text='\n\n')

    def progress_complete(self):
        self.toggle_buttons_enabled()
        self.progress_bar['value'] = 0
        self.s.configure(style=self.style, text='\nComplete!\n')

    def toggle_buttons_enabled(self):
        buttons = [v['button'] for k, v in self.buttons_config.items()]
        if self.disable_buttons:
            for b in buttons:
                b.config(state=NORMAL)
            self.disable_buttons = False
        else:
            for b in buttons:
                b.config(state=DISABLED)
            self.disable_buttons = True


app = Organize()
app.mainloop()
