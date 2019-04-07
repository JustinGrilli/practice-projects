import re, os
from mo_settings import media_extensions


def initcap_file_name(string):
    words = re.sub(r'[^a-zA-Z0-9()]', ' ', string).split(' ')
    extension = words[-1]
    string = ' '.join(words[:-1])
    new_string = string.title()
    new_string = re.sub(r' +', ' ', new_string)
    new_string = '.'.join([new_string, extension])
    return new_string


def tv_show_ep(file):
    """ Finds the pattern of the TV Show and number for the season based on the pattern.

    :param file: The file name to extract the tv show episode pattern and season from.
    :return: The tv show pattern and tv show season number.
    """
    bad_nums = ['360', '480', '720', '1080', '264']
    season = []
    # if the tv show has a pattern like s01e01
    tv_show_episode = re.findall(r'[sS]\d+[eE]\d+', initcap_file_name(file))
    if tv_show_episode != []:
        tv_show_episode = tv_show_episode[0]
        season = int(re.sub(r'[^0-9]', '', tv_show_episode.lower().split('e')[0]))
    else:
        # if the tv show has a pattern like 1x01
        tv_show_episode = re.findall(r'\d+[xX]\d+', initcap_file_name(file))
        if tv_show_episode != []:
            tv_show_episode = tv_show_episode[0]
            season = int(re.sub(r'[^0-9]', '', tv_show_episode.lower().split('x')[0]))
        else:
            # if the tv show has a pattern like 101
            numbers = re.findall(r'\d+', initcap_file_name(file))
            for num in numbers:
                if (len(num) == 3 and num not in bad_nums) or \
                        (len(num) == 4 and num[:2] != '20' and int(num[-2:]) < 30 and num not in bad_nums):
                    tv_show_episode.append(num)
            if tv_show_episode != []:
                tv_show_episode = tv_show_episode[0]
                season = int(re.sub(r'[^0-9]', '', tv_show_episode[:-2]))

    return tv_show_episode, season


def rename_all_media_in_directory(media_path, media_extensions=media_extensions):
    for path, folders, files in os.walk(media_path):
        for file in files:
            file_path = os.path.join(path, file)
            tv_show_episode, season = tv_show_ep(file)
            if tv_show_episode != [] and file.split('.')[-1] in media_extensions and os.path.isfile(file_path):
                renamed_file = initcap_file_name(file)
                renamed_file = renamed_file.split(tv_show_episode)[0] + tv_show_episode + '.' + renamed_file.split('.')[-1]
                os.rename(file_path, os.path.join(path, renamed_file))
            elif file.split('.')[-1] in media_extensions and os.path.isfile(file_path):
                os.rename(file_path, os.path.join(path, initcap_file_name(file)))

