import tkinter.filedialog as filedialog
import json
import os


with open('settings/config.json', 'r') as config:
    configuration = json.load(config)
    required_paths = configuration['required_paths']


def save_paths_to_json(json_file_name='settings', required_paths=required_paths):
    dictionary = {}
    for item in required_paths:
        path = filedialog.askdirectory(title=f'Path to {item} folder')
        dictionary[item] = path

    with open(f'settings/{json_file_name}.json', 'w') as saved_location:
        json.dump(dictionary, saved_location)


def get_downloads_or_media_path(path='downloads'):
    if not os.path.exists('settings/settings.json'):
        # If the locations are not saved, ask for the locations and save them to a json file
        save_paths_to_json(json_file_name='settings', required_paths=required_paths)

    # Load json file
    saves = open('settings/settings.json', 'r')
    paths_dict = json.load(saves)
    saves.close()

    return paths_dict[path]



