import threading
import shutil
import os
import json
from tkinter import *
from tkinter.ttk import Progressbar, Style, Separator
from PIL import Image, ImageTk
from copy import deepcopy
import encodings.idna
import sys

from settings.general_functions import tv_show_ep_from_file_name, tv_show_ep_from_folder_structure, \
    initcap_file_name, rename_all_media_in_directory, get_media_title
from settings.mo_functions import get_downloads_or_media_path, save_paths_to_json
from components.checklist import CheckList


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
        self.title('Media Organizer')
        # self.iconbitmap('Images/organize_media.ico')

        self.colors = {
            'main': '#%02x%02x%02x' % (20, 20, 20),
            'sub': '#%02x%02x%02x' % (35, 35, 35),
            'special': '#%02x%02x%02x' % (92, 15, 128),
            'special_alt': '#%02x%02x%02x' % (180, 53, 240),
            'alt': '#%02x%02x%02x' % (60, 111, 194),
            'font': '#%02x%02x%02x' % (255, 255, 255)
        }

        font_default = 'Constantia'
        self.fonts = {
            'xxsmall': (font_default, 11, 'normal'),
            'xsmall': (font_default, 12, 'normal'),
            'small': (font_default, 13, 'normal'),
            'medium': (font_default, 14, 'normal'),
            'large': (font_default, 18, 'normal'),
            'xlarge': (font_default, 22, 'normal'),
            'xxlarge': (font_default, 40, 'normal'),
        }

        self.config(bg=self.colors['main'])

        with open('settings/config.json', 'r', encoding='utf-8') as config:
            self.configuration = json.load(config)
            self.media_extensions = self.configuration['media_extensions']

        self.on_startup()

        self.geometry(f'{int(self.winfo_screenwidth()*0.8)}x{int(self.winfo_screenheight()*0.8)}')
        self.configure(bg=self.colors['main'])
        ''' Filter media will contain a dictionary like:
            {path: {file_name: name, title: title, kind: kind, ...}}'''
        self.all_media_info = {}
        self.imdb_info = {}
        self.disable_buttons = False
        self.library = 'settings/library_cache.json'

        self.starting_width = self.winfo_width()
        self.starting_height = self.winfo_height()

        # Frames
        self.left_frame = Frame(self, bg=self.colors['main'])
        self.status_bar = Canvas(self, bg=self.colors['sub'], bd=0, highlightthickness=0,
                                 width=self.starting_width, height=0, relief=SUNKEN)
        self.status_bar.pack(side=BOTTOM, fill=X)
        self.left_frame.pack(side=LEFT, fill=Y, ipadx=14, ipady=14)

        self.middle_canvas = Canvas(self, bg=self.colors['sub'], bd=2, highlightthickness=0, relief=SUNKEN)
        self.canvas_frame = Frame(self.middle_canvas, bg=self.colors['sub'])
        self.bind('<Configure>', self.mid_canvas_dim)
        self.middle_canvas.create_window((0, 0), window=self.canvas_frame, anchor=NW)
        y_scroll_bar = Scrollbar(self, command=self.middle_canvas.yview, orient=VERTICAL)
        x_scroll_bar = Scrollbar(self, command=self.middle_canvas.xview, orient=HORIZONTAL)
        self.middle_canvas.config(yscrollcommand=y_scroll_bar.set, xscrollcommand=x_scroll_bar.set)
        y_scroll_bar.pack(side=RIGHT, fill=Y)
        x_scroll_bar.pack(side=BOTTOM, fill=X)
        self.middle_canvas.pack(side=LEFT, fill=BOTH, expand=True, ipadx=4)
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.image_config = {
            # Used by the buttons on the left of the main app
            'Locate Media': {'image': 'dir.png', 'image_size': (64, 64)},
            'Select Media': {'image': 'filter.png', 'image_size': (64, 64)},
            'Organize': {'image': 'organize_media.png', 'image_size': (64, 64)},
            # Used later by the filter window
            'deselect': {'image': 'deselect.png', 'image_size': (24, 24)},
            'select': {'image': 'select.png', 'image_size': (24, 24)},
            'arrow': {'image': 'arrow.png', 'image_size': (24, 24)}
        }
        for label_text, cfg in self.image_config.items():
            with Image.open(f'Images/{cfg["image"]}') as img:
                image = img.resize(self.image_config[label_text]['image_size'], Image.ANTIALIAS)
                self.image_config[label_text]['image_obj'] = ImageTk.PhotoImage(image)

        self.image_config = {k: v['image_obj'] for k, v in self.image_config.items()}

        note_text = 'If you have a Movies/TV Shows folder with a name other than "Movies" or "TV Shows",' \
                    ' in your media folder, you should rename them. Casing matters!\n\n' \
                    'If you do not have the folders, they will be created for you.'

        # Buttons
        self.buttons_config = {
            'Locate Media': {'command': self.locate_media,
                             'tooltip': 'Select your downloads folder and media folder; Your media folder will contain'
                                        ' your "Movies" and "TV Shows" folders'},
            'Select Media': {'command': self.on_press_select_media,
                             'tooltip': 'Gathers a list of media files from your downloads folder, and'
                                        ' allows you to filter which files to organize'},
            'Organize': {'command': self.on_press_organize_media,
                         'tooltip': f'Organize your media into Movies/TV Shows folders:\n\n{note_text}'}
        }
        # Create a button for each button in the config
        for label_text, cfg in self.buttons_config.items():
            # Put each button in a frame for padding purposes
            padding_frame = Frame(self.left_frame, bg=self.colors['main'])
            padding_frame.pack(side=TOP, padx=10, pady=10, fill=X)
            # Button
            button = Button(padding_frame, image=self.image_config[label_text], command=cfg['command'],
                            activebackground=self.colors['sub'], activeforeground=self.colors['font'],
                            bg=self.colors['main'], cursor="hand2", highlightthickness=0, bd=0, relief=FLAT,
                            anchor=CENTER)
            button.pack()
            self.buttons_config[label_text]['button'] = button
            # Button label
            label = Label(padding_frame, text=label_text, font=self.fonts['xsmall'],
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
                         font=self.fonts['xsmall'], thickness=45)

        w = self.winfo_width()
        self.progress_bar = Progressbar(self.status_bar, style=self.style, length=w-8)
        self.progress_bar.bind('<Configure>', self.on_window_adjust)
        # self.progress_bar.pack(side=BOTTOM)
        # self.status_bar.pack_forget()

        self.buttons_config['Organize']['button'].pack_forget()
        self.buttons_config['Organize']['label'].pack_forget()
        if 'downloads' not in self.configuration:
            self.buttons_config['Select Media']['button'].pack_forget()
            self.buttons_config['Select Media']['label'].pack_forget()

    def on_first_locate_media(self, widgets):
        save_paths_to_json()
        with open('settings/config.json', 'r', encoding='utf-8') as config:
            self.configuration = json.load(config)
        if 'downloads' in self.configuration:
            for w in widgets:
                w.destroy()

    def on_startup(self):
        if 'downloads' not in self.configuration:
            with Image.open(f'Images/dir.png') as img:
                img_o = img.resize((94, 94), Image.ANTIALIAS)
                img_o = ImageTk.PhotoImage(img_o)

            frame = Frame(self, bg=self.colors['main'])
            lbl1 = Label(frame, text='Sup,', bg=self.colors['main'], fg=self.colors['alt'],
                         font=self.fonts['xxlarge'])
            lbl2 = Label(frame, text='Start by locating your media', wraplength=450,
                         bg=self.colors['main'], fg='#%02x%02x%02x' % (180, 53, 240), font=self.fonts['xlarge'])
            b = Button(frame, image=img_o, bg=self.colors['main'], relief=RAISED, cursor='hand2')
            b.config(command=lambda x=(lbl1, frame, b): self.on_first_locate_media(x))

            frame.pack(ipadx=20)
            lbl1.pack(fill=X, pady=30)
            b.pack()
            lbl2.pack(fill=X, pady=30)

            self.wait_window(b)

    def on_window_adjust(self, event):
        """ Handles resizing progress bar, when the app is resized """
        w, h = self.winfo_width(), self.winfo_height()
        self.progress_bar.config(length=w-8)

    def mid_canvas_dim(self, event):
        """ Handles resizing of the 'Selected Media' portion of the app, when the app is resized """
        w, h = self.winfo_width(), self.starting_height
        self.middle_canvas.configure(scrollregion=self.middle_canvas.bbox("all"), width=w, height=h)

    def _on_mousewheel(self, event):
        x, y = self.winfo_pointerxy()
        canvas = self.winfo_containing(x, y)
        widget_path = str(canvas.master)
        if widget_path == '.' or widget_path.startswith('.!canvas2') or widget_path.startswith('.checklist'):
            self.middle_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def get_media_info_from_paths(self, paths):
        """ Gets all media information from media files in the given paths

        Output sample:
            '/USER/Downloads': {
                'TV Shows': {'House': {'Season 1': {'C:/USER/Downloads/house.s01e01.avi': House - S01E01'},
                                       'Season 2': {'C:/USER/Downloads/house.s02e01.avi': House - S02E01'}}}
                'Movies': {'C:/USER/Downloads/thor.avi': Thor'}
                }

        :param paths: A list of paths to media files
        :return: A dictionary of information about each file
        """

        def update_dict(dictionary):
            top_folder_dict = {}
            for file_path, i in dictionary.items():
                if i['top_folder_title']:
                    if i['top_folder_title'] not in top_folder_dict:
                        top_folder_dict[i['top_folder_title']] = {'title_list': [i['title']],
                                                                  'kind': i['kind'],
                                                                  'year': i['year']}
                    elif i['top_folder_title'] in top_folder_dict:
                        if i['title'] not in top_folder_dict[i['top_folder_title']]['title_list']:
                            top_folder_dict[i['top_folder_title']]['title_list'].append(i['title'])
                        if i['kind'] == 'TV Show':
                            top_folder_dict[i['top_folder_title']]['kind'] = i['kind']
                        if i['year']:
                            top_folder_dict[i['top_folder_title']]['year'] = i['year']

            for top_folder, info in top_folder_dict.items():
                top_folder_dict[top_folder]['num_unique_titles'] = len(info['title_list'])
            for file_path, i in dictionary.items():
                if i['top_folder_title']:
                    dictionary[file_path]['kind'] = top_folder_dict[i['top_folder_title']]['kind']
                    dictionary[file_path]['year'] = top_folder_dict[i['top_folder_title']]['year']
                    if not dictionary[file_path]['season'] \
                            and dictionary[file_path]['kind'] == 'TV Show':
                        dictionary[file_path]['season'] = -1
                        dictionary[file_path]['renamed_file_name'] = initcap_file_name(os.path.basename(file_path)
                                                                                       ).split('.')[0]
                    if top_folder_dict[i['top_folder_title']]['num_unique_titles'] > 1:
                        dictionary[file_path]['title'] = i['top_folder_title']
            del top_folder_dict

        def extract_info():
            file_info = {}
            for folder_path in paths:
                file_info[folder_path] = {}
                for path, folders, files in sorted(os.walk(folder_path)):
                    for file in sorted(files):
                        file_path = os.path.join(path, file)
                        extension = file.split('.')[-1]
                        # If its a media file
                        if extension in self.media_extensions and os.path.isfile(file_path):
                            renamed_file = initcap_file_name(file)
                            file_folder_path = os.path.dirname(file_path)
                            bottom_folder = os.path.basename(file_folder_path)
                            # Split the file's path by the folder_path to get the folders inside of the main folder
                            if folder_path != file_folder_path:
                                split_path = [x for x in path.split(folder_path) if x]
                                # This is just making sure the string doesn't start with a slash
                                top_folder = split_path[-1] if split_path[-1][0] not in ['\\', '/'] \
                                    else split_path[-1][1:]
                                top_folder = top_folder.split('\\')[0].split('/')[0]
                                top_folder_title = str(get_media_title(None,
                                                                       initcap_file_name(top_folder.replace('.', ' ')))
                                                       ).title()
                            else:
                                bottom_folder = None
                                top_folder_title = None

                            # Use the Season / Episode extracted based on the path,
                            # if it could not be extracted from the file name
                            tv_show_episode, season, episode = tv_show_ep_from_file_name(renamed_file)
                            s, e = tv_show_ep_from_folder_structure(file_path)
                            season = season or s
                            episode = episode or e

                            # Set the kind and season based on the season/episode extracted
                            if (season or season == 0) or (episode or episode == 0):
                                kind = 'TV Show'
                                # Assume it is the first season if there is no season extracted,
                                # but an episode was extracted, and there is a top folder
                                if not (season or season == 0) and (episode or episode == 0) and top_folder_title:
                                    season = 1
                                # If the folder containing the show has 'extras' in the name,
                                # then it is safe to assume that this is an extra episode
                                if 'extras' in str(bottom_folder).lower():
                                    season = -1  # Extras are identified as season -1
                                # Assume it is a movie if it extracted only an episode; i.e. Star Wars Episode 1
                                elif not (season or season == 0) and (episode or episode == 0) and not top_folder_title:
                                    kind = 'Movie'
                            else:
                                kind = 'Movie'

                            title = get_media_title(tv_show_episode, renamed_file)
                            years = re.findall(r'20\d\d|19\d\d', file)
                            year = int(years[0]) if years else None
                            title_w_year = f'{title} ({year})' if year else title

                            # Set the title for the Show/Movie based the show/season/episode info extracted
                            if kind == 'TV Show':
                                if (season or season == 0) and season != -1 and (episode or episode == 0):
                                    e_str = ''
                                    episode = episode if isinstance(episode, list) else [episode]
                                    for e in episode:
                                        e_str += f'E{"0" + str(e) if e < 10 else e}'
                                    title = top_folder_title if top_folder_title else title
                                    renamed_file_name = f'{title} - ' \
                                                        f'S{"0" + str(season) if season < 10 else season}' + e_str
                                else:
                                    renamed_file_name = renamed_file.split('.')[0]
                            else:
                                renamed_file_name = title_w_year

                            file_info[folder_path][file_path] = {'kind': kind, 'year': year,
                                                                 'title': title_w_year, 'season': season,
                                                                 'top_folder_title': top_folder_title,
                                                                 'renamed_file': f'{renamed_file_name}.{extension}'}
                            self.progress_bar['value'] += 1
                            self.s.configure(style=self.style,
                                             text=f'Got info for {file}\nIn the {folder_path} directory\n')
                if not file_info[folder_path]:
                    del file_info[folder_path]

                update_dict(file_info[folder_path])
            return file_info

        def convert_dict(dictionary):
            converted_dict = {}
            for folder, file in dictionary.items():
                converted_dict[folder] = {'TV Shows': {}, 'Movies': {}}
                for file_path, i in file.items():
                    alias = i['renamed_file']
                    title = i['title']
                    season = 'Extras' if i['season'] == -1 else f"Season {i['season']}"
                    if i['kind'] == 'TV Show':
                        if title not in converted_dict[folder]['TV Shows']:
                            converted_dict[folder]['TV Shows'][title] = {season: {file_path: alias}}
                        elif season not in converted_dict[folder]['TV Shows'][title]:
                            converted_dict[folder]['TV Shows'][title][season] = {file_path: alias}
                        elif file_path not in converted_dict[folder]['TV Shows'][title][season]:
                            converted_dict[folder]['TV Shows'][title][season][file_path] = alias
                    if i['kind'] == 'Movie':
                        converted_dict[folder]['Movies'][file_path] = alias
            return converted_dict

        def remove_empty_items(dictionary, new_dict):
            for key, value in dictionary.items():
                if value and isinstance(value, dict):
                    new_dict[key] = {}
                    remove_empty_items(dictionary[key], new_dict[key])
                elif value:
                    new_dict[key] = value

        self.progress_bar_appear()
        self.progress_bar['maximum'] = len([file for path in paths
                                            for x, y, files in os.walk(path)
                                            for file in files
                                            if file.split('.')[-1] in self.media_extensions])
        self.progress_bar['value'] = 0
        self.s.configure(style=self.style, text='Getting media info...')
        # Gets info from media files
        file_info = extract_info()
        # Converts the dictionary to be compatible with checklist
        file_info = convert_dict(file_info)
        file_info_new = {}
        remove_empty_items(file_info, file_info_new)
        self.progress_complete('Gathered Media!')
        return file_info_new

    def media_files_info(self, folder_paths=[]):
        """ Gets information about each media file in a path, from IMDb.

        :param folder_paths: The path to your media files
        :return: A dictionary of information about each file
        """
        self.all_media_info = self.get_media_info_from_paths(folder_paths)

        if not self.all_media_info:
            self.progress_bar_appear()
            self.progress_complete('\nNo Media Detected...\n')
            return 'No Media'

        else:
            checklist = CheckList(self.canvas_frame, dictionary=self.all_media_info, font=self.fonts['large'],
                                  toggle_config=self.image_config, toggle_type='image',
                                  bg=self.colors['main'], fg=self.colors['font'],
                                  highlight_color=self.colors['sub'], border_color=self.colors['special'])

    def recursively_organize_shows_and_movies(self, delete_folders=True):

        def inc_max_progress(d):
            """ Helper callback function to increment the max progress bar value for each file """
            for k, v in d.items():
                if not isinstance(v, dict):
                    self.progress_bar['maximum'] += 1
                else:
                    inc_max_progress(d[k])

        def move_files(d, path=[], level=0):
            """ Callback function to moves the files """
            level += 1
            for k, v in d.items():
                if not isinstance(v, dict):
                    skip = False
                    output_path = os.path.join(media_path, *path)
                    if not os.path.exists(output_path):
                        os.makedirs(output_path)
                    move_path = os.path.join(output_path, os.path.basename(k))
                    rename_path = os.path.join(output_path, v)
                    if not os.path.exists(move_path) and not os.path.exists(rename_path):
                        # Move to the new location
                        shutil.move(k, move_path)
                        # Then rename the file
                        os.rename(move_path, rename_path)
                        status_message = f'Moved & Renamed:\nFrom: {k}\nTo: {rename_path}'
                    elif os.path.exists(move_path) and not os.path.exists(rename_path):
                        # Then rename the file
                        os.rename(move_path, rename_path)
                        status_message = f'Renamed:\nFrom: {k}\nTo: {rename_path}'
                    else:
                        skip = True
                        status_message = f'Skipping: {k}\nFile exists {rename_path}'

                    self.progress_bar['value'] += 1
                    self.s.configure(style=self.style, text=status_message)

                    # Add the moved file's folder path to the list of folders to delete
                    if k != dl_path and k != media_path and k != output_path and not skip \
                            and os.path.dirname(k) not in folders_to_delete:
                        folders_to_delete.append(os.path.dirname(k))
                else:
                    if len(path) >= level:
                        path = path[:level-1]
                    path.append(k)
                    move_files(d[k], path=path, level=level)

        dl_path = get_downloads_or_media_path('downloads')
        media_path = get_downloads_or_media_path('media')
        folders_to_delete = []
        self.progress_bar['maximum'] = 0
        self.progress_bar['value'] = 0
        inc_max_progress(self.all_media_info)
        self.progress_bar_appear()

        for folder_path, i in self.all_media_info.items():
            move_files(i)

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
                if widget['todo'] not in self.final_todo_list:
                    self.final_todo_list.append(widget['todo'])
                    widget['button']['bg'] = self.colors['alt']
            else:
                if widget['todo'] in self.final_todo_list:
                    self.final_todo_list.remove(widget['todo'])
                    widget['button']['bg'] = self.colors['main']

        def on_submit():
            self.toggle_buttons_enabled()
            submit_button.destroy()
            main_frame.destroy()

        main_frame = Frame(self.canvas_frame, bg=self.colors['main'], bd=1, relief=RAISED)
        main_frame.pack(padx=8, pady=90)
        self.toggle_buttons_enabled()

        self.final_todo_list = []

        todo_list = {
            'downloads': 'Downloads',
            'media': 'Movies and TV Shows'
        }
        Label(main_frame, text='Which folders would you like to organize?', font=self.fonts['medium'],
              bg=self.colors['main'], fg=self.colors['font']).pack(side=TOP, fill=X, ipady=20, ipadx=20)

        options_frame = Frame(main_frame, bg=self.colors['main'], bd=2, relief=SUNKEN)
        options_frame.pack(side=TOP)

        dictionary = dict()
        for i, desc in todo_list.items():
            dictionary[i] = {'button': Checkbutton(options_frame, text=desc, onvalue=True, offvalue=False,
                                                   font=self.fonts['xsmall'],
                                                   anchor=NW, bg=self.colors['alt'], fg=self.colors['font'],
                                                   selectcolor=self.colors['main'])}
            dictionary[i]['button'].var = BooleanVar(value=True)
            self.final_todo_list.append(i)
            dictionary[i]['button']['variable'] = dictionary[i]['button'].var
            dictionary[i]['button']['command'] = lambda w=dictionary[i]: upon_select(w)
            dictionary[i]['button'].pack(side=TOP, fill=X, padx=1, pady=1)
            dictionary[i]['todo'] = i
        submit_button = Button(main_frame, text='Select', command=on_submit, font=self.fonts['small'],
                               bg=self.colors['special'], fg=self.colors['font'])
        submit_button.pack(side=BOTTOM, pady=20)
        self.wait_window(main_frame)
        return self.final_todo_list

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
        # Reset Selected Media
        for item in self.canvas_frame.children.values():
            item.pack_forget()

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

            outcome = self.media_files_info(folder_paths=paths)
            if outcome != 'No Media':
                self.organize_button_appear()
            else:
                self.organize_button_disappear()

    def on_press_organize_media(self):
        """ Start organizing media """
        tl = threading.Thread(target=self.recursively_organize_shows_and_movies)
        tl.start()

    def organize_button_appear(self):
        self.buttons_config['Organize']['button'].pack()
        self.buttons_config['Organize']['label'].pack(fill=X)

    def organize_button_disappear(self):
        self.buttons_config['Organize']['button'].pack_forget()
        self.buttons_config['Organize']['label'].pack_forget()

    def progress_bar_appear(self):
        self.toggle_buttons_enabled()
        self.progress_bar.pack(side=BOTTOM)
        w = self.winfo_width()
        self.progress_bar.config(length=w-8)
        self.progress_bar['value'] = 0
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
        with open('settings/config.json', 'r', encoding='utf-8') as config:
            self.configuration = json.load(config)
        if "downloads" in self.configuration:
            self.buttons_config['Select Media']['button'].pack()
            self.buttons_config['Select Media']['label'].pack()


app = Organize()
app.mainloop()
