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
<<<<<<< HEAD
    storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/TrailShelters/'))
=======
    storage_dir = "/home/chuckdaddy/Documents/AppalachianTrailGuide/Data/TrailShelters/"
>>>>>>> ff53fd364cac1fcdf8933138747545f8d9586abf
    cwd = os.getcwd()
    shelters = collections.OrderedDict()
    with open(storage_dir + "/" +filename, 'r') as fp:
        line_num = 0
        for line in iter(fp):
            if line_num != 0:
                read_data = line.split(",")
                shelters[line_num] = {
                    'SID': line_num,
                    'name': mt_to_mount(read_data[0]),
                    'data_set': read_data[1],
                    'lat': float(read_data[2]),
                    'lon': float(read_data[3]),
                    'shelter_type': read_data[4]
                }
            line_num += 1
<<<<<<< HEAD
    shelters_no_duplicates = remove_duplicates(shelters=shelters)
    write_data(shelters_no_duplicates)

def mt_to_mount(original_name):
    if "Mt." in original_name:
        original_name = original_name.replace("Mt", "Mount")
    return original_name

=======
    remove_duplicates(shelters=shelters)
    write_data(shelters)
>>>>>>> ff53fd364cac1fcdf8933138747545f8d9586abf

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
<<<<<<< HEAD

    for key1, value1 in shelters.items():
        same_shelter_by_string = False
        same_shelter_by_gis = False
=======
    counter = 0
    for key1,value1 in shelters.items():
        same_shelter = False
>>>>>>> ff53fd364cac1fcdf8933138747545f8d9586abf
        for key2,value2 in shelters_no_duplicates.items():
            # Shelter fuzzy string comparison.
            comparison_ratio = fuzz.partial_ratio(value1['name'], value2['name'])
            if comparison_ratio >= comparison_threshold:
<<<<<<< HEAD
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

def write_data(shelters_no_duplicates):
    storage_location = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/TrailShelters/'))
    new_shelters_csv = open(storage_location + "/" + "newShelters.csv", 'w')
    new_shelters_csv.write("SID,name,data_set,lat,lon,shelter_type\n")
    sid = 0
    for key,value in shelters_no_duplicates.items():
        sid += 1
        new_shelters_csv.write(str(sid) + "," + value['name'] + "," +  value['data_set']
=======
                # The shelters are the same.
                counter += 1
                #print("Comparing Names: %s and %s" %(value1['name'], value2['name']))
                #print("Comparison Ratio: %d" %comparison_ratio)
                same_shelter = True
            else:
                same_shelter = False
        if not same_shelter:
            shelters_no_duplicates[key1] = value1
    print(counter)

"""
write non duplicates to a csv file
"""
def write_data(shelters_no_duplicates):
    storage_location = "/home/chuckdaddy/Documents/AppalachianTrailGuide/Data/TrailShelters/"
    new_shelters_csv = open(storage_location + "newShelters.csv", 'w')
    new_shelters_csv.write("SID,name,data_set,lat,lon,shelter_type\n")
    for key,value in shelters_no_duplicates.items():
        new_shelters_csv.write(str(value['SID']) + "," + value['name'] + "," +  value['data_set']
>>>>>>> ff53fd364cac1fcdf8933138747545f8d9586abf
        + "," + str(value['lat']) + "," + str(value['lon']) + "," + value['shelter_type'])
    new_shelters_csv.close()

if __name__ == '__main__':
    main()
