import re
import os
import json
from datetime import date


with open('settings/config.json', 'r') as config:
    configuration = json.load(config)
    media_extensions = configuration['media_extensions']


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
    patterns = [r'[sS]\d{1,2}[eE]\d{1,2}',  # s1e1 or s01e01
                r'\d{1,2}[xX]\d{1,2}',  # 1x01 or 10x01
                r'[._\- ](\d{3,4})[._\- ]'  # 101 or 1001
                ]
    current_year = date.today().year
    for pattern in patterns:
        matches = re.findall(pattern, file)
        # If the pattern returns matches
        if matches:
            if patterns.index(pattern) != 2:
                tv_show_episode = matches[0]
                season = int(re.findall(r'\d+', tv_show_episode)[0])
                episode = int(re.findall(r'\d+', tv_show_episode)[-1])
            else:
                matches = [num for num in matches
                           if int(num[-2:]) < 30 and num not in bad_nums
                           and (int(num) < current_year-30 or int(num) > current_year)]
                if matches:
                    tv_show_episode = matches[0]
                    season = int(tv_show_episode[:-2])
                    episode = int(tv_show_episode[-2:])
            continue

    return tv_show_episode, season, episode


def rename_all_media_in_directory(media_path, media_extensions=media_extensions):
    """ Renames all of the media files in the path

    :param media_path: Path to the files to rename
    :param media_extensions: A list of acceptable media extentions
    :return: None
    """
    for path, folders, files in os.walk(media_path):
        for file in files:
            file_path = os.path.join(path, file)
            tv_show_episode, season = tv_show_ep(file)
            renamed_file = initcap_file_name(file)
            # If it is a media file
            if file.split('.')[-1] in media_extensions and os.path.isfile(file_path):
                # If it's a TV show episode
                if tv_show_episode != []:
                    # Remove extract crap after the episode in name -- i.e. family.guy.s01e01.XXX420JUSTBLAZE.crap.mp4
                    renamed_file = renamed_file.split(tv_show_episode)[0] + tv_show_episode + '.' + renamed_file.split('.')[-1]
                os.rename(file_path, os.path.join(path, renamed_file))
    return None

