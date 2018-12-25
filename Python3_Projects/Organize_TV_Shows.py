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
            if os.path.exists(media_show_path):
                moved_file = os.path.join(media_show_path, file)
                shutil.move(file_path, moved_file)
                os.rename(moved_file, os.path.join(media_show_path, renamed_file))
            else:
                os.makedirs(media_show_path)
                moved_file = os.path.join(media_show_path, file)
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
    saves.close()
