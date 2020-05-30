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
        self.geometry(f'{int(self.winfo_screenwidth()*0.8)}x{int(self.winfo_screenheight()*0.8)}')
        # self.resizable(0, 0)

        self.colors = {
            'main': '#%02x%02x%02x' % (20, 20, 20),
            'sub': '#%02x%02x%02x' % (35, 35, 35),
            'special': '#%02x%02x%02x' % (92, 15, 128),
            'alt': '#%02x%02x%02x' % (60, 111, 194),
            'font': '#%02x%02x%02x' % (255, 255, 255)
        }
        with open('settings/config.json', 'r') as config:
            self.configuration = json.load(config)
            self.media_extensions = self.configuration['media_extensions']

        self.configure(bg=self.colors['main'])
        ''' Filter media will contain a dictionary like:
            {path: {file_name: name, title: title, kind: kind, ...}}'''
        self.filtered_media = {}
        self.all_media_info = {}
        self.imdb_info = {}
        self.disable_buttons = False
        self.library = 'settings/library_cache.json'

        self.starting_width = self.winfo_width()
        self.starting_height = self.winfo_height()

        # Frames
        self.left_frame = Frame(self, bg=self.colors['main'], bd=2, relief=RAISED)
        self.status_bar = Canvas(self, bg=self.colors['sub'], bd=0, highlightthickness=0,
                                 width=self.starting_width, height=0, relief=SUNKEN)
        self.status_bar.pack(side=BOTTOM, fill=X)
        self.left_frame.pack(side=LEFT, fill=Y, ipadx=14, ipady=14)

        selected_files_header = Label(self, text='Selected Media', anchor=N, bg=self.colors['main'],
                                      fg=self.colors['font'], relief=RAISED, font='none 12 bold')
        selected_files_header.pack(side=TOP, fill=X, ipadx=100)

        self.middle_canvas = Canvas(self, bg=self.colors['sub'], bd=2, highlightthickness=0, relief=FLAT)
        self.canvas_frame = Frame(self.middle_canvas, bg=self.colors['sub'])
        self.bind('<Configure>', self.mid_canvas_dim)
        self.middle_canvas.create_window((0, 0), window=self.canvas_frame, anchor=NW)
        y_scroll_bar = Scrollbar(self, command=self.middle_canvas.yview, orient=VERTICAL)
        x_scroll_bar = Scrollbar(self, command=self.middle_canvas.xview, orient=HORIZONTAL)
        self.middle_canvas.config(yscrollcommand=y_scroll_bar.set, xscrollcommand=x_scroll_bar.set)
        y_scroll_bar.pack(side=RIGHT, fill=Y)
        x_scroll_bar.pack(side=BOTTOM, fill=X)
        self.middle_canvas.pack(side=LEFT, fill=BOTH, ipadx=4)

        # Images -- Used later by the filter window
        image_width, image_height = 24, 24
        deselect_image = Image.open('Images/deselect.png')
        deselect_image = deselect_image.resize((image_width, image_height), Image.ANTIALIAS)
        self.deselect_image = ImageTk.PhotoImage(deselect_image)
        select_image = Image.open('Images/select.png')
        select_image = select_image.resize((image_width, image_height), Image.ANTIALIAS)
        self.select_image = ImageTk.PhotoImage(select_image)
        image_width, image_height = 24, 24
        arrow_image = Image.open('Images/arrow.png')
        arrow_image = arrow_image.resize((image_width, image_height), Image.ANTIALIAS)
        self.arrow_image = ImageTk.PhotoImage(arrow_image)

        note_text = 'If you have a Movies/TV Shows folder with a name other than "Movies" or "TV Shows",' \
                    ' in your media folder, you should rename them. Casing matters!\n\n' \
                    'If you do not have the folders, they will be created for you.'

        # Buttons
        self.buttons_config = {
            'Locate Media': {'image': 'dir.png', 'command': self.locate_media,
                             'tooltip': 'Select your downloads folder and media folder; Your media folder will contain'
                                        ' your "Movies" and "TV Shows" folders'},
            'Select Media': {'image': 'filter.png', 'command': self.on_press_select_media,
                             'tooltip': 'Gathers a list of media files from your downloads folder, and'
                                        ' allows you to filter which files to organize'},
            'Organize': {'image': 'organize_media.png', 'command': self.on_press_organize_media,
                         'tooltip': f'Organize your media into Movies/TV Shows folders:\n\n{note_text}'}
        }
        # Create a button for each button in the config
        image_width, image_height = 64, 64
        for label_text, cfg in self.buttons_config.items():
            # Put each button in a frame for padding purposes
            padding_frame = Frame(self.left_frame, bg=self.colors['main'])
            padding_frame.pack(side=TOP, padx=10, pady=10, fill=X)
            # row += 1
            # Button image
            with Image.open(f'Images/{cfg["image"]}') as img:
                image = img.resize((image_width, image_height), Image.ANTIALIAS)
                self.buttons_config[label_text]['image_obj'] = ImageTk.PhotoImage(image)
            # Button
            button = Button(padding_frame, image=self.buttons_config[label_text]['image_obj'], command=cfg['command'],
                            cursor="hand2", bg=self.colors['main'], relief=FLAT, anchor=CENTER)
            button.pack(fill=X)
            self.buttons_config[label_text]['button'] = button
            # Button label
            label = Label(padding_frame, text=label_text, font='none 10 bold',
                  bg=self.colors['main'], fg=self.colors['font'])
            label.pack(fill=X)
            self.buttons_config[label_text]['label'] = label
            # Button tooltip
            CreateToolTip(button, cfg['tooltip'], bg=self.colors['main'], fg=self.colors['font'])

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
                         background=self.colors['special'], foreground=self.colors['font'],
                         font='none 10 bold', thickness=45)

        w = self.winfo_width()
        self.progress_bar = Progressbar(self.status_bar, style=self.style, length=w-8)
        self.progress_bar.bind('<Configure>', self.on_window_adjust)

        self.buttons_config['Organize']['button'].pack_forget()
        self.buttons_config['Organize']['label'].pack_forget()
        if 'downloads' not in self.configuration:
            self.buttons_config['Select Media']['button'].pack_forget()
            self.buttons_config['Select Media']['label'].pack_forget()


    @staticmethod
    def get_media_title(tv_show_episode, clean_file_name):
        if tv_show_episode:
            # If the episode is the first part of the file name
            if clean_file_name.startswith(tv_show_episode):
                clean_file_name = clean_file_name.replace(f'{tv_show_episode} ', '').split('.')[0]
                return re.findall(r'(^[a-z ]*\d{0,2})[^\d]', clean_file_name, re.IGNORECASE)[0].strip()
            else:
                return clean_file_name.split(f' {tv_show_episode}')[0]
        else:
            title = re.findall(r'([\w: ]+\d?)[^\d]?', clean_file_name, re.IGNORECASE)
            year = re.findall(r'19\d\d|20\d\d', clean_file_name)
            new_file_name = f'{title[0].strip()} ({year[0]})' if year else title[0]
            return new_file_name

    @staticmethod
    def cache_title_info(path, title, year, kind):
        # Create a cache file if the file does not exist
        if not os.path.exists(path):
            with open(path, 'w') as cache_file:
                json.dump({title: {'info': None,
                                        'episodes': None,
                                        'year': year,
                                        'kind': kind}}, cache_file)

        with open(path, 'r') as cache_file:
            cache = json.load(cache_file)
            # Add the title to the cache if it is not in it already
            if title not in cache:
                cache[title] = {'info': None,
                                     'episodes': None,
                                     'year': year,
                                     'kind': kind}
            # Update the year if the year is not cached for this title
            if title in cache and not cache[title]['year'] and year:
                cache[title]['year'] = year
        with open(path, 'w') as cache_file:
            json.dump(cache, cache_file, indent=2)

    @staticmethod
    def get_info_from_library(media_info, library):
        """ Get the info from the libray and apply it to the media_file_info.

        library example:
            'Title': {
                "info": {
                    "long imdb title": "Long Title (1999)",
                    "genres": ["genre", "genre 1"]},
                "episodes": {1: {1: "Episode Title"}}},
                "year": 1999,
                "kind": "tv series"
                  }

        :param media_info: A dictionary of information about each media file
        :param library: A dictionary of information about a series of titles
        :return:
        """
        for folder_path, i in media_info.items():
            for file_path, info in i.items():
                season = info['season'] if info['season'] else None
                episode = info['episode'] if info['episode'] else None
                title = str(info['file_title'])
                extras = False

                new_title = re.sub(r'[^\w\d\-() ]+', '', library[title]['info']['long imdb title'])
                try:
                    ep_title = " - %s" % re.sub(r'[^\d\w ]+', '',
                                                library[title]['episodes'][str(season)][str(episode)]) \
                        if library[title]['episodes'] else ''
                except KeyError:
                    ep_title = ''
                if season and episode:
                    file_name = f'{title} S{0 if season < 10 else ""}{season}' \
                                f'E{0 if episode < 10 else ""}{episode}{ep_title}'
                else:
                    # If it's a movie, use the renamed title from IMDb
                    if not library[title]['episodes']:
                        file_name = new_title
                        ep_title = None
                    # If it is a show that we couldn't extract the episode/season for,
                    # use the cleaned up original file name, and label it as an extra
                    else:
                        file_name = initcap_file_name(info['file_name']).split('.')[0]
                        extras = True

                if library[title]['episodes'] or info['kind'] == 'tv series':
                    media_info[folder_path][file_path]['kind'] = 'tv series'
                else:
                    media_info[folder_path][file_path]['kind'] = 'movie'
                media_info[folder_path][file_path]['title'] = new_title
                media_info[folder_path][file_path]['file_path'] = file_path
                media_info[folder_path][file_path]['renamed_file_name'] = file_name
                media_info[folder_path][file_path]['episode_title'] = ep_title
                media_info[folder_path][file_path]['genres'] = library[title]['info']['genres']
                media_info[folder_path][file_path]['season'] = -1 if extras else season

    @staticmethod
    def get_missing_titles(media_info, library):
        missing_titles = {}
        for folder_path, info in media_info.items():
            for file_path, file_info in info.items():
                if file_info['file_title'] not in library or not library[file_info['file_title']]['info']:
                    if file_info['file_title'] not in missing_titles or \
                            not missing_titles[file_info['file_title']]['year'] and file_info['year']:
                        missing_titles[file_info['file_title']] = {"info": None, "episodes": None,
                                                                   "year": file_info['year'], "kind": file_info['kind']}

        return missing_titles

    def on_window_adjust(self, event):
        """ Handles resizing progress bar, when the app is resized """
        w, h = self.winfo_width(), self.winfo_height()
        self.progress_bar.config(length=w-8)

    def mid_canvas_dim(self, event):
        """ Handles resizing of the 'Selected Media' portion of the app, when the app is resized """
        w, h = self.winfo_width(), self.starting_height
        self.middle_canvas.configure(scrollregion=self.middle_canvas.bbox("all"), width=w, height=h)

    def merge_temp_files_to_library(self):
        """ Merges all temp files to the main library file, and removes the temp files.

        :return: library json dict
        """
        with open(self.library, 'r') as cache:
            library = json.load(cache)
        for temp_cache_name in os.listdir('settings'):
            if temp_cache_name.startswith('TEMP_'):
                with open(f'settings/{temp_cache_name}', 'r') as temp_cache:
                    temp = json.load(temp_cache)
                    for k, v in temp.items():
                        library[k] = v
                # Delete the temp cache file
                os.remove(f'settings/{temp_cache_name}')
        with open(self.library, 'w') as cache:
            json.dump(library, cache, indent=2)
        return library

    def append_imdb_info(self, db, title, kind, year):
        # Open temp cache for this title
        with open(f'settings/TEMP_{title}.json', 'r') as cache:
            temp = json.load(cache)
        possible_titles = [x for x in db.search_movie(title, results=1)
                           if (not year or x['year'] == year) and x['kind'] == kind]

        if possible_titles:
            imdb_info = db.get_movie(possible_titles[0].movieID)
        else:
            imdb_info = {'long imdb title': str(title), 'genres': []}
        try:
            temp[str(title)]['info'] = {'long imdb title': imdb_info['long imdb title'],
                                        'genres': imdb_info['genres']}
        except KeyError as e:
            print(temp)
            print(title)
            raise Exception(e)
            self.destroy()
        if kind == 'tv series' and possible_titles:
            temp[str(title)]['episodes'] = {
                k: {key: value['title'] for key, value in v.items()}
                for k, v in db.get_movie_episodes(possible_titles[0].movieID)['data']['episodes'].items()}

        else:
            temp[str(title)]['episodes'] = None

        # Save info gathered from IMDb to temp cached file
        with open(f'settings/TEMP_{title}.json', 'w') as cache:
            json.dump(temp, cache)
        # Update progress
        self.s.configure(style=self.style, text=f'Gathered info from IMDb...\n{kind.title()}: {title}\n')
        self.progress_bar['value'] += 1

        # If this is the final task
        if self.progress_bar['value'] == self.progress_bar['maximum']:
            # Once all tasks have cached to their TEMP files, combine the temp files with the main library file
            library = self.merge_temp_files_to_library()
            self.progress_complete('\nAll info gathered from IMDb!\n')
            self.get_info_from_library(self.all_media_info, library)
            self.filtered_media = self.filter_window(self.all_media_info)

    def get_media_info_from_paths(self, paths):
        """ Gets all media information from media files in the given paths

        :param paths: A list of paths to media files
        :return: A dictionary of information about each file
        """
        file_info = {}
        # Get a list of files to gather info for, and extract info from the local file
        for folder_path in paths:
            file_info[folder_path] = {}
            for path, folders, files in sorted(os.walk(folder_path)):
                for file in sorted(files):
                    current_file_path = os.path.join(path, file)
                    extension = file.split('.')[-1]
                    # If its a media file
                    if extension in self.media_extensions and os.path.isfile(current_file_path):
                        split_path = [x for x in path.split(folder_path) if x]
                        if split_path:
                            top_folder = split_path[-1] if split_path[-1][0] not in ['\\', '/'] \
                                else split_path[-1][1:]
                            top_folder = top_folder.split('\\')[0].split('/')[0]
                            top_folder_title = str(self.get_media_title(None, initcap_file_name(top_folder))).title()
                        else:
                            top_folder_title = None
                        renamed_file = initcap_file_name(file)
                        tv_show_episode, season, episode = tv_show_ep(renamed_file)
                        title = str(self.get_media_title(tv_show_episode, renamed_file)).title()
                        kind = 'tv series' if tv_show_episode else 'movie'
                        year = re.findall(r'20\d\d|19\d\d', file)
                        year = int(year[0]) if year else None

                        file_info[folder_path][current_file_path] = {
                            'title': None, 'episode_title': None, 'genres': None, 'renamed_file_name': None,
                            'file_name': file, 'file_title': title, 'top_folder_title': top_folder_title,
                            'kind': kind, 'year': year, 'season': season, 'episode': episode, }
            if not file_info[folder_path]:
                del file_info[folder_path]

        top_folder_dict = {}
        for folder_path, info in file_info.items():
            for file_path, i in info.items():
                if i['top_folder_title']:
                    if i['top_folder_title'] not in top_folder_dict:
                        top_folder_dict[i['top_folder_title']] = {'title_list': [i['file_title']],
                                                                  'kind': i['file_title'],
                                                                  'year': i['year']}
                    elif i['top_folder_title'] in top_folder_dict:
                        if i['file_title'] not in top_folder_dict[i['top_folder_title']]['title_list']:
                            top_folder_dict[i['top_folder_title']]['title_list'].append(i['file_title'])
                        if i['kind'] == 'tv series':
                            top_folder_dict[i['top_folder_title']]['kind'] = i['kind']
                        if i['year']:
                            top_folder_dict[i['top_folder_title']]['year'] = i['year']

        for top_folder, info in top_folder_dict.items():
            top_folder_dict[top_folder]['num_unique_titles'] = len(info['title_list'])
        for folder_path, info in file_info.items():
            for file_path, i in info.items():
                if i['top_folder_title']:
                    file_info[folder_path][file_path]['kind'] = top_folder_dict[i['top_folder_title']]['kind']
                    file_info[folder_path][file_path]['year'] = top_folder_dict[i['top_folder_title']]['year']
                    if top_folder_dict[i['top_folder_title']]['num_unique_titles'] > 1:
                        file_info[folder_path][file_path]['file_title'] = i['top_folder_title']

        return file_info

    def media_files_info(self, folder_paths=[]):
        """ Gets information about each media file in a path, from IMDb.

        Output sample:
            'C:/USER/Downloads': {
                'C:/USER/Downloads/house.s01e01.avi': {
                    'title': 'House (2004)',
                    'episode_title': 'Pilot',
                    'file_title': 'House',
                    'renamed_file_name': 'House - S01E01 - Pilot',
                    'kind': 'tv series',
                    'season': 1,
                    'episode': 1,
                    'genres': ['Drama', 'Comedy'],
                    'file_name': 'house.s01e01.avi'}}

        :param folder_paths: The path to your media files
        :return: A dictionary of information about each file
        """
        files_info = self.get_media_info_from_paths(folder_paths)

        if not files_info:
            self.progress_bar_appear()
            self.progress_complete('\nNo Media Detected...\n')
            return None

        if not os.path.exists(self.library):
            with open(self.library, 'w') as cache_file:
                json.dump({}, cache_file)
        # Read the library
        with open(self.library, 'r') as cache_file:
            library = json.load(cache_file)

        missing_titles = self.get_missing_titles(files_info, library)

        if missing_titles:

            for title, info in missing_titles.items():
                with open(f'settings/TEMP_{title}.json', 'w') as temp_cache:
                    json.dump({title: info}, temp_cache)

            # Set progress bar based on files we will be getting info for
            self.progress_bar_appear()
            self.progress_bar['maximum'] = len(missing_titles.keys())
            self.progress_bar['value'] = 0
            self.all_media_info = files_info
            db = IMDb()
            for imdb_title, imdb_info in missing_titles.items():
                threading.Thread(target=self.append_imdb_info,
                                 args=(db, imdb_title, imdb_info['kind'], imdb_info['year'])).start()

        else:
            self.get_info_from_library(files_info, library)
            self.filtered_media = self.filter_window(files_info)

    def filter_window(self, all_media):
        """ The filter window that appears to filter the media files to be sorted.

        :param all_media: The dictionary of all the media to filter
        :return: Filtered media
        """
        filtered_media = deepcopy(all_media)

        def upon_select(widget):
            d = widget['destination']
            fp = widget['file_path']
            # Add or remove files from list when they are toggled
            if widget['button'].var.get():
                if fp not in filtered_media[d]:
                    filtered_media[d][fp] = deepcopy(all_media[d][fp])
                    widget['button']['bg'] = self.colors['alt']
            else:
                if fp in filtered_media[d]:
                    del filtered_media[d][fp]
                    widget['button']['bg'] = self.colors['main']

        def toggle_all(x):
            button, files_dict, toggle = x
            for file, widget in files_dict.items():
                widget['button'].var = BooleanVar(value=toggle.get())
                widget['button']['variable'] = widget['button'].var
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
            # Reset tree
            for item in self.canvas_frame.children.values():
                item.pack_forget()
            # Create tree
            inner_frame = Frame(self.canvas_frame, bg=self.colors['sub'])
            inner_frame.pack(fill=BOTH, expand=True)
            for folder_path, info in filtered_media.items():
                if info:
                    destination = os.path.basename(folder_path).title()
                    destination_frame = Frame(inner_frame, bg=self.colors['sub'], bd=2, relief=SUNKEN)
                    destination_frame.pack(side=LEFT, fill=BOTH, expand=True)
                    destination_label = Label(destination_frame, text=destination, relief=RAISED, font='none 12 bold',
                                              bg=self.colors['main'], fg=self.colors['font'])
                    destination_label.pack(side=TOP, fill=X)
                for kind in sorted(list(set([v['kind'] for v in info.values()])), reverse=True):
                    media_type = 'TV Shows' if kind == 'tv series' else 'Movies'
                    kind_frame = Frame(destination_frame, bg=self.colors['sub'])
                    kind_frame.pack(side=TOP, fill=X)
                    kind_label = Label(kind_frame, text=media_type, font='none 12 bold', anchor=W,
                                       fg=self.colors['font'], bg=self.colors['sub'])
                    kind_label.pack(side=TOP, fill=X)
                    for title in sorted(list(set([v['title'] for k, v in info.items() if v['kind'] == kind]))):
                        if kind == 'tv series':
                            title_frame = Frame(destination_frame, bg=self.colors['sub'])
                            title_frame.pack(side=TOP, fill=X, padx=30)
                            title_arrow = Label(title_frame, image=self.arrow_image, bg=self.colors['sub'])
                            title_arrow.pack(side=LEFT, fill=X)
                            title_label = Label(title_frame, text=title, font='none 11 bold',
                                                bg=self.colors['sub'], fg=self.colors['font'])
                            title_label.pack(side=LEFT, fill=X)
                            for season in sorted(list(set([v['season']
                                                           for v in info.values() if v['title'] == title]))):
                                season_frame = Frame(destination_frame, bg=self.colors['sub'])
                                season_frame.pack(side=TOP, fill=X, padx=60)
                                season_arrow = Label(season_frame, image=self.arrow_image, bg=self.colors['sub'])
                                season_arrow.pack(side=LEFT, fill=X)
                                season_text = f'Season {season}' if season != -1 else 'Extras'
                                season_label = Label(season_frame, text=season_text, font='none 10 bold',
                                                     bg=self.colors['sub'], fg=self.colors['font'])
                                season_label.pack(side=LEFT, fill=X)
                                for file in sorted(list(set([v['renamed_file_name'] for v in info.values()
                                                             if v['title'] == title and v['season'] == season]))):
                                    file_frame = Frame(destination_frame, bg=self.colors['sub'])
                                    file_frame.pack(side=TOP, fill=X, padx=90)
                                    file_label = Label(file_frame, text=file, font='none 9 bold',
                                                       bg=self.colors['sub'], fg=self.colors['font'])
                                    file_label.pack(side=LEFT, fill=X)
                        if kind == 'movie':
                            for file in sorted(list(set([v['renamed_file_name'] for v in info.values()
                                                         if v['title'] == title]))):
                                file_frame = Frame(destination_frame, bg=self.colors['sub'])
                                file_frame.pack(side=TOP, fill=X, padx=30)
                                # file_arrow = Label(file_frame, image=self.arrow_image, bg=self.colors['sub'])
                                # file_arrow.pack(side=LEFT, fill=X)
                                file_label = Label(file_frame, text=file, font='none 9 bold',
                                                   bg=self.colors['sub'], fg=self.colors['font'])
                                file_label.pack(side=LEFT, fill=X)
            self.toggle_buttons_enabled()
            top.destroy()

        def canvas_dim(event):
            w, h = top.winfo_width(), top.winfo_height()
            self.top_canvas.configure(scrollregion=self.top_canvas.bbox("all"), width=w, height=h)

        def create_checklist(frame, files):
            kind_mapping = {'tv series': 'TV Shows', 'movie': 'Movies'}
            for folder_path, info in files.items():
                media_destination = os.path.basename(folder_path).title()
                destination_frame = Frame(frame, bg=self.colors['main'], bd=2, relief=SUNKEN)
                destination_frame.pack(side=LEFT, fill=BOTH, expand=True)
                destination_title = Label(destination_frame, text=media_destination, relief=RAISED,
                                          bg=self.colors['main'], fg=self.colors['font'], font='none 12 bold')
                destination_title.pack(side=TOP, fill=X)
                sections = sorted(list(set([i['kind'] for f, i in info.items()])), reverse=True)
                for kind in sections:
                    kind_dict = dict()
                    if sections.index(kind) > 0:
                        # Add a separator between shows and movies
                        Separator(destination_frame).pack(fill=X, pady=8)
                    media_type_frame = Frame(destination_frame, bg=self.colors['main'])
                    media_type_frame.pack(side=TOP, fill=X, anchor=NW)
                    media_type_label = Label(media_type_frame, text=kind_mapping[kind], font='none 12 bold', anchor=NW,
                                             width=50, bg=self.colors['main'], fg=self.colors['font'], justify=LEFT)
                    media_type_label.pack(side=LEFT, fill=X)
                    if kind == 'movie':
                        movie_frame = Frame(destination_frame, bg=self.colors['sub'], bd=2, relief=SUNKEN)
                        movie_frame.pack(side=TOP, fill=X, anchor=NW)
                    for t in set([v['title'] for k, v in info.items() if v['kind'] == kind]):
                        dictionary = dict()
                        if kind == 'tv series':
                            show_frame = Frame(destination_frame, bg=self.colors['main'])
                            show_frame.pack(side=TOP, fill=X, anchor=NW)
                            show_title_frame = Frame(show_frame, bg=self.colors['main'])
                            show_title_frame.pack(side=TOP, fill=X, anchor=NW)
                            show_title_button = Button(show_title_frame, text='+ ' + t, font='none 10 bold', anchor=NW,
                                                       cursor='hand2', bg=self.colors['special'], fg=self.colors['font'],
                                                       justify=LEFT)
                            show_title_button.pack(side=LEFT, fill=X, expand=True, anchor=NW)
                            show_checklist_frame = Frame(show_frame, bg=self.colors['alt'], bd=2, relief=SUNKEN)
                            show_checklist_frame.pack(side=TOP, fill=X, anchor=NW)
                            show_title_button['command'] = lambda x=(show_title_button,
                                                                     show_checklist_frame): collapse_show(x)
                            show_checklist_frame.pack_forget()
                        for file_path, i in {f: i for f, i in info.items() if i['title'] == t}.items():
                            dictionary[file_path] = i
                            if kind == 'tv series':
                                dictionary[file_path]['button'] = Checkbutton(show_checklist_frame)
                            else:
                                dictionary[file_path]['button'] = Checkbutton(movie_frame)
                            dictionary[file_path]['button'].config(text=i['renamed_file_name'], onvalue=True, offvalue=False,
                                                              anchor=NW, bg=self.colors['alt'], fg=self.colors['font'],
                                                              selectcolor=self.colors['main'])
                            dictionary[file_path]['button'].var = BooleanVar(value=True)
                            dictionary[file_path]['button']['variable'] = dictionary[file_path]['button'].var
                            dictionary[file_path]['button']['command'] = lambda w=dictionary[file_path]: upon_select(w)
                            dictionary[file_path]['button'].pack(side=TOP, fill=X, expand=True, anchor=NW)
                            dictionary[file_path]['destination'] = folder_path
                            kind_dict[file_path] = dictionary[file_path]
                        if kind == 'tv series':
                            toggle_title = BooleanVar(value=False)
                            toggle_all_title_button = Button(show_title_frame, image=self.deselect_image,
                                                             text='deselect', anchor=NW, cursor='hand2',
                                                             relief=FLAT, bg=self.colors['main'], justify=LEFT)
                            toggle_all_title_button['command'] = lambda d=(toggle_all_title_button,
                                                                           dictionary, toggle_title): toggle_all(d)
                            toggle_all_title_button.pack(side=RIGHT)
                    toggle = BooleanVar(value=False)
                    toggle_all_button = Button(media_type_frame, image=self.deselect_image, text='deselect', anchor=NW,
                                               cursor='hand2', relief=FLAT, bg=self.colors['main'], justify=LEFT)
                    toggle_all_button['command'] = lambda d=(toggle_all_button, kind_dict, toggle): toggle_all(d)
                    toggle_all_button.pack(side=RIGHT, anchor=NW)

        top = Toplevel(bg=self.colors['main'])
        top.title('Select desired media...')
        top.iconbitmap('images/filter.ico')
        top.focus_force()
        w, h = self.winfo_width(), self.winfo_height()
        top.geometry(str(w)+'x'+str(h))
        bottom_frame = Frame(top, bg=self.colors['main'])
        self.toggle_buttons_enabled()

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

        create_checklist(canv_frame, files=filtered_media)

        Separator(bottom_frame).pack(fill=X, expand=True)
        select_button = Button(bottom_frame, text='Select', command=final_select, anchor=SW, cursor='hand2',
                               bg=self.colors['special'], fg=self.colors['font'], font='none 12 bold')
        select_button.pack(side=BOTTOM, pady=4)
        self.wait_window(top)
        return filtered_media

    def recursively_organize_shows_and_movies(self, delete_folders=False):
        dl_path = get_downloads_or_media_path('downloads')
        media_path = get_downloads_or_media_path('media')
        folders_to_delete = []
        self.progress_bar_appear()
        self.progress_bar['maximum'] = len(self.filtered_media.keys())
        self.progress_bar['value'] = 0

        for folder_path, i in self.filtered_media.items():
            for file_path, info in i.items():
                path = os.path.dirname(file_path)
                file = os.path.basename(file_path)
                extension = file.split('.')[-1]
                skip = False
                # Route for TV Shows
                if info['kind'] == 'tv series':
                    season_folder = 'Extras' if info["season"] == -1 else f'Season {info["season"]}'
                    output_folder = os.path.join(media_path, 'TV Shows', info['title'], season_folder)
                # Route for Movies
                else:
                    output_folder = os.path.join(media_path, 'Movies')
                output_path = os.path.join(output_folder, file)
                renamed_file = info['renamed_file_name'] + '.' + extension
                renamed_file_path = os.path.join(output_folder, renamed_file)
                # Create output folder if it does not exist
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                # Move and then rename file
                if not os.path.exists(output_path) and not os.path.exists(renamed_file_path):
                    shutil.move(file_path, output_path)
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
        self.progress_complete('\nMedia Organized!\n')
        return None

    def todo_window(self):

        def upon_select(widget):
            if widget['button'].var.get():
                if widget['todo'] not in final_todo_list:
                    final_todo_list.append(widget['todo'])
                    widget['button']['bg'] = self.colors['alt']
            else:
                if widget['todo'] in final_todo_list:
                    final_todo_list.remove(widget['todo'])
                    widget['button']['bg'] = self.colors['main']

        def on_submit():
            self.toggle_buttons_enabled()
            top.destroy()

        top = Toplevel(bg=self.colors['main'])
        top.title('Select desired media...')
        top.iconbitmap('images/filter.ico')
        top.focus_force()
        self.toggle_buttons_enabled()

        final_todo_list = []

        todo_list = {
            'downloads': 'Organize media from Downloads',
            'media': 'Organize media from Movie and TV Shows'
        }

        Label(top, text='Choose which media to organize...',
              bg=self.colors['main'], fg=self.colors['font']).pack(side=TOP, fill=X)

        top_frame = Frame(top, bg=self.colors['main'], bd=2, relief=SUNKEN)
        top_frame.pack(side=TOP, fill=BOTH, expand=True)
        bottom_frame = Frame(top, bg=self.colors['main'], bd=2, relief=RAISED)
        bottom_frame.pack(side=BOTTOM, fill=X)

        dictionary = dict()
        for i, desc in todo_list.items():
            dictionary[i] = {'button': Checkbutton(top_frame, text=desc, onvalue=True, offvalue=False,
                                                   anchor=NW, bg=self.colors['alt'], fg=self.colors['font'],
                                                   selectcolor=self.colors['main'])}
            dictionary[i]['button'].var = BooleanVar(value=True)
            final_todo_list.append(i)
            dictionary[i]['button']['variable'] = dictionary[i]['button'].var
            dictionary[i]['button']['command'] = lambda w=dictionary[i]: upon_select(w)
            dictionary[i]['button'].pack(side=TOP, fill=X, padx=2, pady=2)
            dictionary[i]['todo'] = i
        submit_button = Button(bottom_frame, text='Okay', command=on_submit,
                               bg=self.colors['special'], fg=self.colors['font'])
        submit_button.pack()
        self.wait_window(top)
        return final_todo_list

    def on_press_select_media(self):
        """
        When you press "Select Media" the following should happen:
            - Popup window displaying a checklist of options for things that will happen:
                - Move media from Downloads to Movies and TV Shows folders
                - Organize media already in the Movie and TV Shows folders
            - After choosing one or both options a Filter window will appear
            - The filter window will have two possible columns; One of downloads and one for existing media
            - Once files are selected, a button will appear to start organizing
        """
        # POPUP: Checklist of actions
        options = self.todo_window()
        if options:
            paths = []
            for option in options:
                if option == 'media':
                    path = get_downloads_or_media_path(option)
                    paths.append(os.path.join(path, 'TV Shows'))
                    paths.append(os.path.join(path, 'Movies'))
                else:
                    paths.append(get_downloads_or_media_path(option))

            self.media_files_info(folder_paths=paths)
            # Button Appears: Organize
        self.organize_button_appear()

    def on_press_organize_media(self):
        """ Start organizing media """
        tl = threading.Thread(target=self.recursively_organize_shows_and_movies)
        tl.start()

    def left_frame_buttons_appear(self):
        self.buttons_config['Select Media']['button'].pack()
        self.buttons_config['Select Media']['label'].pack()

    def organize_button_appear(self):
        self.buttons_config['Organize']['button'].pack()
        self.buttons_config['Organize']['label'].pack()

    def progress_bar_appear(self):
        self.toggle_buttons_enabled()
        w = self.winfo_width()
        self.progress_bar.config(length=w-8)
        self.progress_bar['value'] = 0
        self.progress_bar.pack(side=BOTTOM)
        self.s.configure(style=self.style, text='\n\n')

    def progress_complete(self, message):
        self.toggle_buttons_enabled()
        self.progress_bar['value'] = 0
        self.s.configure(style=self.style, text=message)

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

    def locate_media(self):
        save_paths_to_json()
        with open('settings/config.json', 'r') as config:
            self.configuration = json.load(config)
        if "downloads" in self.configuration:
            self.left_frame_buttons_appear()


app = Organize()
app.mainloop()
