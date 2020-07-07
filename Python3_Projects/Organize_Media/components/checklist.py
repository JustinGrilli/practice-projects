from tkinter import *
from copy import deepcopy
from PIL import Image, ImageTk
# Import components
from .collapsible_frame import CollapsibleFrame


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
        self.font = kwargs.pop('font', ('none', 20, 'bold'))
        self.dictionary = dictionary
        self.reference_dict = deepcopy(dictionary)
        self.check_button_dict = dict()
        self.toggle_button_dict = deepcopy(dictionary)
        self.toggle_config = kwargs.pop('toggle_config', {'deselect': 'X', 'select': 'O'})
        self.toggle_type = kwargs.pop('toggle_type', 'text')
        self.deepest_level = 0

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
        if widget.var.get():
            self.add_to_dict(path, self.dictionary, self.reference_dict)
            widget['bg'] = self.highlight_color
        else:
            self.remove_from_dict(path, self.dictionary)
            widget['bg'] = self.bg

    def all_children(self, widget, callback):
        _list = widget.winfo_children()
        for w in _list:
            callback.append(w)
            self.all_children(w, callback)
        return callback

    def update_button_toggle(self, path, dictionary, frame, first_run=True):
        if len(path) >= 1 and isinstance(dictionary[path[0]], dict):
            f = dictionary[path[0]]['frame']
            b = dictionary[path[0]]['button']
            callback = []
            checkbutton_children = [c for c in self.all_children(f, callback)
                                    if type(c) == Checkbutton and not c.var.get()]
            if checkbutton_children:
                b[self.toggle_type] = self.toggle_config['select']
            else:
                b[self.toggle_type] = self.toggle_config['deselect']
            # Set all child toggle buttons equal to the parent on the first
            if first_run:
                callback = []
                toggle_children = [b for b in self.all_children(frame, callback)
                                   if type(b) == Button
                                   and b[self.toggle_type] in [str(i) for i in self.toggle_config.values()]]
                for child in toggle_children:
                    child[self.toggle_type] = b[self.toggle_type]
            self.update_button_toggle(path[1:], dictionary[path[0]], frame, first_run=False)

    def toggle_all(self, x):
        """ Functionality when clicking a toggle all button:
            - Checks all dependant check buttons: on or off depending on the status of the toggle button
            - Adjusts the status of other dependant toggle buttons """

        frame, button, path = x
        child_callback = []
        checklist_children = [obj for obj in self.all_children(frame, child_callback) if type(obj) == Checkbutton]
        # Toggle each item in the dictionary based on the toggle
        toggle = str(button[self.toggle_type]) == str(self.toggle_config['select'])
        for c in checklist_children:
            c.var = BooleanVar(value=toggle)
            c['variable'] = c.var
            self.upon_select(c)

        # Go down the path, and toggle button on or off based on each dependant checkbutton's status
        self.update_button_toggle(path, self.toggle_button_dict, frame)

    def create_checklist_button(self, frame, dict_path, **kwargs):
        """ Creates a Checkbutton and adds it to the dictionary of Checkbuttons """
        name = kwargs.pop('name', None)
        font = kwargs.pop('font', None)
        cbutton = Checkbutton(frame, text=name, fg=self.fg, onvalue=True, highlightthickness=0, bd=0,
                              offvalue=False, anchor=W, justify=LEFT, font=font, cursor='hand2',
                              selectcolor=self.highlight_color, bg=self.highlight_color,
                              activeforeground=self.fg, activebackground=self.highlight_color)
        cbutton.var = BooleanVar(value=True)
        cbutton['variable'] = cbutton.var
        cbutton['command'] = lambda w=cbutton: self.upon_select(w)
        self.check_button_dict[cbutton] = dict_path

    def add_to_toggle_button_dict(self, path, dict, button, frame):
        if len(path) > 1:
            self.add_to_toggle_button_dict(path[1:], dict[path[0]], button, frame)
        elif len(path) == 1:
            dict[path[0]]['button'] = button
            dict[path[0]]['frame'] = frame

    def create_section_frame(self, frame, **kwargs):
        """ Create the section frame for a given section """
        path = kwargs.pop('path', None)
        title = kwargs.pop('title', None)
        font = kwargs.pop('font', None)
        padx = kwargs.pop('padx', None)
        pady = kwargs.pop('pady', None)
        start_collapsed = kwargs.pop('start_collapsed', True)

        section_frame = Frame(frame, bg=self.bg)
        section_frame.pack(side=TOP, fill=X, padx=padx, pady=pady, anchor=NW)

        f = CollapsibleFrame(section_frame, title=title, font=font, bg=self.bg, fg=self.fg,
                             highlight_color=self.highlight_color, title_color=self.border_color,
                             start_collapsed=start_collapsed)
        section_bottom_frame = Frame(f.collapse_frame, bg=self.bg)
        toggle_button = Button(f.top_frame, cursor='hand2', relief=FLAT, bd=0, highlightthickness=0,
                               bg=self.bg, fg=self.fg, activebackground=self.bg, activeforeground=self.fg)
        toggle_button[self.toggle_type] = self.toggle_config['deselect']
        toggle_button['command'] = lambda x=(section_bottom_frame, toggle_button, path): self.toggle_all(x)
        toggle_button.pack(side=LEFT)
        self.add_to_toggle_button_dict(path=path, dict=self.toggle_button_dict, button=toggle_button,
                                       frame=section_bottom_frame)

        section_bottom_frame.pack(side=TOP, fill=X, anchor=NW)

        return section_bottom_frame

    def construct_sections(self, frame, level=0, section=None, checklist_dict=None,
                           path=None, **kwargs):
        """ Constructs all sections for a given dictionary.
            Will continue creating sections until the value is not a dictionary. """
        font = kwargs.pop('font', None)
        padx = kwargs.pop('padx', None)
        pady = kwargs.pop('pady', None)
        # Use the level to keep track of how deep we are in the dictionary
        level += 1
        if level > self.deepest_level:
            self.deepest_level = level
        font = (font[0], font[1] - 2, font[2])
        for sub_section in sorted([k for k in checklist_dict[section].keys()]):
            # Adjust path for the section based on the level of the dictionary
            if len(path) >= level + 1:
                path = path[:level + 1]
                path.pop(level)
            path.append(sub_section)

            if isinstance(checklist_dict[section][sub_section], dict):
                section_frame = self.create_section_frame(frame, title=sub_section, font=font, padx=padx, pady=pady,
                                                          path=path)
                self.construct_sections(frame=section_frame, font=font, padx=padx, pady=pady,
                                        section=sub_section, checklist_dict=checklist_dict[section],
                                        path=path, level=level)
            else:
                self.create_checklist_button(frame, name=checklist_dict[section][sub_section], font=font,
                                             dict_path=path)

    def construct_columns(self, frame, checklist_dict):
        """ Constructs the columns for the checklists.
            Assumes the first key in the dict is the column name """
        temp = deepcopy(checklist_dict)
        indent = 25
        num_cols = 0
        for column in sorted(list(temp.keys())):
            num_cols += 1
            if isinstance(temp[column], dict):
                toggle_buttons = []
                c_frame = Frame(frame, bg=self.bg)
                c_frame.pack(side=LEFT, anchor=NW)
                column_frame = self.create_section_frame(c_frame, title=column, font=self.font, path=[column],
                                                         toggle_buttons=toggle_buttons, start_collapsed=False,
                                                         padx=2, pady=2)
                self.construct_sections(frame=column_frame, font=self.font, section=column,
                                        checklist_dict=temp, path=[column], toggle_buttons=toggle_buttons,
                                        padx=(indent, 0), pady=4)
            else:
                raise Exception(f'Not a proper dictionary. Expected {column} to have a dictionary.')
        # Pack the Check Buttons
        for ch in self.check_button_dict.keys():
            ch['font'] = (self.font[0], self.font[1] - (self.deepest_level * 2), self.font[2])
            ch.pack(side=TOP, fill=X, anchor=NW, pady=1, padx=(indent, 0))


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

    colors = {
        'main': '#%02x%02x%02x' % (20, 20, 20),
        'sub': '#%02x%02x%02x' % (35, 35, 35),
        'special': '#%02x%02x%02x' % (92, 15, 128),
        'special_alt': '#%02x%02x%02x' % (180, 53, 240),
        'alt': '#%02x%02x%02x' % (60, 111, 194),
        'font': '#%02x%02x%02x' % (255, 255, 255)
    }
    font = ('Arial', 20, 'bold')

    app = Tk()
    app.title('Example Checklist')
    checklist = CheckList(app, dictionary=dictionary, bg=colors['main'], fg=colors['font'], font=font,
                          highlight_color=colors['sub'], border_color=colors['special'])
    checklist.pack()
    app.mainloop()
