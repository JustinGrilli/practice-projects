import re
from Python3_Projects.Organize_Media.functionality.general_functions import initcap_file_name

clean_file_name = 'x-factor (1999)'
clean_file_name = initcap_file_name(clean_file_name)
print(clean_file_name)
title = re.findall(r'^('
                   r'[a-z:\- ]+[0-9]?$|'
                   r'[a-z:\- ]+[0-9]?[^\d]\([a-z]+\)$|'
                   r'[a-z:\- ]+[0-9]?[^\d]\([a-z]+\)[^\d]|'
                   r'[a-z:\- ]+[0-9]?[^\d]|[0-9]+[^\w\d]?'
                   r')', clean_file_name, re.IGNORECASE)
print(title)
