"""
ShelterDuplicateRemover.py
Takes the combined AT Shelters data set and removes duplicates, then exports to CSV.
:Author: Chris Campell
:Version: 8/25/2016
"""

import os
import collections
from fuzzywuzzy import fuzz

"""
main -Goes through every shelter in the AT_Shelters_Combined dataset and removes duplicate shelters. Then the new
    dataset (with duplicates removed) is written to the hard drive.
"""
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
                    'lat': float(read_data[2]),
                    'lon': float(read_data[3]),
                    'shelter_type': read_data[4]
                }
            line_num += 1
    shelters_no_duplicates = remove_duplicates(shelters=shelters)

"""
remove_duplicates -Finds and removes duplicate shelters in the dataset by utilizing two comparisions for equality:
    1. A fuzzy string comparison between the duplicate in question and every entry in the unique shelter dataset,
        with a comparison threshold of 90/100 or greater.
    2. A latitude and longitude comparison between the duplicate shelter in question and every entry in the unique
        shelter dataset. Latitude and longitude are rounded to the 3rd decimal place and then compared for equality.
:param shelters -A dictionary representing the entire Combined_Shelter_Dataset with duplicates to be removed included.
"""
def remove_duplicates(shelters):
    shelters_no_duplicates = collections.OrderedDict()
    # Add the first shelter to the list of no duplicates.
    shelters_no_duplicates[1] = shelters[1]
    comparison_threshold = 90

    for key1, value1 in shelters.items():
        same_shelter_by_string = False
        same_shelter_by_gis = False
        for key2,value2 in shelters_no_duplicates.items():
            # Shelter fuzzy string comparison.
            comparison_ratio = fuzz.partial_ratio(value1['name'], value2['name'])
            if comparison_ratio >= comparison_threshold:
                # The shelters are the same by fuzzy string comparison.
                print("Comparing Names: %s and %s" %(value1['name'], value2['name']))
                print("Comparison Ratio: %d" %comparison_ratio)
                same_shelter_by_string = True

                # Compare the shelters by latitude and longitude (rounded to 100ths place)
                value1_lat = value1['lat']
                value1_lon = value1['lon']
                value2_lat = value2['lat']
                value2_lon = value2['lon']
                value1_lat = float("{0:.3f}".format(value1_lat))
                value1_lon = float("{0:.3f}".format(value1_lon))
                value2_lat = float("{0:.3f}".format(value2_lat))
                value2_lon = float("{0:.3f}".format(value2_lon))
                if value1_lat == value2_lat or value1_lon == value2_lon:
                    # The shelters are the same by latitude comparison.
                    same_shelter_by_gis = True
            else:
                same_shelter_by_string = False
        if not same_shelter_by_string:
            if not same_shelter_by_gis:
                shelters_no_duplicates[key1] = value1
    return shelters_no_duplicates

def write_data():
    pass

if __name__ == '__main__':
    main()
