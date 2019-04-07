import tkinter.filedialog as filedialog, json
from mo_settings import required_paths


def save_paths_to_json(json_file_name='settings', required_paths=required_paths):
    dictionary = {}
    for item in required_paths:
        path = filedialog.askdirectory(title=f'Path to {item} folder')
        dictionary[item] = path

    with open(f'settings/{json_file_name}.json', 'w') as saved_location:
        json.dump(dictionary, saved_location)


def get_downloads_or_media_path(path='downloads'):
    try:
        # If the locations are already saved to a file, open that file
        saves = open('settings/settings.json', 'r')
    except FileNotFoundError:
        # If the locations are not saved, ask for the locations and save them to a  json file
        save_paths_to_json(json_file_name='settings', required_paths=required_paths)
        # Now open that file
        saves = open('settings/settings.json', 'r')
    finally:
        # Load json file
        paths_dict = json.load(saves)
        saves.close()

    return paths_dict[path]



