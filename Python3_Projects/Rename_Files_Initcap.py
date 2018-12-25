import tkinter.filedialog as ttk
import re
import os


def initcap_file_name(string):
    words = re.sub(r'[^a-zA-Z0-9()]', ' ', string).split(' ')
    extension = words[-1]
    string = ' '.join(words[:-1])
    new_string = string.title()
    new_string = '.'.join([new_string, extension])
    return new_string


def initcap_folder_name(string):
    new_string = re.sub(r'[^a-zA-Z0-9()]', ' ', string).title()
    return new_string


def rename_file_names(path):
    for file in os.listdir(path):
        is_a_file = os.path.isfile(os.path.join(path, file))
        # print(is_a_file)
        if is_a_file:
            new_name = initcap_file_name(file)
            os.rename(os.path.join(path, file), os.path.join(path, new_name))
        else:
            print(file)
            new_name = initcap_folder_name(file)
            print(new_name)
            os.rename(os.path.join(path, file), os.path.join(path, new_name))
            subpath = os.path.join(path, new_name)
            for subfile in os.listdir(subpath):
                new_subname = initcap_file_name(subfile)
                os.rename(os.path.join(subpath, subfile), os.path.join(subpath, new_subname))


try:
    # If the locations are already saved to a file, open that file
    saves = open('saved_rename_path.txt', 'r')
except FileNotFoundError:
    # If the locations are not saved, ask for the locations and save them to a file
    saved_locations = open('saved_rename_path.txt', 'w')

    path = ttk.askdirectory(title='Path of files')

    saved_locations.write(path)
    saved_locations.close()
    # Now open that file
    saves = open('saved_rename_path.txt', 'r')
finally:
    # Move new files from one location to another
    the_path = saves.read()
    rename_file_names(the_path)
    saves.close()
