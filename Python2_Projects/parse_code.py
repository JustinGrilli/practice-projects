from code_sample import event
from decimal import Decimal


def parse_orders_note_value_after_colon(the_event, parse_from):
    parse_list = []
    notes = the_event['notes']
    print notes

    new_notes = []
    for letter in notes:
        if letter != '[' and letter != ']':
            new_notes.append(letter)

    notes = ''.join(new_notes)

    notes_lists = notes.split('\n')
    # print notes_lists
    notes_list = []

    for list in notes_lists:
        notes_list.append(list.split(' '))
    # print notes_list

    for list in notes_list:
        count = 0
        for item in list:
            if item == parse_from:
                parse_list.append(list[count + 1])
            count += 1
    try:
        print '\n\n'
        print Decimal(parse_list[-1])
    except:
        last_value_list = parse_list[-1].split(',')

        print '\n\n'
        print Decimal(last_value_list[0])


def parse_orders_note_list_after_colon(the_event, section, parse_from):
    parse_list = []
    notes = the_event['notes']
    print notes

    notes_lists = notes.split('\n\n')

    list_notes = []
    for item in notes_lists:
        list_notes.append(item.split('\n'))
    list_notes[0].remove('')
    list_notes[-1].remove('')

    for list in list_notes:
        list[0] = list[0].split(']')[-1].split(':')[0]
        listed_list = list[0].split(' ')
        list[0] = ' '.join(listed_list[1:])

    print list_notes
    for one_down_list in list_notes:
        # Convert string to list
        for item in one_down_list[1:]:
            new_item = item.split(':')
            one_down_list.remove(item)
            one_down_list.append(new_item)
        # Convert list to dictionary
        print list_notes
        for two_down_list in one_down_list[1:]:
            two_down_list[0] = ' '.join(two_down_list[0].split(' ')[1:])
            value_dict = {}
            value_dict.update({two_down_list[0]: two_down_list[1:]})
            one_down_list.remove(two_down_list)
            one_down_list.append(value_dict)

    notes_dict = {}
    for list in list_notes:
        notes_dict[list[0]] = list[1:]


    print list_notes
    print notes_dict
    print notes_dict[section][-1][parse_from]
    notes_list = []


# parse_orders_note_list_after_colon(event, 'Scale from 3 doors', 'Final Scale')
parse_orders_note_value_after_colon(event, 'Deviation:')