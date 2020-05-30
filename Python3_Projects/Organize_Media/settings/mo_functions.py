import tkinter.filedialog as filedialog
import json


def save_paths_to_json():

    with open('settings/config.json', 'r') as c:
        config = json.load(c)
        required_paths = config['required_paths']

    for item in required_paths:
        path = filedialog.askdirectory(title=f'Path to {item.title()} folder')
        config[item] = path
        if not config[item]:
            del config[item]

    with open('settings/config.json', 'w') as n:
        json.dump(config, n, indent=2)

    return config


def get_downloads_or_media_path(path='downloads'):

    with open('settings/config.json', 'r') as c:
        config = json.load(c)
        if path not in config:
            # If the locations are not saved, ask for the locations and save them to a json file
            config = save_paths_to_json()

    return config[path]



