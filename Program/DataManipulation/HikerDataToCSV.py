"""
HikerDataToCSV.py
Takes all validated hikers and writes them to CSV format for use in Pandas.
__author__ = Chris Campell
__version__ = 9/29/2016
"""
import os
import json
from collections import OrderedDict
from datetime import datetime

"""
get_validated_hikers -Returns a dictionary of the hikers validated using the code in HikerValidator2.py
:param validated_hikers_path: The file path to the CSV file containing the validated hikers.
:return validated_hikers: A dictionary containing the validated hikers.
"""
def get_validated_hikers(validated_hikers_path):
    validated_hikers = {}
    for filename in os.listdir(validated_hikers_path):
        with open(validated_hikers_path + "/" + filename, 'r') as fp:
            hiker = json.load(fp=fp)
            validated_hikers[int(filename.strip(".json"))] = hiker
    return validated_hikers

"""
get_validated_shelters -Returns a dictionary of the shelters validated using the combined TNL and ATC data sets.
@param validated_shelters_path -The path to the CSV file containing the validated shelters.
@return validated_shelters -A dictionary containing the geocoded shelters.
"""
def get_validated_shelters(validated_shelters_path):
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

def write_csv_shelter_entry(csv_header, journal_entry_string, entry_num, journal_entry):
    """
    write_csv_shelter_entry -Writes the shelter section of the journal entry string for a given entry. Returns the
        provided journal_entry_string with the concatenated shelter information.
    :param csv_header: The csv header to use as a guidline for building the csv journal entry row.
    :param journal_entry_string: The string so far for the current journal entry. Should contain the 'HID,ENUM,'.
    :param entry_num: The unique identifier associated with the journal entry.
    :param journal_entry: The journal entry itself.
    :return:
    """
    # Go through every hikers journal; extracting each journal entry.
    # The hiker journal entries in directory VHDistancePrediction must have at least one valid start_loc.
    for i in range(2, len(csv_header) - 6):
        if journal_entry['start_loc']['SID'] + journal_entry['start_loc']['dir'] == csv_header[i]:
            # The entry for the start_loc matches the column header.
            journal_entry_string += "1,"
        else:
            # The entry for the start_loc does not match the column header.
            journal_entry_string += "0,"
    return journal_entry_string

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
    except ValueError:
        print("Error: entry_one_date=%s\tentry_two_date=%s" %entry_two_date_string, entry_two_date_string)
    return delta.days

def get_csv_header(valid_shelters, storage_location_path):
    """
    get_csv_header -Returns an array of strings that form the csv header. Writes the csv header to the output file.
    :param valid_shelters: An ordered dictionary composed of the validated shelters from the combined data sets.
    :param storage_location_path: A os.path pointing to the storage location for the csv to be written to.
    :return csv_header: An array of strings that make up the csv header (this array is written to the csv with comma
        delimiters before returning).
    """
    csv_header = []
    csv_header.append("HID")
    csv_header.append("ENUM")
    num_shelter_cols = 0
    for sid, shelter in valid_shelters.items():
        # Append the ShelterID (SID) and the associated direction (North or South)
        csv_header.append(str(sid) + "N")
        csv_header.append(str(sid) + "S")
        num_shelter_cols += 2
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
    # Append a column header to serve as the regularization term:
    csv_header.append("bias")
    # print("csv_header_len: %d" % len(csv_header))
    with open(storage_location_path + "/DistancePrediction.csv", 'w') as fp:
        # Write the CSV header to the output file.
        for i in range(len(csv_header)):
            if i != len(csv_header) - 1:
                fp.write(csv_header[i] + ",")
            else:
                fp.write(csv_header[i] + "\n")
    return csv_header

"""
write_to_csv -Writes the hiker data to CSV format at the specified storage_location in a form intended to be used
    by Pandas for Linear Regression Least Squares approximation.
:param valid_hikers: A dictionary containing the geocoded hiker locations.
:param valid_shelters: A dictionary containing the AT Shelters dataset.
:param storage_location_path: The location to write the created CSV to.
"""
def write_to_csv(valid_hikers, valid_shelters, storage_location_path):
    # Build and write the CSV header (the column header for LstSqr):
    csv_header = get_csv_header(valid_shelters, storage_location_path)
    # Go through every hiker and create a row in the csv for each trail journal:
    for hid, hiker_info in valid_hikers.items():
        hiker_strings = []
        sorted_hiker_journal_keys = sorted([int(enum) for enum in hiker_info['journal'].keys()])
        for enum1, enum2 in zip(sorted_hiker_journal_keys, sorted_hiker_journal_keys[1:]):
            first_entry = hiker_info['journal'][str(enum1)]
            next_entry = hiker_info['journal'][str(enum2)]
            # Label csv entry with the hiker identifier and journal entry number:
            journal_entry_string = str(hid) + "," + str(enum1) + ","
            # Label csv entry with the start_loc shelter and direction of departure (e.g. 108N or 108S):
            journal_entry_string = write_csv_shelter_entry(
                csv_header=csv_header, journal_entry_string=journal_entry_string, entry_num=enum1,
                journal_entry=first_entry)
            # Append the total trip mileage to the csv entry string:
            journal_entry_string = journal_entry_string + str(first_entry['trip_mileage']) + ","
            # Append the date to the csv entry string:
            journal_entry_date = first_entry['date'].replace(",", "")
            journal_entry_string = journal_entry_string + journal_entry_date + ","
            # If there is another following entry compute the delta attributes:
            if next_entry:
                # Append the delta mileage between entries to the csv entry string:
                delta_mileage = get_delta_trip_miles(journal_entry_one=first_entry, journal_entry_two=next_entry)
                journal_entry_string = journal_entry_string + str(delta_mileage) + ","
                # Append the elapsed number of days between entries to the csv entry string:
                delta_days = get_delta_days(journal_entry_one=first_entry, journal_entry_two=next_entry)
                journal_entry_string = journal_entry_string + str(delta_days) + ","
                # Append miles per day between entry_one and entry_two:
                if delta_days != 0:
                    miles_per_day = delta_mileage / delta_days
                else:
                    miles_per_day = 0
                journal_entry_string = journal_entry_string + str(miles_per_day) + ",1\n"
            else:
                # There is no next entry for this hiker. Can't compute delta attributes. Save as '-'.
                journal_entry_string += "-,-,-,1\n"
            hiker_strings.append(journal_entry_string)
        with open(storage_location_path + "/DistancePrediction.csv", 'a') as fp:
            for string in hiker_strings:
                fp.write(string)

def main(valid_shelters_path, valid_hikers_path, storage_location_path):
    valid_shelters = get_validated_shelters(validated_shelters_path=valid_shelters_path)
    valid_hikers = get_validated_hikers(validated_hikers_path=valid_hikers_path)
    write_to_csv(valid_hikers, valid_shelters, storage_location_path)

if __name__ == '__main__':
    validated_shelter_data_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/TrailShelters/'))
    validated_hikers_data_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/VHDistancePrediction/'))
    csv_write_location_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/'))
    main(valid_shelters_path=validated_shelter_data_path, valid_hikers_path=validated_hikers_data_path,
         storage_location_path=csv_write_location_path)
