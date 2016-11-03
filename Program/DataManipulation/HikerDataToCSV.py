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
    for i in range(len(csv_header)):
        if i == len(csv_header) - 1:
            # Entry is the last in the csv row.
            if journal_entry['start_loc']['SID'] + journal_entry['start_loc']['dir'] == csv_header[i]:
                # The entry for the start_loc matches the column header.
                journal_entry_string += "1,"
            else:
                # The entry for the start_loc does not match the column header.
                journal_entry_string += "0,"
            print("journal entry string length: %d" % len(journal_entry_string.split(",")))
            break
        else:
            # Entry is not the last in the csv.
            if journal_entry['start_loc']['SID'] + journal_entry['start_loc']['dir'] == csv_header[i]:
                # The entry for the start_loc matches the column header.
                journal_entry_string += "1,"
            else:
                # The entry for the start_loc does not match the column header.
                journal_entry_string += "0,"
    return journal_entry_string

def write_csv_delta_trip_miles(journal_entry_string_one, journal_entry_string_two):
    """
    write_csv_delta_trip_miles -Given two journal strings, computes the delta trip miles between the two and appends
        the change in mileage to the first journal entry string.
    :param journal_entry_string_one: A string to be written to the csv for distance prediction.
    :param journal_entry_string_two: A journal entry string to be written to the csv for distance prediction.
    :return journal_entry_string_one: The provided journal entry string with the appended change in mileage.
    """
    journal_one_entries = journal_entry_string_one.split(",")
    journal_one_trip_mileage = float(journal_one_entries[len(journal_one_entries) - 3])
    journal_two_entries = journal_entry_string_two.split(",")
    journal_two_trip_mileage = float(journal_two_entries[len(journal_two_entries) - 3])
    journal_entry_string_one += str(journal_two_trip_mileage - journal_one_trip_mileage) + ","
    return journal_entry_string_one

def write_csv_delta_days(journal_entry_string_one, journal_entry_string_two):
    """
    write_csv_delta_days -Given two journal strings, computes the elapsed number of days between journal entries and
        appends the change in days to the first journal entry string.
    :param journal_entry_string_one: A journal entry string to be written to the csv for distance prediction.
    :param journal_entry_string_two: A journal entry string to be written to the csv for distance prediction.
    :return journal_entry_string_one: The provided journal entry string with the appended change in days.
    """
    journal_one_entries = journal_entry_string_one.split(",")
    journal_one_date_string = journal_one_entries[len(journal_one_entries) - 3]
    journal_one_date = datetime.strptime(journal_one_date_string, "%A %B %d %Y")
    journal_two_entries = journal_entry_string_two.split(",")
    journal_two_date_string = journal_two_entries[len(journal_two_entries) - 3]
    journal_two_date = datetime.strptime(journal_two_date_string, "%A %B %d %Y")
    delta = journal_two_date - journal_one_date
    return delta.days

"""
write_to_csv -Writes the hiker data to CSV format at the specified storage_location in a form intended to be used
    by Pandas for Linear Regression Least Squares approximation.
:param valid_hikers: A dictionary containing the geocoded hiker locations.
:param valid_shelters: A dictionary containing the AT Shelters dataset.
:param storage_location_path: The location to write the created CSV to.
"""
def write_to_csv(valid_hikers, valid_shelters, storage_location_path):
    # Build the CSV header (the column header for LstSqr).
    csv_header = []
    csv_header.append("HID")
    csv_header.append("ENUM")
    num_shelter_cols = 0
    for sid, shelter in valid_shelters.items():
        # Append the ShelterID (SID) and the associated direction (North or South)
        csv_header.append(str(sid) + "N")
        csv_header.append(str(sid) + "S")
        num_shelter_cols += 2
    # Append a column header to keep track of the elapsed change in trip mileage between entries:
    csv_header.append("DTM")
    # Append a column header to keep track of the number of elapsed days between entries:
    csv_header.append("DD")
    # Append a column header to keep track of the miles/day between journal entries:
    csv_header.append("MPD")
    # Append a column header to serve as the regularization term:
    csv_header.append("bias")
    print("csv_header_len: %d" % len(csv_header))
    with open(storage_location_path + "/DistancePrediction.csv", 'w') as fp:
        # Write the CSV header to the output file.
        for i in range(len(csv_header)):
            if i != len(csv_header) - 1:
                fp.write(csv_header[i] + ",")
            else:
                fp.write(csv_header[i] + "\n")
    csv_journal_strings = []
    # Go through every hiker and create a row in the csv for each trail journal:
    for hid, hiker_info in valid_hikers.items():
        # Go through each journal entry and create an appropriate row in the CSV.
        for enum, entry in hiker_info['journal'].items():
            # Label journal entry start_loc shelter and direction of departure (e.g. 102S or 102N):
            journal_entry_string = str(hid) + "," + str(enum) + ","
            journal_entry_string = write_csv_shelter_entry(csv_header, journal_entry_string, enum, entry)
            # Append the total trip mileage to the csv entry string:
            journal_entry_string = journal_entry_string + str(entry['trip_mileage']) + ","
            # Append the date to the csv entry string:
            journal_entry_string = journal_entry_string + entry['date'].replace(",", "") + ","
            # Save the journal entry string:
            csv_journal_strings.append(journal_entry_string)
    # Iterate over pairs of journal strings computing delta information and storing in the first string:
    for journal_entry_string_one, journal_entry_string_two in zip(csv_journal_strings, csv_journal_strings[1:]):
        journal_entry_string_one += write_csv_delta_trip_miles(journal_entry_string_one, journal_entry_string_two)
        journal_entry_string_one += write_csv_delta_days(journal_entry_string_one, journal_entry_string_two)
        # journal_entry_string_one +=

def main(valid_shelters_path, valid_hikers_path, storage_location_path):
    valid_shelters = get_validated_shelters(validated_shelters_path=valid_shelters_path)
    valid_hikers = get_validated_hikers(validated_hikers_path=valid_hikers_path)
    write_to_csv(valid_hikers, valid_shelters, storage_location_path)
    csv_header = ""

if __name__ == '__main__':
    validated_shelter_data_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/TrailShelters/'))
    validated_hikers_data_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/VHDistancePrediction/'))
    csv_write_location_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/'))
    main(valid_shelters_path=validated_shelter_data_path, valid_hikers_path=validated_hikers_data_path,
         storage_location_path=csv_write_location_path)
