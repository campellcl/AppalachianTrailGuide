"""
SPLR.py
Shelter Population Linear Regression: Performs linear regression to predict the weekly population of shelters along the AT.
:author: Chris Campell
:version: 12/1/2016
"""
__author__ = "Chris Campell"
__version__ = "12/1/2016"

import os
import json
from collections import OrderedDict
from datetime import datetime
import operator

def get_validated_hikers(validated_hikers_path):
    """
    get_validated_hikers -Reads all validated hikers in the specified directory into memory. Returns an
        OrderedDictionary of validated_hikers sorted by hiker identifier.
    :param validated_hikers_path: The file path to the CSV file containing the validated hikers.
    :return sorted_validated_hikers: A dictionary containing the sorted validated hikers.
    """
    validated_hikers = {}
    for filename in os.listdir(validated_hikers_path):
        with open(validated_hikers_path + "/" + filename, 'r') as fp:
            hiker = json.load(fp=fp)
            validated_hikers[int(filename.strip(".json"))] = hiker
    # Sort the validated_hikers by hiker id:
    sorted_validated_hikers = OrderedDict(sorted(validated_hikers.items()))
    for hid, hiker in sorted_validated_hikers.items():
        sorted_hiker_journal = OrderedDict()
        for enum, entry in hiker['journal'].items():
            sorted_hiker_journal[int(enum)] = entry
        sorted_validated_hikers[hid]['journal'] = OrderedDict(sorted(sorted_hiker_journal.items()))
    # Sort the hiker's trail journals by entry number (chronologically....kinda):
    return sorted_validated_hikers

def get_validated_shelters(validated_shelters_path):
    """
    get_validated_shelters -Returns a dictionary of the shelters validated using the combined TNL and ATC data sets.
    @param validated_shelters_path -The path to the CSV file containing the validated shelters.
    @return validated_shelters -A dictionary containing the geocoded shelters.
    """
    validated_shelters = OrderedDict()
    line_num = 0
    with open(validated_shelters_path + "/ATSheltersCombinedNoDuplicates.csv", 'r') as fp:
        for line in iter(fp):
            if not line_num == 0:
                split_string = str.split(line, sep=",")
                shelter_id = split_string[0]
                shelter_name = split_string[1]
                data_set = split_string[2]
                lat = float(split_string[3])
                lon = float(split_string[4])
                type = split_string[5]
                validated_shelters[int(shelter_id)] = {
                    'name': shelter_name, 'dataset': data_set,
                    'type': type, 'lat': lat, 'lon': lon
                }
            line_num += 1
    return validated_shelters


def main():
    validated_hikers_storage_loc = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/VHDistancePrediction/')
    )
    validated_shelters_storage_loc = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/TrailShelters/')
    )

    valid_hikers = get_validated_hikers(validated_hikers_path=validated_hikers_storage_loc)
    valid_shelters = get_validated_shelters(validated_shelters_path=validated_shelters_storage_loc)
     # iterate over every hiker and every journal entry, record the HID, Enum, SID+Dir, Datetime, week_of_year, month_of_year
    shelter_pop_stats = {}
    i = 0
    for hid, hiker in valid_hikers.items():
        for enum, entry in hiker['journal'].items():
            entry_date = entry['date'].replace(',', "")
            try:
                entry_date = datetime.strptime(entry_date, "%A %B %d %Y")
            except Exception:
                print("Exception encountered with hid: %d. Entry number: %d." %(hid, enum))
                exit(-1)
            current_entry_start_loc_shelter = entry['start_loc']['SID']
            current_entry_dir = entry['start_loc']['dir']
            shelter_pop_stats[i] = {
                'HID': hid, 'ENUM': enum, 'LOCDIR': str(current_entry_start_loc_shelter) + current_entry_dir,
                'Date': entry_date, 'Week': entry_date.isocalendar()[1], 'Month': entry_date.month
            }
            i += 1
    # Write collected data to csv or go from dict to dataframe.


    # Sort validated hiker's journal entries chronologically by date.
    for hid, hiker_info in valid_hikers.items():
        entry_numbers_and_dates = {}
        for enum, entry in hiker_info['journal'].items():
            entry_date = entry['date'].replace(',', "")
            try:
                entry_date = datetime.strptime(entry_date, "%A %B %d %Y")
            except Exception:
                print("Exception encountered with hid: %d. Entry number: %d." %(hid, enum))
            entry_numbers_and_dates[enum] = entry_date
        # now sort the entry numbers by datetime:
        sorted_enums_by_date = sorted(entry_numbers_and_dates.items(), key=operator.itemgetter(0))
        chrono_sorted_hiker_journal = OrderedDict()
        for enum, sorted_entry in sorted_enums_by_date:
            chrono_sorted_hiker_journal[enum] = hiker_info['journal'][enum]
        # replace the hiker's journal with the chronologically sorted one:
        hiker_info['journal'] = chrono_sorted_hiker_journal
    print("Finished Sorting all Hiker Entries by datetime representation.")


if __name__ == '__main__':
    main()


