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

def get_csv_ending_header():
    """
    get_csv_ending_header - Returns a list composed of user specific information flags to be used in the csv header.
    :return csv_ending_header: A list ready to be used as a section of the csv header once delimited by commas.
    """
    csv_ending_header = []
    # Append a column header to keep track of the total mileage of the current entry:
    csv_ending_header.append("TM")
    # Append a column header to keep track of the date of the current entry:
    csv_ending_header.append("Date")
    # Append a column header to keep track of the elapsed change in trip mileage between entries:
    csv_ending_header.append("DTM")
    # Append a column header to keep track of the number of elapsed days between entries:
    csv_ending_header.append("DD")
    # Append a column header to keep track of the miles/day between journal entries:
    csv_ending_header.append("MPD")
    # Append a column header to keep track of the user's bias in relation to the average:
    csv_ending_header.append("UB")
    # Append a column header to serve as the regularization term:
    csv_ending_header.append("bias")
    return csv_ending_header

def get_csv_shelter_header(valid_shelters):
    """
    get_csv_shelter_header - Returns a list composed of shelters' SID + dir; to be used in the CSV header.
    :param valid_shelters: The dictionary of validated shelters read into memory from the appropriate file.
    :return csv_shelter_header: A list ready to be used as a section of the csv header once delimited by commas and
        appended with a newline character '\n'.
    """
    csv_shelter_header = []
    for sid, shelter in valid_shelters.items():
        # Append the ShelterID (SID) and the associated direction (North or South)
        csv_shelter_header.append(str(sid) + "N")
        csv_shelter_header.append(str(sid) + "S")
    return csv_shelter_header

def get_csv_header(csv_shelter_header, csv_ending_header):
    """
    get_csv_header - Returns a list representing the entire CSV header to be written to csv.
    :param csv_shelter_header: A list composed of shelters and directions to be used in the csv header.
    :param csv_ending_header: A list composed of user specific information obtained over several entries, to be used in
        the csv header.
    :return csv_header: A list ready to be used as the csv header once delimited by commas and appended with a
        newline character '\n'.
    """
    csv_header = []
    csv_header.append("HID")
    csv_header.append("ENUM")
    for col_header in csv_shelter_header:
        csv_header.append(col_header)
    for col_header in csv_ending_header:
        csv_header.append(col_header)
    return csv_header

def write_csv_header(csv_shelter_header, csv_ending_header, storage_location_path):
    """
    write_csv_header - Writes the csv header to DistancePrediction.csv in the specified storage directory.
    :param csv_shelter_header: The section of the csv header containing shelters.
    :param csv_ending_header: The section of the csv header containing delta information.
    :param storage_location_path: The location to write the output file 'DistancePrediction.csv'
    :return: Upon completion, the file DistancePrediction.csv will be written to the specified storage directory;
        populated with the CSV header.
    """
    csv_header = get_csv_header(csv_shelter_header, csv_ending_header)
    # print("csv_header_len: %d" % len(csv_header))
    with open(storage_location_path + "/DistancePrediction.csv", 'w') as fp:
        # Write the CSV header to the output file.
        for i in range(len(csv_header)):
            if i != len(csv_header) - 1:
                fp.write(csv_header[i] + ",")
            else:
                fp.write(csv_header[i] + "\n")

def get_user_bias(hiker_string_dict, avg_hiker_delta_mileage):
    """
    get_user_bias -Computes a bias for the user representing how far above or below the average hiker they are. This is
        computed by averaging the hiker's daily mileage across all valid start_locations in comparison to the average
        hiker.
    :param hiker_strings: The
    :param avg_hiker_delta_mileage:
    :return:
    """
    return user_bias

def get_csv_shelter_string(csv_shelter_header, start_loc):
    """
    get_csv_shelter_string -Returns a shelter string for encoding to CSV. The string is of the form SID1N, SID1S, ...
    :param csv_shelter_header:
    :param start_loc:
    :return hiker_shelter_string:
    """
    hiker_shelter_string = ""
    for i in range(len(csv_shelter_header)):
        if start_loc['SID'] + start_loc['dir'] == csv_shelter_header[i]:
            # The entry for the start_loc matches the column header.
            hiker_shelter_string += "1,"
        else:
            # The entry for the start_loc does not match the column header.
            hiker_shelter_string += "0,"
    return hiker_shelter_string

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


def get_average_miles_per_day(hiker_strings_dict):
    """
    get_average_miles_per_day - Returns the average change in mileage per day for all recorded hikers.
    :param hiker_strings_dict: A dictionary containing information between entries for each hiker.
    :return average_miles_per_day: The average number of miles-per-day for all recorded hikers.
    """
    num_entries = 0
    total_miles_per_day = 0
    i = 0
    for hid, hiker_string_info in hiker_strings_dict.items():
        if i == 0:
            pass
        else:
            for enum, delta_info in hiker_string_info['journal_strings'].items():
                num_entries += 1
                total_miles_per_day += delta_info['miles_per_day']
        i += 1
    average_miles_per_day = total_miles_per_day / num_entries
    return average_miles_per_day


def get_hiker_average_miles_per_day(hiker_strings_entry):
    total_num_entries = len(list(hiker_strings_entry.keys()))
    total_miles_per_day = 0
    for enum, delta_info in hiker_strings_entry.items():
        total_miles_per_day += delta_info['miles_per_day']
    hiker_average_miles_per_day = total_miles_per_day / total_num_entries
    return hiker_average_miles_per_day


def get_miles_per_day(journal_entry_one, journal_entry_two):
    delta_trip_miles = get_delta_trip_miles(journal_entry_one, journal_entry_two)
    delta_days = get_delta_days(journal_entry_one, journal_entry_two)
    if delta_days != 0:
        miles_per_day = delta_trip_miles / delta_days
    else:
        miles_per_day = 0
    return miles_per_day

def build_hiker_strings_for_csv(valid_hikers, valid_shelters):
    """
    build_hiker_strings_for_csv -TODO: method descriptor.
    :param valid_hikers: TODO: waka flaka
    :param valid_shelters: TODO: waka flaka
    :return:
    """
    hiker_strings = OrderedDict()
    hiker_strings['avg_miles_per_day'] = None
    for hid, hiker_info in valid_hikers.items():
        hiker_strings[hid] = {'computed_info': {'user_bias': None, 'hiker_avg_miles_per_day': None}}
        hiker_strings[hid]['journal_strings'] = OrderedDict()
        # Sort the hiker's journal chronologically:
        sorted_hiker_journal_keys = sorted([int(enum) for enum in hiker_info['journal'].keys()])
        for enum1, enum2 in zip(sorted_hiker_journal_keys, sorted_hiker_journal_keys[1:]):
            first_entry = hiker_info['journal'][str(enum1)]
            second_entry = hiker_info['journal'][str(enum2)]
            hiker_strings[hid]['journal_strings'][enum1] = {
                'trip_mileage': first_entry['trip_mileage'],
                'date': first_entry['date'].replace(",", ""),
                'delta_mileage': get_delta_trip_miles(first_entry, second_entry),
                'delta_days': get_delta_days(first_entry, second_entry),
                'miles_per_day': get_miles_per_day(first_entry, second_entry),
                'bias': 1,
                'identifying_string': str(hid) + "," + str(enum1) + ",",
                'shelter_string': get_csv_shelter_string(get_csv_shelter_header(valid_shelters), first_entry['start_loc']),
                'delta_string': ""
            }
            hiker_strings[hid]['journal_strings'][enum1]['delta_string'] = \
                str(hiker_strings[hid]['journal_strings'][enum1]['trip_mileage']) + "," \
                + hiker_strings[hid]['journal_strings'][enum1]['date'] + "," \
                + str(hiker_strings[hid]['journal_strings'][enum1]['delta_mileage']) + "," \
                + str(hiker_strings[hid]['journal_strings'][enum1]['delta_days']) + "," \
                + str(hiker_strings[hid]['journal_strings'][enum1]['miles_per_day']) + ","
        # Now that all journal entries and associated pairwise delta info. is logged, compute hiker stats:
        hiker_strings[hid]['computed_info']['hiker_avg_miles_per_day'] = get_hiker_average_miles_per_day(hiker_strings[hid]['journal_strings'])
    # Now that all hiker dictionaries are built, iterate through hiker strings and compute average delta miles:
    hiker_strings['avg_miles_per_day'] = get_average_miles_per_day(hiker_strings)
    # Calculate the user bias and append to hiker dictionaries:
    i = 0
    for hid, hiker_info in hiker_strings.items():
        if i == 0:
            pass
        else:
            user_bias = hiker_info['computed_info']['hiker_avg_miles_per_day'] - hiker_strings['avg_miles_per_day']
            hiker_strings[hid]['computed_info']['user_bias'] = user_bias
            for enum, delta_info in hiker_info['journal_strings'].items():
                delta_string = delta_info['delta_string']
                hiker_strings[hid]['journal_strings'][enum]['delta_string'] = delta_string + str(user_bias) + ",1\n"
        i += 1
    return hiker_strings

"""
write_to_csv -Writes the hiker data to CSV format at the specified storage_location in a form intended to be used
    by Pandas for Linear Regression Least Squares approximation.
:param valid_hikers: A dictionary containing the geocoded hiker locations.
:param valid_shelters: A dictionary containing the AT Shelters dataset.
:param storage_location_path: The location to write the created CSV to.
"""
def write_to_csv(valid_hikers, valid_shelters, storage_location_path):
    # Build the CSV header (the column header for LstSqr):
    csv_header = get_csv_header(valid_shelters, storage_location_path)
    hiker_strings = build_hiker_strings_for_csv(valid_hikers, valid_shelters)
    # TODO: Write information populated in hiker_strings to csv.
    csv_shelter_header = get_csv_shelter_header(valid_shelters)
    csv_ending_header = get_csv_ending_header()
    csv_header = get_csv_header(csv_shelter_header, csv_ending_header)
    with open(storage_location_path + "/DistancePrediction.csv", 'a') as fp:
        for i in range(len(csv_header)):
            if i != len(csv_header) - 1:
                fp.write(csv_header[i] + ",")
            else:
                fp.write(csv_header[i] + "\n")
        i = 0
        for hid, hiker_strings in hiker_strings.items():
            hiker_string = ""
            if i != 0:
                for enum, journal_strings in hiker_strings['journal_strings'].items():
                    hiker_string += journal_strings['identifying_string']
                    hiker_string += journal_strings['shelter_string']
                    hiker_string += journal_strings['delta_string']
                fp.write(hiker_string)
            i += 1

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
