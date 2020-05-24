import os
import shutil

og_path = 'C:\\Users\\HOVER\\Documents\\MEDIA_TEST\\backup'
og_file = 'warehouse.13.s01e01.avi'
copy_file = 'warehouse.13.s01e%s.avi'
eps = 12
og_file_path = os.path.join(og_path, og_file)
for x in range(2, eps+1):
    inc = f'0{x}' if x < 10 else str(x)
    shutil.copy(og_file_path, os.path.join(og_path, copy_file % inc))