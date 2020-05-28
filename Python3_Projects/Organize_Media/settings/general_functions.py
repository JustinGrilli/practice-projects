import re
import os
from datetime import date


def initcap_file_name(string):
    words = re.sub(r'[^a-zA-Z0-9()]', ' ', string).split(' ')
    extension = words[-1]
    string = ' '.join(words[:-1])
    new_string = string.title()
    new_string = re.sub(r' +', ' ', new_string)
    new_string = '.'.join([new_string, extension])
    return new_string


def tv_show_ep(file):
    """ Finds the pattern of the TV Show, and number for the season and episode based on the pattern.

    :param file: The file name to extract the tv show episode pattern and season from.
    :return: The tv show pattern, tv show season number, and episode number.
    """
    bad_nums = ['360', '480', '720', '1080', '264']
    tv_show_episode = []
    season = []
    episode = []
    # if the tv show has a pattern like...
    patterns = [r's\d{1,2}e\d{1,2}',  # s1e1 or s01e01
                r'\d{1,2}x\d{1,2}',  # 1x01 or 10x01
                # Season 1 Episode 1 or Season 01 Episode 01
                r'(season[^\w\d]\d{1,2}[^\w\d]episode[^\w\d]\d{1,2})[^\d]?',
                r'[^\w\d]*(\d{3,4})[^\w\d]*'  # 101 or 1001
                ]
    current_year = date.today().year
    for pattern in patterns:
        matches = re.findall(pattern, file, re.IGNORECASE)
        # If the pattern returns matches
        if matches:
            if patterns.index(pattern) != 3:
                tv_show_episode = matches[0]
                season, episode = [int(x) for x in re.findall(r'\d+', tv_show_episode)]
                return tv_show_episode, season, episode
            else:
                matches = [num for num in matches
                           if int(num[-2:]) < 30 and num not in bad_nums
                           and (int(num) < current_year-30 or int(num) > current_year)]
                if matches:
                    tv_show_episode = matches[0]
                    season = int(tv_show_episode[:-2])
                    episode = int(tv_show_episode[-2:])
                    return tv_show_episode, season, episode

    return tv_show_episode, season, episode


def rename_all_media_in_directory(media_info):
    """ Renames all of the media files in the path

    :param media_info: Dict of all files to rename
    :return: None
    """
    for file, info in media_info.items():
        file_folder = os.path.dirname(info['path'])
        renamed_file_path = os.path.join(file_folder, info['file_name'] + file.split('.')[-1])
        if not os.path.exists(renamed_file_path):
            os.rename(info['path'], renamed_file_path)
    return None

