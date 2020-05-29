import sys
import json 

def setup(filepath='data/codes.json'):
    with open(filepath) as json_file:
        master_location_dictionary=[]
        data = json.load(json_file)
        for location in data['TIPLOCDATA']:
            if location['3ALPHA'] != ' ':
                TIPLOC = location['TIPLOC']
                DESC = location['NLCDESC']
                CRS = location['3ALPHA']
                if CRS != " ":
                    PRIORITY = 1
                else:
                    PRIORITY = 2
                master_location_dictionary.append(
                    {
                        "TIPLOC": TIPLOC,
                        "DESC": DESC,
                        "CRS": CRS,
                        "PRIORITY": PRIORITY
                        }
                )
    master_location_dictionary = sorted(master_location_dictionary, key=lambda k: k['PRIORITY'])
    print(master_location_dictionary, file=sys.stderr)
    return master_location_dictionary

location_dict = setup()

