"""
HikerDataToCSV2.py
A more efficent and correct version of the HikerData writer which produces a CSV to be used by Pandas in the file
    'HikerDistanceLinearRegression.py'
:author: Chris Campell
:version: 11/7/2016
"""
import os
import json
from datetime import datetime
from collections import OrderedDict
import copy

__author__ = "Chris Campell"
__version__ = "11/7/2016"

avg_hikers_miles_per_day = None

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
                validated_shelters[shelter_id] = {
                    'name': shelter_name, 'dataset': data_set,
                    'type': type, 'lat': lat, 'lon': lon
                }
            line_num += 1
    return validated_shelters

def get_csv_header_list():
    """
    get_csv_header_list -Returns the CSV header as a list object ready to be written once delimited by commas and
        appended with a newline character.
    :return csv_header: A list of strings to be used as column headers for the written CSV file.
    """
    csv_header = []
    csv_header.append("HID")
    csv_header.append("ENUM")
    csv_header.append("LOCDIR")
    # Append a column header to keep track of the total mileage of the current entry:
    csv_header.append("TM")
    # Append a column header to keep track of the date of the current entry:
    csv_header.append("Date")
    # Append a column header to keep track of the elapsed change in trip mileage between entries:
    csv_header.append("DTM")
    # Append a column header to keep track of the number of elapsed days between entries:
    csv_header.append("DD")
    # Append a column header to keep track of the miles/day between journal entries:
    csv_header.append("MPD")
    # Append a column header to keep track of the user's average miles per day:
    csv_header.append("AVG_MPD")
    # Append a column header to keep track of the user's bias in relation to the average:
    csv_header.append("UB")
    # Append a column header to serve as the regularization term:
    csv_header.append("bias")
    return csv_header

def write_csv_header(csv_header, storage_location_path):
    """
    write_csv_header - Writes the csv header to DistancePrediction.csv in the specified storage directory.
    :param csv_header: A list of strings representing the column header for the CSV.
    :param storage_location_path: The location to write the output file 'DistancePrediction.csv'
    :return: Upon completion, the file DistancePrediction.csv will be written to the specified storage directory;
        populated with the CSV header.
    """
    # print("csv_header_len: %d" % len(csv_header))
    with open(storage_location_path + "/DistancePrediction.csv", 'w') as fp:
        # Write the CSV header to the output file.
        for i in range(len(csv_header)):
            if i != len(csv_header) - 1:
                fp.write(csv_header[i] + ",")
            else:
                fp.write(csv_header[i] + "\n")

def get_delta_trip_miles(journal_entry_one, journal_entry_two):
    """
    get_delta_trip_miles -Returns the elapsed difference in mileage between journal entries.
    :param journal_entry_one: The first journal entry.
    :param journal_entry_two: The next chronological journal entry.
    :return delta_mileage: The elapsed trip mileage between journal entry one and two.
    """
    return journal_entry_two['trip_mileage'] - journal_entry_one['trip_mileage']

def get_delta_days(journal_entry_one, journal_entry_two):
    """
    get_delta_days -Returns the elapsed number of days between journal entries.
    :param journal_entry_one: The first journal entry.
    :param journal_entry_two: The next chronological journal entry.
    :return delta.days: The elapsed number of days between journal entry one and two.
    """
    entry_one_date_string = journal_entry_one['date'].replace(",", "")
    entry_two_date_string = journal_entry_two['date'].replace(",", "")
    try:
        entry_one_date = datetime.strptime(entry_one_date_string, "%A %B %d %Y")
        entry_two_date = datetime.strptime(entry_two_date_string, "%A %B %d %Y")
        delta = entry_two_date - entry_one_date
        return delta.days
    except ValueError:
        print("Error: entry_one_date=%s\tentry_two_date=%s" %entry_two_date_string, entry_two_date_string)
        return None

def get_miles_per_day(delta_trip_miles, delta_days):
    """
    get_miles_per_day -Returns the elapsed mileage between the two provided journal entries.
    :param delta_trip_miles: The elapsed number of total trip miles between two journal entries.
    :param delta_days: The elapsed number of days between two journal entries.
    :return miles_per_day: The elapsed mileage between start locations of the two provided journal entries.
    """
    if delta_days != 0:
        miles_per_day = delta_trip_miles / delta_days
    else:
        miles_per_day = 0
    return miles_per_day

def add_hiker_attributes(validated_hiker):
    """
    add_hiker_attributes - Adds the hiker attributes that can only be calculated using pairwise comparison of journal
        entries.
    :param validated_hiker: A validated hiker read into memory by get_validated_hikers.
    :return updated_validated_hiker -A deepcopy of the original validated_hiker with added delta attributes.
    """
    updated_validated_hiker = copy.deepcopy(validated_hiker)
    sorted_hiker_journal_keys = list(updated_validated_hiker['journal'].keys())
    for enum1, enum2 in zip(sorted_hiker_journal_keys, sorted_hiker_journal_keys[1:]):
        entry_one = updated_validated_hiker['journal'][enum1]
        entry_two = updated_validated_hiker['journal'][enum2]
        updated_validated_hiker['journal'][enum1]['date'] = entry_one['date'].replace(",", "")
        location_direction =  entry_one['start_loc']['SID'] + entry_one['start_loc']['dir']
        delta_mileage = get_delta_trip_miles(entry_one, entry_two)
        delta_days = get_delta_days(entry_one, entry_two)
        miles_per_day = get_miles_per_day(delta_mileage, delta_days)
        updated_validated_hiker['journal'][enum1]['loc-dir'] = location_direction
        updated_validated_hiker['journal'][enum1]['delta_mileage'] = delta_mileage
        updated_validated_hiker['journal'][enum1]['delta_days'] = delta_days
        updated_validated_hiker['journal'][enum1]['miles_per_day'] = miles_per_day
        updated_validated_hiker['journal'][enum1]['entry_string'] = ""
    return updated_validated_hiker

def compute_hiker_avg_miles_per_day(validated_hiker):
    """
    compute_hiker_avg_miles_per_day -Returns an individual hiker's average miles per day computed over all valid
        start_locations.
    :param validated_hiker:
    :return:
    """
    total_miles_per_day = 0
    total_num_entries = 0
    for enum, entry in validated_hiker['journal'].items():
        if 'miles_per_day' in entry:
            total_num_entries += 1
            total_miles_per_day += entry['miles_per_day']
    hiker_average_miles_per_day = total_miles_per_day / total_num_entries
    return hiker_average_miles_per_day

def write_to_csv(valid_hikers, storage_location_path):
    write_csv_header(get_csv_header_list(), storage_location_path)
    with open(storage_location_path + "/DistancePrediction.csv", 'a') as fp:
        for hid, hiker in valid_hikers.items():
            for enum, entry in hiker['journal'].items():
                if 'entry_string' in entry:
                    fp.write(entry['entry_string'])

def main(valid_shelters_path, valid_hikers_path, storage_location_path):
    valid_shelters = get_validated_shelters(validated_shelters_path=valid_shelters_path)
    valid_hikers = get_validated_hikers(validated_hikers_path=valid_hikers_path)
    # Update every hiker dict with new attributes:
    for hid, hiker in valid_hikers.items():
        valid_hikers[hid] = add_hiker_attributes(hiker)
    # Give every hiker an attribute corresponding to the hiker's average miles per day.
    for hid, hiker in valid_hikers.items():
        hiker_avg_miles_per_day = compute_hiker_avg_miles_per_day(hiker)
        valid_hikers[hid]['avg_miles_per_day'] = hiker_avg_miles_per_day
    # Get the average hiker's average miles-per-day:
    num_entries = 0
    total_avg_miles_per_day = 0
    for hid, hiker in valid_hikers.items():
        total_avg_miles_per_day += hiker['avg_miles_per_day']
        num_entries += 1
    avg_hikers_miles_per_day = total_avg_miles_per_day / num_entries
    # Calculate the user bias for every hiker in relation to the average:
    for hid, hiker in valid_hikers.items():
        valid_hikers[hid]['user_bias'] = hiker['avg_miles_per_day'] - avg_hikers_miles_per_day
    # Update journal entry strings:
    for hid, hiker in valid_hikers.items():
        for enum, entry in hiker['journal'].items():
            if 'miles_per_day' in entry:
                journal_entry_string = \
                    str(hiker['identifier']) + "," + str(enum) + "," \
                    + entry['loc-dir'] + "," + str(entry['trip_mileage']) + "," \
                    + entry['date'] + "," + str(entry['delta_mileage']) + "," \
                    + str(entry['delta_days']) + "," + str(entry['miles_per_day']) + "," \
                    + str(hiker['avg_miles_per_day']) + "," + str(hiker['user_bias']) + ",1\n"
                valid_hikers[hid]['journal'][enum]['entry_string'] = journal_entry_string
    write_to_csv(valid_hikers, storage_location_path)

if __name__ == '__main__':
    validated_shelter_data_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/TrailShelters/'))
    validated_hikers_data_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/VHDistancePrediction/'))
    csv_write_location_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/'))
    main(valid_shelters_path=validated_shelter_data_path, valid_hikers_path=validated_hikers_data_path,
         storage_location_path=csv_write_location_path)
