"""
HikerDataToCSV.py
Takes all validated hikers and writes them to CSV format for use in Pandas.
__author__ = Chris Campell
__version__ = 9/29/2016
"""
import os
import json

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
    validated_shelters = {}
    line_num = 0
    with open(validated_shelters_path + "/newShelters.csv", 'r') as fp:
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
    num_shelter_cols = 0
    for sid, shelter in valid_shelters.items():
        # Append the ShelterID (SID) and the associated direction (North or South)
        csv_header.append(str(sid) + "N")
        csv_header.append(str(sid) + "S")
        num_shelter_cols += 2
    csv_header.append("bias")
    print("csv_header_len: %d" % len(csv_header))
    with open(storage_location_path + "/DistancePrediction.csv", 'w') as fp:
        # Write the CSV header to the output file.
        for i in range(len(csv_header)):
            if i != len(csv_header) - 1:
                fp.write(csv_header[i] + ",")
            else:
                fp.write(csv_header[i] + "\n")
        # Populate teh CSV with hiker data:
        # Go through every hiker and extract each journal; filling in the csv as appropriate.
        for hid, hiker_info in valid_hikers.items():
            # Go through every hikers journal; extracting each journal entry.
            journal_string = ""
            journal_string += str(hid) + ","
            for enum, entry in hiker_info.items():
                entry_string = journal_string
                # For each journal entry, we only care about the start_location and its associated shelter.
                if entry['start_loc'] is not None:
                    # The journal entry had a successfully mapped start_location. Now populate the CSV for this entry.
                    # TODO: Need to modify the validated_hiker to also hold on to hiker's information
                    for i in range(len(csv_header)):
                        if i == len(csv_header) - 1:
                            # Entry is the last in the csv.
                            if entry['start_loc']['SID'] + "N" == csv_header[i]:
                                # The entry for the start_loc matches the column header.
                                entry_string += "1\n"
                            elif entry['start_loc']['SID'] + "S" == csv_header[i]:
                                # The entry for the start_loc matches the column header.
                                entry_string += "1\n"
                            else:
                                # The entry for the start_loc does not match the column header.
                                entry_string += "0\n"
                            print("journal entry string length: %d" % len(entry_string.split(",")))
                            fp.write(entry_string)
                        else:
                            # Entry is not the last in the csv.
                            if entry['start_loc']['SID'] + "N" == csv_header[i]:
                                # The entry for the start_loc matches the column header.
                                entry_string += "1,"
                            elif entry['start_loc']['SID'] + "S" == csv_header[i]:
                                # The entry for the start_loc matches the column header.
                                entry_string += "1,"
                            else:
                                # The entry for the start_loc does not match the column header.
                                entry_string += "0,"
                else:
                    # If the start_loc was not mapped and the destination was, we don't care.
                    pass

def main(valid_shelters_path, valid_hikers_path, storage_location_path):
    valid_shelters = get_validated_shelters(validated_shelters_path=valid_shelters_path)
    valid_hikers = get_validated_hikers(validated_hikers_path=valid_hikers_path)
    write_to_csv(valid_hikers, valid_shelters, storage_location_path)
    csv_header = ""


if __name__ == '__main__':
    validated_shelter_data_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/TrailShelters/'))
    validated_hikers_data_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/ValidatedHikers/'))
    csv_write_location_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/'))
    main(valid_shelters_path=validated_shelter_data_path, valid_hikers_path=validated_hikers_data_path,
         storage_location_path=csv_write_location_path)

