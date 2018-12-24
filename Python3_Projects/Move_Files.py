"""
This is a program that will move, all files created in the last weeks, from one folder to another folder.
"""

import os
import datetime
import shutil
import tkinter.filedialog as ttk


def move_new_files(current_path, new_path, days_old):
    """ Moves files from one folder to another based on how many days it has been since it was last modified.

    :param current_path: Path of the file to be moved
    :param new_path: Path of the output folder
    :param days_old: Number of days since last modified
    :return: None
    """
    oldest_date = datetime.date.today() - datetime.timedelta(days=days_old)

    for file in os.listdir(current_path):
        time_stamp = os.path.getctime(current_path+file)
        file_modified_date = datetime.date.fromtimestamp(time_stamp)

        if file_modified_date >= oldest_date:
            shutil.move(current_path+file, new_path+file)

    return None


# Set it up so that it won't ask for the folder locations every time the file is run; Only the first time.
try:
    # If the locations are already saved to a file, open that file
    saves = open('saved_locations.txt', 'r')
except FileNotFoundError:
    # If the locations are not saved, ask for the locations and save them to a file
    saved_locations = open('saved_locations.txt', 'w')

    path = ttk.askdirectory(title='Path of files')+'/'
    the_new_path = ttk.askdirectory(title='Move the files here!')+'/'

    saved_locations.write(path)
    saved_locations.write('\n'+the_new_path)
    saved_locations.close()
    # Now open that file
    saves = open('saved_locations.txt', 'r')
finally:

    # Move new files from one location to another
    new_files_path, move_new_files_path = saves.read().split('\n')
    move_new_files(new_files_path, move_new_files_path, 7)
    saves.close()
