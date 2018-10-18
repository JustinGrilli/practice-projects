import json
from pprint import pprint


manowar_data_json = open('results_manowar.json', 'r')
manowar_data_json = manowar_data_json.read().split('\n')
# print manowar_data_json
for x in manowar_data_json:
    results_manowar_json = json.loads(x)
    pprint(results_manowar_json)


json_file = open('data_file.json', 'r')
data_results = json.load(json_file)
#
# print data_results