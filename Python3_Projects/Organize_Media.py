import tkinter.filedialog as ttk
import os
import shutil
import json
import re


def initcap_file_name(string):
    words = re.sub(r'[^a-zA-Z0-9()]', ' ', string).split(' ')
    extension = words[-1]
    string = ' '.join(words[:-1])
    new_string = string.title()
    new_string = '.'.join([new_string, extension])
    return new_string


def recursively_organize_shows_and_movies(dl_path, media_path, delete_folders=True):
    movies_folder = os.path.join(media_path, 'Movies')
    folders_in_main = [folders for path, folders, files in os.walk(dl_path) if path == dl_path][:][0]
    folders_to_delete = []
    for path, folders, files in os.walk(dl_path):
        if path == dl_path:
            # Moves Media files in the main folder
            for file in files:
                movies_file_path = os.path.join(movies_folder, file)
                current_file_path = os.path.join(path, file)
                tv_show_episode = re.findall(r'[sS]\d+[eE]\d+', initcap_file_name(file))
                # Route for TV Shows
                if tv_show_episode != [] and file.split('.')[-1] in media_extentions and os.path.isfile(current_file_path):
                    season = int(re.sub(r'[^0-9]', '', tv_show_episode[0].lower().split('e')[0]))
                    show_folder = os.path.join(media_path, 'TV Shows', initcap_file_name(file).split(' ' + tv_show_episode[0])[0], 'Season ' + str(season))
                    show_file_path = os.path.join(show_folder, file)
                    renamed_file = initcap_file_name(file)
                    renamed_file = renamed_file.split(tv_show_episode[0])[0]+tv_show_episode[0]+'.'+renamed_file.split('.')[-1]
                    if os.path.exists(show_folder):
                        shutil.move(current_file_path, show_file_path)
                        os.rename(show_file_path, os.path.join(show_folder, renamed_file))
                    else:
                        os.makedirs(show_folder)
                        shutil.move(current_file_path, show_file_path)
                        os.rename(show_file_path, os.path.join(show_folder, renamed_file))
                # Route for Movies
                elif file.split('.')[-1] in media_extentions and os.path.isfile(current_file_path):
                    if os.path.exists(movies_folder):
                        shutil.move(current_file_path, movies_file_path)
                        os.rename(movies_file_path, os.path.join(movies_folder, initcap_file_name(file)))
                    else:
                        os.makedirs(movies_folder)
                        shutil.move(current_file_path, movies_file_path)
                        os.rename(movies_file_path, os.path.join(movies_folder, initcap_file_name(file)))
        else:
            # Moves Media files NOT in the main folder
            for file in files:
                movies_file_path = os.path.join(movies_folder, file)
                current_file_path = os.path.join(path, file)
                tv_show_episode = re.findall(r'[sS]\d+[eE]\d+', initcap_file_name(file))
                # Route for TV Shows
                if tv_show_episode != [] and file.split('.')[-1] in media_extentions and os.path.isfile(current_file_path):
                    season = int(re.sub(r'[^0-9]', '', tv_show_episode[0].lower().split('e')[0]))
                    show_folder = os.path.join(media_path, 'TV Shows', initcap_file_name(file).split(' ' + tv_show_episode[0])[0], 'Season ' + str(season))
                    show_file_path = os.path.join(show_folder, file)
                    renamed_file = initcap_file_name(file)
                    renamed_file = renamed_file.split(tv_show_episode[0])[0]+tv_show_episode[0]+'.'+renamed_file.split('.')[-1]
                    if path not in folders_to_delete:
                        folders_to_delete.append(path)

                    if os.path.exists(show_folder):
                        shutil.move(current_file_path, show_file_path)
                        os.rename(show_file_path, os.path.join(show_folder, renamed_file))
                    else:
                        os.makedirs(show_folder)
                        shutil.move(current_file_path, show_file_path)
                        os.rename(show_file_path, os.path.join(show_folder, renamed_file))
                # Route for Movies
                elif file.split('.')[-1] in media_extentions and os.path.isfile(current_file_path):
                    if path not in folders_to_delete:
                        folders_to_delete.append(path)

                    if os.path.exists(movies_folder):
                        shutil.move(current_file_path, movies_file_path)
                        os.rename(movies_file_path, os.path.join(movies_folder, initcap_file_name(file)))
                    else:
                        os.makedirs(movies_folder)
                        shutil.move(current_file_path, movies_file_path)
                        os.rename(movies_file_path, os.path.join(movies_folder, initcap_file_name(file)))
    # Delete folders that contained media files that were moved
    if delete_folders:
        for f in folders_in_main:
            for folder in folders_to_delete:
                if f in folder:
                    if os.path.exists(os.path.join(dl_path, f)):
                        shutil.rmtree(os.path.join(dl_path, f))
    return None


media_extentions = ['mp4', 'mkv', 'avi', 'flv', 'wmv', 'webm', 'm4p', 'mov', 'm4v', 'mpg']

try:
    # If the locations are already saved to a file, open that file
    saves = open('path_saves.json', 'r')
except FileNotFoundError:
    # If the locations are not saved, ask for the locations and save them to a file
    saved_locations = open('path_saves.json', 'w')

    download_path = ttk.askdirectory(title='Path to Download folder')
    media_path = ttk.askdirectory(title='Path to Media folder')
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
    recursively_organize_shows_and_movies(dl_path, m_path, delete_folders=True)
    saves.close()
