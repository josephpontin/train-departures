import sys
import json 

def setup(filepath='data/codes.json'):
    with open(filepath) as json_file:
        master_location_dictionary={}
        data = json.load(json_file)
        for location in data['TIPLOCDATA']:
            if location['TIPLOC'] != " " and location['NLCDESC'] != " ":
                master_location_dictionary[location['NLCDESC']] = location['TIPLOC']
    
    return master_location_dictionary

location_dict = setup()

