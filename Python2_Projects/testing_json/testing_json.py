import json
from pprint import pprint


manowar_data_json = open('results_manowar.json', 'r')
manowar_data_json_dict_list = manowar_data_json.read().split('\n')
manowar_data_json_dict_list = filter(None, manowar_data_json_dict_list)

classes_list = []
for x in manowar_data_json_dict_list:
    current_dict = json.loads(x)
    if current_dict['class'] not in classes_list:
        classes_list.append(current_dict['class'])

print '\nClasses:\n'
pprint(classes_list)
print '\n\n_____________________________________________________________________________________________________________\n'
for x in manowar_data_json_dict_list:
    current_dict = json.loads(x)
    if current_dict['class'] == 'BuildingVersion':
        pprint(current_dict)
        pprint('_____________________________________________________________________________________________________________')


# pprint(json.loads(manowar_data_json))


# json_file = open('data_file.json', 'r')
# data_results = json.load(json_file)
#
# print data_results