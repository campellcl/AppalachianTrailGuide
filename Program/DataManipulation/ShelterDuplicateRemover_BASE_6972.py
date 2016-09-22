"""
ShelterDuplicateRemover.py
Takes the combined AT Shelters data set and removes duplicates, then exports to CSV.
:Author: Chris Campell
:Version: 8/25/2016
"""

import os
import collections
from fuzzywuzzy import fuzz

def main():
    filename = "AT Shelters Combined.csv"
    storage_dir = "C:/Users/Chris/Documents/GitHub/AppalachianTrailGuide/Data/TrailShelters/"
    cwd = os.getcwd()
    shelters = collections.OrderedDict()
    with open(storage_dir + filename, 'r') as fp:
        line_num = 0
        for line in iter(fp):
            if line_num != 0:
                read_data = line.split(",")
                shelters[line_num] = {
                    'SID': line_num,
                    'name': read_data[0],
                    'data_set': read_data[1],
                    'lat': read_data[2],
                    'lon': read_data[3],
                    'shelter_type': read_data[4]
                }
            line_num += 1
    remove_duplicates(shelters=shelters)

def remove_duplicates(shelters):
    shelters_no_duplicates = collections.OrderedDict()
    # Add the first shelter to the list of no duplicates?
    shelters_no_duplicates[1] = shelters[1]
    comparison_threshold = 90

    for key1,value1 in shelters.items():
        same_shelter = False
        for key2,value2 in shelters_no_duplicates.items():
            # Shelter string comparison.

            comparison_ratio = fuzz.partial_ratio(value1['name'], value2['name'])
            if comparison_ratio >= comparison_threshold:
                # The shelters are the same.
                print("Comparing Names: %s and %s" %(value1['name'], value2['name']))
                print("Comparison Ratio: %d" %comparison_ratio)
                same_shelter = True
            else:
                same_shelter = False
        if not same_shelter:
            shelters_no_duplicates[key1] = value1

def write_data():
    pass

if __name__ == '__main__':
    main()