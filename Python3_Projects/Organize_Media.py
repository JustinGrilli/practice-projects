from tkinter import *
import tkinter.filedialog as filedialog
import os
import shutil
import json
import re
from tkinter.ttk import Progressbar, Style
from PIL import Image, ImageTk


class Organize(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.title('Media Organizer 9000')
        self.configure(bg='#222222')
        self.resizable(0, 0)

        self.media_extensions = ['mp4', 'mkv', 'avi', 'flv', 'wmv', 'webm', 'm4p', 'mov', 'm4v', 'mpg']
        colors = {
            'main': '#%02x%02x%02x' % (43, 53, 68),
            'sub': '#%02x%02x%02x' % (62, 77, 99),
            'special': '#%02x%02x%02x' % (153, 68, 12),
            'alt': 'white'
        }

        # Frames
        left_frame = Frame(self, bg=colors['main'])
        left_frame.pack(side=LEFT, expand=True, fill=BOTH)
        right_frame = Frame(self, bg=colors['main'])
        right_frame.pack(side=LEFT, expand=True, fill=BOTH)
        right_bottom_frame = Frame(right_frame, bg=colors['main'])
        right_bottom_frame.pack(side=BOTTOM, expand=True, fill=BOTH)

        # Images
        image_width, image_height = 35, 35
        dir_image = Image.open('Images/dir.png')
        dir_image = dir_image.resize((image_width, image_height), Image.ANTIALIAS)
        self.directory_image = ImageTk.PhotoImage(dir_image)

        # Buttons
        organize_button = Button(left_frame, text='Organize Media', command=self.organize_media, font='none 14 bold', fg='white', bg=colors['special'], width=14)
        organize_button.grid(row=0, column=0, sticky=NW, padx=1, pady=2)
        directory_button = Button(left_frame, image=self.directory_image, command=self.choose_directory, font='none 14 bold', fg='white', bg=colors['sub'])
        directory_button.grid(row=0, column=1, sticky=NW, padx=1, pady=2)
        rename_button = Button(left_frame, text='Rename Media', command=self.rename_media, font='none 14 bold', fg='white', bg=colors['sub'], width=14)
        rename_button.grid(row=1, column=0, sticky=NW, padx=1, pady=2)
        flatten_button = Button(left_frame, text='Flatten Movies', command=self.flatten_movie_files, font='none 14 bold', fg='white', bg=colors['sub'], width=14)
        flatten_button.grid(row=2, column=0, sticky=NW, padx=1, pady=2)
        note_label = Label(left_frame, text='- Note about Organize Media -', font='none 11 bold underline', fg='grey', bg=colors['main'], width=12, wraplength=220, justify=LEFT)
        note_label.grid(row=3, columnspan=2, sticky=N + S + E + W, pady=2)
        self.label_var = StringVar()
        self.label_var.set('If have a Movies/TV Shows folder with a name other than "Movies" or "TV Shows", in your media folder, you should rename them. Casing matters!\n\nIf you do not have the folders, they will be created for you.')
        note_label = Label(left_frame, textvariable=self.label_var, font='none 10 italic', fg='grey', bg=colors['main'], width=12, wraplength=220, justify=LEFT)
        note_label.grid(row=4, columnspan=2, sticky=N+S+E+W)

        self.progress_label_text = StringVar()
        self.progress_label_text.set('')
        progress_label = Label(right_frame, textvariable=self.progress_label_text, font='none 18 bold', fg='white', bg=colors['main'], justify=LEFT)
        progress_label.pack(side=TOP, expand=True, anchor=SW)
        self.close_button = Button(right_bottom_frame, text='Close', command=self.destroy, font='none 14 bold', fg='white', bg='darkgreen')
        self.s = Style()
        self.s.theme_use('classic')
        self.s.configure('blue.Horizontal.TProgressbar', troughcolor='#222222', background='darkgreen', thickness=25)
        self.progress_bar = Progressbar(right_frame, style='blue.Horizontal.TProgressbar', length=600)

    def initcap_file_name(self, string):
        words = re.sub(r'[^a-zA-Z0-9()]', ' ', string).split(' ')
        extension = words[-1]
        string = ' '.join(words[:-1])
        new_string = string.title()
        new_string = '.'.join([new_string, extension])
        return new_string


    def recursively_organize_shows_and_movies(self, dl_path, media_path, delete_folders=True):
        movies_folder = os.path.join(media_path, 'Movies')
        folders_in_main = [folders for path, folders, files in os.walk(dl_path) if path == dl_path][:][0]
        folders_to_delete = []
        total_count = 0
        progress_count = 0
        for path, folders, files in os.walk(dl_path):
            for file in files:
                current_file_path = os.path.join(path, file)
                if file.split('.')[-1] in self.media_extensions and os.path.isfile(current_file_path):
                    total_count += 1
        self.progress_bar['maximum'] = total_count
        self.progress_bar['value'] = progress_count
        for path, folders, files in os.walk(dl_path):
            if path == dl_path:
                # Moves Media files in the main folder
                for file in files:
                    movies_file_path = os.path.join(movies_folder, file)
                    current_file_path = os.path.join(path, file)
                    tv_show_episode = re.findall(r'[sS]\d+[eE]\d+', self.initcap_file_name(file))
                    # Route for TV Shows
                    if tv_show_episode != [] and file.split('.')[-1] in self.media_extensions and os.path.isfile(current_file_path):
                        season = int(re.sub(r'[^0-9]', '', tv_show_episode[0].lower().split('e')[0]))
                        show_folder = os.path.join(media_path, 'TV Shows', self.initcap_file_name(file).split(' ' + tv_show_episode[0])[0], 'Season ' + str(season))
                        show_file_path = os.path.join(show_folder, file)
                        renamed_file = self.initcap_file_name(file)
                        renamed_file = renamed_file.split(tv_show_episode[0])[0]+tv_show_episode[0]+'.'+renamed_file.split('.')[-1]
                        if os.path.exists(show_folder):
                            shutil.move(current_file_path, show_file_path)
                            os.rename(show_file_path, os.path.join(show_folder, renamed_file))
                            self.progress_label_text.set('Moved & Renamed Show:\nFrom: ' + file + '\nTo: ' + renamed_file)
                            progress_count += 1
                            self.progress_bar['value'] = progress_count
                        else:
                            os.makedirs(show_folder)
                            shutil.move(current_file_path, show_file_path)
                            os.rename(show_file_path, os.path.join(show_folder, renamed_file))
                            self.progress_label_text.set('Moved & Renamed Show:\nFrom: ' + file + '\nTo: ' + renamed_file)
                            progress_count += 1
                            self.progress_bar['value'] = progress_count
                    # Route for Movies
                    elif file.split('.')[-1] in self.media_extensions and os.path.isfile(current_file_path):
                        if os.path.exists(movies_folder):
                            shutil.move(current_file_path, movies_file_path)
                            os.rename(movies_file_path, os.path.join(movies_folder, self.initcap_file_name(file)))
                            self.progress_label_text.set('Moved & Renamed Movie:\nFrom: ' + file + '\nTo: ' + self.initcap_file_name(file))
                            progress_count += 1
                            self.progress_bar['value'] = progress_count
                        else:
                            os.makedirs(movies_folder)
                            shutil.move(current_file_path, movies_file_path)
                            os.rename(movies_file_path, os.path.join(movies_folder, self.initcap_file_name(file)))
                            self.progress_label_text.set('Moved & Renamed Movie:\nFrom: ' + file + '\nTo: ' + self.initcap_file_name(file))
                            progress_count += 1
                            self.progress_bar['value'] = progress_count
            else:
                # Moves Media files NOT in the main folder
                for file in files:
                    movies_file_path = os.path.join(movies_folder, file)
                    current_file_path = os.path.join(path, file)
                    tv_show_episode = re.findall(r'[sS]\d+[eE]\d+', self.initcap_file_name(file))
                    # Route for TV Shows
                    if tv_show_episode != [] and file.split('.')[-1] in self.media_extensions and os.path.isfile(current_file_path):
                        season = int(re.sub(r'[^0-9]', '', tv_show_episode[0].lower().split('e')[0]))
                        show_folder = os.path.join(media_path, 'TV Shows', self.initcap_file_name(file).split(' ' + tv_show_episode[0])[0], 'Season ' + str(season))
                        show_file_path = os.path.join(show_folder, file)
                        renamed_file = self.initcap_file_name(file)
                        renamed_file = renamed_file.split(tv_show_episode[0])[0]+tv_show_episode[0]+'.'+renamed_file.split('.')[-1]
                        if path not in folders_to_delete:
                            folders_to_delete.append(path)

                        if os.path.exists(show_folder):
                            shutil.move(current_file_path, show_file_path)
                            os.rename(show_file_path, os.path.join(show_folder, renamed_file))
                            self.progress_label_text.set('Moved & Renamed Show:\nFrom: ' + file + '\nTo: ' + renamed_file)
                            progress_count += 1
                            self.progress_bar['value'] = progress_count
                        else:
                            os.makedirs(show_folder)
                            shutil.move(current_file_path, show_file_path)
                            os.rename(show_file_path, os.path.join(show_folder, renamed_file))
                            self.progress_label_text.set('Moved & Renamed Show:\nFrom: ' + file + '\nTo: ' + renamed_file)
                            progress_count += 1
                            self.progress_bar['value'] = progress_count
                    # Route for Movies
                    elif file.split('.')[-1] in self.media_extensions and os.path.isfile(current_file_path):
                        if path not in folders_to_delete:
                            folders_to_delete.append(path)

                        if os.path.exists(movies_folder):
                            shutil.move(current_file_path, movies_file_path)
                            os.rename(movies_file_path, os.path.join(movies_folder, self.initcap_file_name(file)))
                            self.progress_label_text.set('Moved & Renamed Movie:\nFrom: ' + file + '\nTo: ' + self.initcap_file_name(file))
                            progress_count += 1
                            self.progress_bar['value'] = progress_count
                        else:
                            os.makedirs(movies_folder)
                            shutil.move(current_file_path, movies_file_path)
                            os.rename(movies_file_path, os.path.join(movies_folder, self.initcap_file_name(file)))
                            self.progress_label_text.set('Moved & Renamed Movie:\nFrom: ' + file + '\nTo: ' + self.initcap_file_name(file))
                            progress_count += 1
                            self.progress_bar['value'] = progress_count
        # Delete folders that contained media files that were moved
        if delete_folders:
            for f in folders_in_main:
                for folder in folders_to_delete:
                    if f in folder:
                        if os.path.exists(os.path.join(dl_path, f)):
                            shutil.rmtree(os.path.join(dl_path, f))
        return None

    def flatten_movies(self, media_path, delete_folders=True):
        movies_folder = os.path.join(media_path, 'Movies')
        folders_in_main = [folders for path, folders, files in os.walk(movies_folder) if path == movies_folder][:][0]
        folders_to_delete = []
        total_count = 0
        progress_count = 0
        for path, folders, files in os.walk(media_path):
            for file in files:
                current_file_path = os.path.join(path, file)
                if file.split('.')[-1] in self.media_extensions and os.path.isfile(current_file_path):
                    total_count += 1
        self.progress_bar['maximum'] = progress_count
        if os.path.exists(movies_folder):
            for path, folders, files in os.walk(movies_folder):
                if path != movies_folder:
                    # Moves Media files NOT in the main folder
                    for file in files:
                        movies_file_path = os.path.join(movies_folder, file)
                        current_file_path = os.path.join(path, file)
                        tv_show_episode = re.findall(r'[sS]\d+[eE]\d+', self.initcap_file_name(file))
                        # Route for TV Shows
                        if tv_show_episode == [] and file.split('.')[-1] in self.media_extensions and os.path.isfile(current_file_path):
                            if path not in folders_to_delete:
                                folders_to_delete.append(path)
                            shutil.move(current_file_path, movies_file_path)
                            os.rename(movies_file_path, os.path.join(movies_folder, self.initcap_file_name(file)))
                            progress_count += 1
                            self.progress_label_text.set('Moved:\n'+self.initcap_file_name(file))
                            self.progress_bar['value'] = progress_count
            # Delete folders that contained media files that were moved
            if delete_folders:
                for f in folders_in_main:
                    for folder in folders_to_delete:
                        if f in folder:
                            if os.path.exists(os.path.join(movies_folder, f)):
                                shutil.rmtree(os.path.join(movies_folder, f))
        return None

    def organize_media(self):
        try:
            # If the locations are already saved to a file, open that file
            saves = open('path_saves.json', 'r')
        except FileNotFoundError:
            # If the locations are not saved, ask for the locations and save them to a file
            saved_locations = open('path_saves.json', 'w')

            download_path = filedialog.askdirectory(title='Path to Download folder')
            media_path = filedialog.askdirectory(title='Path to Media folder')
            dictionary = '{"downloads": "'+download_path+'", "media": "'+media_path+'"}'
            saved_locations.write(dictionary)
            saved_locations.close()
            # Now open that file
            saves = open('path_saves.json', 'r')
        finally:
            # Move new files from one location to another
            paths = saves.read()
            dl_path = json.loads(paths)['downloads']
            m_path = json.loads(paths)['media']
            self.progress_bar_appear()
            self.recursively_organize_shows_and_movies(dl_path, m_path, delete_folders=True)
            saves.close()
            self.progress_complete()

    def choose_directory(self):
        download_path = filedialog.askdirectory(title='Path to Download folder')
        media_path = filedialog.askdirectory(title='Path to Media folder')
        saved_locations = open('path_saves.json', 'w')
        dictionary = '{"downloads": "' + download_path + '", "media": "' + media_path + '"}'
        saved_locations.write(dictionary)
        saved_locations.close()

    def rename_all_media(self, media_path):
        for path, folders, files in os.walk(media_path):
            for file in files:
                file_path = os.path.join(path, file)
                tv_show_episode = re.findall(r'[sS]\d+[eE]\d+', self.initcap_file_name(file))
                if tv_show_episode != [] and file.split('.')[-1] in self.media_extensions and os.path.isfile(file_path):
                    renamed_file = self.initcap_file_name(file)
                    renamed_file = renamed_file.split(tv_show_episode[0])[0] + tv_show_episode[0] + '.' + renamed_file.split('.')[-1]
                    os.rename(file_path, os.path.join(path, renamed_file))
                elif file.split('.')[-1] in self.media_extensions and os.path.isfile(file_path):
                    os.rename(file_path, os.path.join(path, self.initcap_file_name(file)))

    def rename_media(self):
        try:
            # If the locations are already saved to a file, open that file
            saves = open('path_saves.json', 'r')
        except FileNotFoundError:
            # If the locations are not saved, ask for the locations and save them to a file
            saved_locations = open('path_saves.json', 'w')

            download_path = filedialog.askdirectory(title='Path to Download folder')
            media_path = filedialog.askdirectory(title='Path to Media folder')
            dictionary = '{"downloads": "'+download_path+'", "media": "'+media_path+'"}'
            saved_locations.write(dictionary)
            saved_locations.close()
            # Now open that file
            saves = open('path_saves.json', 'r')
        finally:
            # Move new files from one location to another
            paths = saves.read()
            m_path = json.loads(paths)['media']
            self.rename_all_media(m_path)
            saves.close()

    def flatten_movie_files(self):
        try:
            # If the locations are already saved to a file, open that file
            saves = open('path_saves.json', 'r')
        except FileNotFoundError:
            # If the locations are not saved, ask for the locations and save them to a file
            saved_locations = open('path_saves.json', 'w')

            download_path = filedialog.askdirectory(title='Path to Download folder')
            media_path = filedialog.askdirectory(title='Path to Media folder')
            dictionary = '{"downloads": "'+download_path+'", "media": "'+media_path+'"}'
            saved_locations.write(dictionary)
            saved_locations.close()
            # Now open that file
            saves = open('path_saves.json', 'r')
        finally:
            # Move new files from one location to another
            paths = saves.read()
            self.progress_bar_appear()
            m_path = json.loads(paths)['media']
            self.flatten_movies(m_path)
            saves.close()
            self.progress_complete()

    def progress_bar_appear(self):
        self.progress_bar['value'] = 0
        self.progress_bar.pack(side=BOTTOM)
        self.progress_label_text.set('')
        self.close_button.pack_forget()

    def progress_complete(self):
        self.progress_label_text.set('Complete!')
        self.close_button.pack(side=RIGHT, fill=X, anchor=SE, pady=4)


app = Organize()
app.mainloop()
