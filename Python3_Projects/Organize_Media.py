import tkinter.filedialog as ttk
import os
import shutil
import json
import re


def flatten_tv_show_folders(download_path, delete_folders=True):
    for file in os.listdir(download_path):
        subpath = os.path.join(download_path, file)
        tv_show_folder = re.findall(r's\d+e\d+', file.lower())
        if tv_show_folder != [] and os.path.isdir(subpath):
            for subfile in os.listdir(subpath):
                tv_show_file = re.findall(r's\d+e\d+', subfile.lower())
                if tv_show_file != [] and os.path.isfile(os.path.join(subpath, subfile)) and subfile.split('.')[-1] in media_extentions:
                    shutil.move(os.path.join(subpath, subfile), os.path.join(download_path, subfile))
            if delete_folders:
                shutil.rmtree(subpath)
    return None


def organize_tv_shows(download_path, media_path):
    for file in os.listdir(download_path):
        file_path = os.path.join(download_path, file)
        renamed_file = initcap_file_name(file)
        tv_show_episode = re.findall(r'[sS]\d+[eE]\d+', renamed_file)
        if tv_show_episode != [] and os.path.isfile(file_path) and renamed_file.split('.')[-1] in media_extentions:
            renamed_file = renamed_file.split(tv_show_episode[0])[0]+tv_show_episode[0]+'.'+renamed_file.split('.')[-1]
            season = int(re.sub(r'[^0-9]', '', tv_show_episode[0].lower().split('e')[0]))
            media_show_path = os.path.join(media_path, 'TV Shows', renamed_file.split(' '+tv_show_episode[0])[0], 'Season '+str(season))
            moved_file = os.path.join(media_show_path, file)
            if os.path.exists(media_show_path):
                shutil.move(file_path, moved_file)
                os.rename(moved_file, os.path.join(media_show_path, renamed_file))
            else:
                os.makedirs(media_show_path)
                shutil.move(file_path, moved_file)
                os.rename(moved_file, os.path.join(media_show_path, renamed_file))
    return None


def initcap_file_name(string):
    words = re.sub(r'[^a-zA-Z0-9()]', ' ', string).split(' ')
    extension = words[-1]
    string = ' '.join(words[:-1])
    new_string = string.title()
    new_string = '.'.join([new_string, extension])
    return new_string


def recursively_organize_movies(dl_path, media_path, delete_folders=True):
    movies_folder = os.path.join(media_path, 'Movies')
    folders_in_main = [folders for path, folders, files in os.walk(dl_path) if path == dl_path][:][0]
    folders_to_delete = []
    for path, folders, files in os.walk(dl_path):
        if path == dl_path:
            # Moves Media files in the main folder
            for file in files:
                movies_file_path = os.path.join(movies_folder, file)
                current_file_path = os.path.join(path, file)
                if file.split('.')[-1] in media_extentions and os.path.isfile(current_file_path):
                    if os.path.exists(movies_folder):
                        shutil.move(current_file_path, movies_file_path)
                        os.rename(movies_file_path, os.path.join(movies_folder, initcap_file_name(file)))
                    else:
                        os.makedirs(movies_folder)
                        shutil.move(current_file_path, movies_file_path)
                        os.rename(movies_file_path, os.path.join(movies_folder, initcap_file_name(file)))
                    print('Moved File: ' + file)
        else:
            # Moves Media files NOT in the main folder
            for file in files:
                movies_file_path = os.path.join(movies_folder, file)
                current_file_path = os.path.join(path, file)
                if file.split('.')[-1] in media_extentions and os.path.isfile(current_file_path):
                    if path not in folders_to_delete:
                        folders_to_delete.append(path)

                    if os.path.exists(movies_folder):
                        shutil.move(current_file_path, movies_file_path)
                        os.rename(movies_file_path, os.path.join(movies_folder, initcap_file_name(file)))
                    else:
                        os.makedirs(movies_folder)
                        shutil.move(current_file_path, movies_file_path)
                        os.rename(movies_file_path, os.path.join(movies_folder, initcap_file_name(file)))
                    print('Moved File: ' + file)
    # Delete folders that contained media files that were moved
    if delete_folders:
        for f in folders_in_main:
            for folder in folders_to_delete:
                if f in folder:
                    shutil.rmtree(os.path.join(dl_path, f))
                    print('Deleted Folder: '+os.path.join(dl_path, f))
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
    flatten_tv_show_folders(dl_path, delete_folders=True)
    organize_tv_shows(dl_path, m_path)
    recursively_organize_movies(dl_path, m_path, delete_folders=True)
    saves.close()
