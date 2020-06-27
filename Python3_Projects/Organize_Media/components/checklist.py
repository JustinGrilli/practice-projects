from tkinter import *
from copy import deepcopy
from PIL import Image, ImageTk

from collapsible_frame import CollapsibleFrame


class CheckList(Frame):
    """ Creates a series of checklists based on a dictionary.
        Assumes the lowest level of the dictionary is the checklist.

    Dictionary Sample:
    {
        'column': {
            'section':
                sub_section: {
                    'checklist_name': 'alias_name'
                }
            }
        }
    }

    Sample output:
        Column1                       |  Column2
            section1                  |      section1
                sub_section1          |          sub_section1
                    [x] checkbutton1  |             [x] checkbutton1
                    [x] checkbutton2  |             [x] checkbutton2
                sub_section2          |          sub_section2
                    [x] checkbutton1  |             [x] checkbutton1
                    [x] checkbutton2  |             [x] checkbutton2
            section2                  |      section2
                sub_section1          |          sub_section1
                    [x] checkbutton1  |             [x] checkbutton1


    :param dictionary: The dictionary of all the media to filter
    :return: Filtered media
    """

    def __init__(self, widget, dictionary, **kwargs):
        Frame.__init__(self)
        # self.config(bg=bg)
        self.bg = kwargs.pop('bg', None)
        self.fg = kwargs.pop('fg', None)
        self.highlight_color = kwargs.pop('highlight_color', None)
        self.border_color = kwargs.pop('border_color', None)
        self.section_color = kwargs.pop('section_color', None)
        self.column_font = kwargs.pop('column_font', ('none', 20, 'bold'))
        self.dictionary = dictionary
        self.filtered_dict = deepcopy(dictionary)

        self.image_config = {
            'deselect': {'image': 'deselect.png', 'image_size': (24, 24)},
            'select': {'image': 'select.png', 'image_size': (24, 24)},
            'arrow': {'image': 'arrow.png', 'image_size': (24, 24)}
        }
        for label_text, cfg in self.image_config.items():
            with Image.open(f'../Images/{cfg["image"]}') as img:
                image = img.resize(self.image_config[label_text]['image_size'], Image.ANTIALIAS)
                self.image_config[label_text]['image_obj'] = ImageTk.PhotoImage(image)

        main_frame = Frame(widget, bg=self.bg, name='checklist')
        main_frame.pack(fill=BOTH)
        self.construct_columns(main_frame, checklist_dict=self.dictionary)

    def add_to_dict(self, path, update_dict, source_dict):
        if len(path) == 1 or path[0] not in update_dict:
            update_dict[path[0]] = source_dict[path[0]]
        else:
            self.add_to_dict(path[1:], update_dict[path[0]], source_dict[path[0]])

    def remove_from_dict(self, path, update_dict):
        if len(path) == 1 and path[0] in update_dict:
            del update_dict[path[0]]
        elif path[0] in update_dict:
            self.remove_from_dict(path[1:], update_dict[path[0]])

    def upon_select(self, widget):
        # Add or remove items from list when they are toggled
        path = self.check_button_dict[widget]
        print(path)
        if widget.var.get():
            self.add_to_dict(path, self.filtered_dict, self.dictionary)
            widget['bg'] = self.highlight_color
        else:
            self.remove_from_dict(path, self.filtered_dict)
            widget['bg'] = self.bg

    def all_children(self, widget, callback):
        _list = widget.winfo_children()
        for w in _list:
            callback.append(w)
            self.all_children(w, callback)
        return callback

    def get_mapped_parent_objects(self, col_frame, button):

        def get_clean_path(objects):
            obs = dict()
            for obj in objects:
                fixed_path = []
                for w in str(obj).split('.'):
                    if w and w not in fixed_path:
                        fixed_path.append(w)
                obs[obj] = fixed_path
            return obs

        def map_obs_to_frame(obj_dict):
            mapping = dict()
            for obj, path in obj_dict['frame'].items():
                for o, p in obj_dict['button'].items():
                    for item in p:
                        if item not in path:
                            path.append(item)
                    if sorted(p) == sorted(path):
                        if obj not in mapping:
                            mapping[obj] = {o: p}
                        else:
                            mapping[obj][o] = p
            return mapping

        def replace_obj_path_with_indicator(mapping, button_path):
            for fobj, objs in mapping.items():
                for obj, path in objs.items():
                    for i in button_path:
                        if i not in path:
                            path.append(i)
                    objs[obj] = sorted(path) == sorted(button_path)
                mapping[fobj] = objs
            return mapping

        parent_callback = []
        parent_objects = [obj for obj in self.all_children(col_frame, parent_callback)
                          if type(obj) in (Frame, Button) and str(button).split('.') > str(obj).split('.')]

        objs = get_clean_path(parent_objects)
        obj_by_kind = {'button': {obj: l for obj, l in objs.items() if type(obj) == Button and obj['text'] == 'toggle'},
                       'frame': {obj: l for obj, l in objs.items() if type(obj) == Frame}}

        obj_mapping = map_obs_to_frame(obj_by_kind)

        b_path = []
        for w in str(button).split('.'):
            if w and w not in b_path:
                b_path.append(w)

        obj_mapping = replace_obj_path_with_indicator(obj_mapping, b_path)

        obj_mapping = {frame_obj: [obj for obj, same in objs.items() if same]
                       for frame_obj, objs in obj_mapping.items()}

        # Remove empty lists
        temp = {k: v for k, v in obj_mapping.items()}
        for obj, info in obj_mapping.items():
            if not info:
                del temp[obj]
        obj_mapping = temp

        return obj_mapping

    def toggle_all(self, x):
        col_frame, frame, button, parent_frames = x
        child_callback = []
        deselect_image = self.image_config['deselect']['image_obj']
        select_image = self.image_config['select']['image_obj']
        checklist_children = [obj for obj in self.all_children(frame, child_callback) if type(obj) == Checkbutton]
        button_children = [obj for obj in self.all_children(frame, child_callback)
                           if type(obj) == Button and obj['text'] == 'toggle']
        # Toggle each item in the dictionary based on the toggle
        toggle = str(button['image']) == str(select_image)
        for c in checklist_children:
            c.var = BooleanVar(value=toggle)
            c['variable'] = c.var
            self.upon_select(c)
        if toggle:
            button['image'] = deselect_image
            for b in button_children:
                b['image'] = deselect_image
        else:
            button['image'] = select_image
            for b in button_children:
                b['image'] = select_image

        print(parent_frames)
        for frame in parent_frames:
            child_callback = []
            off_check_button_children = []
            for obj in self.all_children(frame, child_callback):
                if type(obj) == Checkbutton and not obj.var.get() and obj not in off_check_button_children:
                    off_check_button_children.append(obj)

    def create_checklist_button(self, frame, name, font, dict_path):
        cbutton = Checkbutton(frame, text=name, fg=self.fg, onvalue=True,
                              offvalue=False, anchor=NW, bg=self.highlight_color,
                              font=font, selectcolor=self.bg)
        cbutton.var = BooleanVar(value=True)
        cbutton['variable'] = cbutton.var
        cbutton['command'] = lambda w=cbutton: self.upon_select(w)
        cbutton.pack(side=TOP, fill=X, anchor=NW, pady=1, padx=1)
        self.check_button_dict[cbutton] = dict_path

    def create_section_frame(self, frame, col_frame, **kwargs):
        """ Create the section frame for a given section """
        frames = kwargs.pop('frames', None)
        title = kwargs.pop('title', None)
        font = kwargs.pop('font', None)
        padx = kwargs.pop('padx', None)
        pady = kwargs.pop('pady', None)

        section_frame = Frame(frame, bg=self.bg, name=title.lower())
        section_frame.pack(side=TOP, fill=X, padx=padx, anchor=NW)
        if not frames:
            frames = [section_frame]

        f = CollapsibleFrame(section_frame, bg=self.bg, title=title, font=font)
        section_bottom_frame = Frame(f.collapse_frame, bd=2, bg=self.bg)
        toggle_button = Button(f.top_frame, image=self.image_config['deselect']['image_obj'], bg=self.bg, relief=FLAT)
        toggle_button['text'] = 'toggle'
        toggle_button['command'] = lambda x=(col_frame, section_bottom_frame, toggle_button, frames): self.toggle_all(x)
        toggle_button.pack(side=LEFT)

        section_bottom_frame.pack(side=TOP, fill=X, padx=padx, pady=pady, anchor=NW)

        return section_bottom_frame, section_frame

    def construct_sections(self, frame, font, outer_frame=None, column=None, section=None, checklist_dict=None,
                           path=None, frames=None, level=0):
        """ Constructs all sections for a given dictionary.
            Will continue creating sections until the value is not a dictionary. """

        # Use the level to keep track of how deep we are in the dictionary
        level += 1
        font = (font[0], font[1] - 2, font[2])
        for sub_section in sorted([k for k in checklist_dict[section].keys()]):
            # Adjust path for the section based on the level of the dictionary
            if len(path) >= level + 1:
                path = path[:level + 1]
                path.pop(level)
                frames = frames[:level]
                frames.pop(level-1)
            path.append(sub_section)
            frames.append(outer_frame)

            if isinstance(checklist_dict[section][sub_section], dict):
                section_frame, of = self.create_section_frame(frame, title=sub_section, font=font,
                                                              padx=(10, 0), col_frame=frame, frames=frames)
                self.construct_sections(frame=section_frame, outer_frame=of, frames=frames, font=font, column=column,
                                        section=sub_section, checklist_dict=checklist_dict[section],
                                        path=path, level=level)
            else:
                self.create_checklist_button(frame, name=checklist_dict[section][sub_section], font=font,
                                             dict_path=path)

    def construct_columns(self, frame, checklist_dict):
        """ Constructs the columns for the checklists.
            Assumes the first key in the dict is the column name """
        temp = deepcopy(checklist_dict)
        self.check_button_dict = dict()
        for column in sorted(list(temp.keys())):
            if isinstance(temp[column], dict):
                c_frame = Frame(frame)
                c_frame.pack(side=LEFT, anchor=NW)
                column_frame, outer_frame = self.create_section_frame(c_frame, title=column, font=self.column_font,
                                                                      col_frame=c_frame)
                self.construct_sections(frame=column_frame, outer_frame=outer_frame, frames=[outer_frame], font=self.column_font, column=column,
                                        section=column, checklist_dict=temp, path=[column])
            else:
                raise Exception(f'Not a proper dictionary. Expected {column} to have a dictionary.')


if __name__ == '__main__':
    dictionary = {
        'HEADER_1': {
            'Zheckbox_1': 'Zheck 1',
            'Section_1': {
                'Sub_Section_1': {
                    'Checkbox_1': 'Check 1'}},
            'Section_2': {
                'Sub_Section_1': {
                    'Checkbox_1': 'Check 1',
                    'Checkbox_2': 'Check 2'},
                'Sub_Section_2': {
                    'Checkbox_1': 'Check 1'}},
            'Section_3': {
                'Checkbox_1': 'Check 1'},
            'Checkbox_2': 'Check 2'},
        'HEADER_2': {
            'Section_1': {
                'Checkbox_1': 'Check 1'},
            'Checkbox_1': 'Check 1'},
        'HEADER_3': {
            'Checkbox_1': 'Check 1'}
    }
    app = Tk()
    checklist = CheckList(app, dictionary=dictionary,
                          bg='white', fg='black', highlight_color='light blue')
    checklist.pack()
    app.mainloop()
