from tkinter import *
from copy import deepcopy
from PIL import Image, ImageTk

from collapsible_frame import CollapsibleFrame


class CheckList(Frame):
    """ Creates a series of checklists based on a dictionary.
        The first level of Keys int the dictionary are a column (and the title of that column).
        Each level of the dictionary adds a sub-section.
        The lowest level of the dictionary is the checklist.

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

    def toggle_all(self, x):
        col_frame, frame, button, toggle_buttons = x
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
        print(toggle_buttons)
        # for frame in parent_frames:
        #     child_callback = []
        #     off_check_button_children = []
        #     for obj in self.all_children(frame, child_callback):
        #         if type(obj) == Checkbutton and not obj.var.get() and obj not in off_check_button_children:
        #             off_check_button_children.append(obj)

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
        title = kwargs.pop('title', None)
        font = kwargs.pop('font', None)
        padx = kwargs.pop('padx', None)
        pady = kwargs.pop('pady', None)
        toggle_buttons = kwargs.pop('toggle_buttons', [])

        section_frame = Frame(frame, bg=self.bg, name=title.lower())
        section_frame.pack(side=TOP, fill=X, padx=padx, anchor=NW)

        f = CollapsibleFrame(section_frame, bg=self.bg, title=title, font=font)
        section_bottom_frame = Frame(f.collapse_frame, bd=2, bg=self.bg)
        toggle_button = Button(f.top_frame, image=self.image_config['deselect']['image_obj'], bg=self.bg, relief=FLAT)
        toggle_button['text'] = 'toggle'
        toggle_buttons.append(toggle_button)
        toggle_button['command'] = lambda x=(col_frame, section_bottom_frame, toggle_button, toggle_buttons): self.toggle_all(x)
        toggle_button.pack(side=LEFT)

        section_bottom_frame.pack(side=TOP, fill=X, padx=padx, pady=pady, anchor=NW)

        return section_bottom_frame

    def construct_sections(self, frame, font, column=None, section=None, checklist_dict=None,
                           path=None, level=0, toggle_buttons=None):
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
                toggle_buttons = toggle_buttons[:level + 1]
                toggle_buttons.pop(level)
            path.append(sub_section)

            if isinstance(checklist_dict[section][sub_section], dict):
                section_frame = self.create_section_frame(frame, title=sub_section, font=font, padx=(10, 0),
                                                          col_frame=frame, toggle_buttons=toggle_buttons)
                self.construct_sections(frame=section_frame, font=font, column=column,
                                        section=sub_section, checklist_dict=checklist_dict[section],
                                        path=path, level=level, toggle_buttons=toggle_buttons)
            else:
                toggle_buttons.append(None)
                self.create_checklist_button(frame, name=checklist_dict[section][sub_section], font=font,
                                             dict_path=path)

    def construct_columns(self, frame, checklist_dict):
        """ Constructs the columns for the checklists.
            Assumes the first key in the dict is the column name """
        temp = deepcopy(checklist_dict)
        self.check_button_dict = dict()
        num_cols = 0
        for column in sorted(list(temp.keys())):
            num_cols += 1
            if isinstance(temp[column], dict):
                toggle_buttons = []
                c_frame = Frame(frame)
                c_frame.pack(side=LEFT, anchor=NW)
                column_frame = self.create_section_frame(c_frame, title=column, font=self.column_font,
                                                         col_frame=c_frame, toggle_buttons=toggle_buttons)
                self.construct_sections(frame=column_frame, font=self.column_font, column=column, section=column,
                                        checklist_dict=temp, path=[column], toggle_buttons=toggle_buttons)
            else:
                raise Exception(f'Not a proper dictionary. Expected {column} to have a dictionary.')
        # Adjust Width and Height of each column
        self.update()
        col_frames = [c for c in frame.winfo_children() if type(c) == Frame]
        max_width = max([c.winfo_width() for c in col_frames])
        max_height = max([c.winfo_height() for c in col_frames])
        max_width = max_width if max_width < int(self.winfo_screenwidth()/num_cols) \
            else int(self.winfo_screenwidth()/num_cols)
        max_height = max_height if max_height < self.winfo_screenheight() else self.winfo_screenheight()
        for c in col_frames:
            c.pack_propagate(False)
            c.config(width=max_width, height=max_height)


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
    app.title('Exmaple Checklist')
    checklist = CheckList(app, dictionary=dictionary,
                          bg='white', fg='black', highlight_color='light blue')
    checklist.pack()
    app.mainloop()
