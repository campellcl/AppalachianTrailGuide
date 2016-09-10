"""
HikerValidator.py
Handles the mapping between user entered text and GPS coordinates for shelters.
:Author: Chris Campell
:Version: 9/8/2016
"""

import os
import json
from fuzzywuzzy import fuzz
from collections import OrderedDict

class HikerValidator(object):
    """
    HikerValidator(object) -Wrapper for ShelterValidator, HostelValidator, and GeoValidator. Maps a hiker's entered
        locations to validated GPS coordinates in the appropriate data sets.
    :Author: Chris Campell
    :Version: 9/8/2016
    """

    """
    __init__ -Constructor for objects of type HikerValidator.
    :param validated_shelters: The AT_Shelters data set loaded into memory from json file.
    :param validated_hostels: The AT_Hostels data set loaded into memory from json file.
    :param validated_places: The AT_Places data set loaded into memory from json file.
    """
    def __init__(self, validated_shelters, validated_hostels, validated_places):
        self.validated_shelters = validated_shelters
        self.validated_hostels = validated_hostels
        self.validated_places = validated_places
        self.storage_location = "C:/Users/Chris/Documents/GitHub/AppalachianTrailGuide/Data"

    """
    validate_entry_locations -Takes a hiker journal entry and attempts to map the provided
        start_loc and dest to a validated shelter.
    :param unvalidated_start_loc: The user entered string for their starting location.
    :param unvalidated_dest: The user entered string for their destination location.
    :param comparison_threshold: The threshold for which a match is considered valid.
    """
    def validate_entry_locations(self, unvalidated_start_loc, unvalidated_dest, comparison_threshold=90):
        max_comp_ratio_usl = 0
        max_comp_ratio_ud = 0
        max_comp_sid_usl = 0
        max_comp_sid_ud = 0
        if unvalidated_start_loc is None:
            max_comp_sid_usl = None
        if unvalidated_dest is None:
            max_comp_sid_ud = None
        for shelter_id, shelter_data in self.validated_shelters.items():
            # Create a comparison ratio for the hiker's entered start_loc and the validated shelter's name.
            comparison_ratio_usl = fuzz.partial_ratio(unvalidated_start_loc, shelter_data['name'])
            # Create a comparison ratio for the hiker's entered destination and the validated shelter's name.
            comparison_ratio_ud = fuzz.partial_ratio(unvalidated_dest, shelter_data['name'])

            if comparison_ratio_usl >= max_comp_ratio_usl:
                max_comp_ratio_usl = comparison_ratio_usl
                max_comp_sid_usl = shelter_id
            if comparison_ratio_ud >= max_comp_ratio_ud:
                max_comp_ratio_ud = comparison_ratio_ud
                max_comp_sid_ud = shelter_id

            # Perform comparison threshold check.
            if max_comp_ratio_usl < comparison_threshold:
                max_comp_sid_usl = None
            if max_comp_ratio_ud < comparison_threshold:
                max_comp_sid_ud = None
        return (max_comp_sid_usl, max_comp_sid_ud)

    """
    validate_entry -Maps an unvalidated hiker's trail journal entry to a validated entry in one of the data sets.
    :param entry: An entry from the hiker's trail journal which is unmapped to a GPS location.
    :return entry: The same entry now mapped to a valid shelter object from one of the data sets.
    """
    def validate_entry(self, entry):
        start_loc_lookup_key, dest_lookup_key = self.validate_entry_locations(
            unvalidated_start_loc=entry['start_loc'], unvalidated_dest=entry['dest'], comparison_threshold=90)
        if start_loc_lookup_key is not None:
            entry['start_loc'] = {
                'shelter_name': self.validated_shelters[start_loc_lookup_key]['name'],
                'shelter_id': start_loc_lookup_key,
                'lat': self.validated_shelters[start_loc_lookup_key]['lat'],
                'lon': self.validated_shelters[start_loc_lookup_key]['lon'],
                'type': self.validated_shelters[start_loc_lookup_key]['type']
            }
        else:
            entry['start_loc'] = None
        if dest_lookup_key is not None:
            entry['dest'] = {
                'shelter_name': self.validated_shelters[dest_lookup_key]['name'],
                'shelter_id': dest_lookup_key,
                'lat': self.validated_shelters[dest_lookup_key]['lat'],
                'lon': self.validated_shelters[dest_lookup_key]['lon'],
                'type': self.validated_shelters[dest_lookup_key]['type']
            }
        else:
            entry['dest'] = None
        return entry

    """
    validate_shelters -Goes through the hiker's journal entries: geocoding each starting location and destination.
    :param hiker: The deserialized hiker object read from the json file.
    """
    def validate_shelters(self, hiker):
        statistics = {'val_ratio': None, 'succ': {}, 'fail': {}}
        unmapped_entries = []
        unvalidated_journal = hiker['journal']
        unmapped_start_loc = []
        unmapped_dest_loc = []
        for entry_num, entry in unvalidated_journal.items():
            geocoded_entry = self.validate_entry(entry)
            # TODO: Report statistics, names unmapped: {"shelter_1,shelter_2,shelter_3"}
            # if start_loc was not mapped correctly.
            if geocoded_entry['start_loc'] is None and geocoded_entry['dest'] is None:
                unmapped_entries.append(entry_num)
            else:
                hiker[entry_num] = geocoded_entry
        num_mapped = len(unvalidated_journal) - len(unmapped_entries)
        print("Hiker %s (%s)'s Geocoding Statistics: There were %d entries successfully mapped out of %d."
              %(hiker['identifier'], hiker['name'], num_mapped, len(unvalidated_journal)))

        print("\tUnmapped Shelters: {%s}" % unmapped_start_loc)
        # for unmapped_entry_num in unmapped_entries:
            # unmapped_start_loc.append(hiker['journal'][unmapped_entry_num]['start_loc'])
            # unmapped_dest_loc.append(hiker['journal'][unmapped_entry_num]['end_loc'])
        for unmapped_entry in unmapped_entries:
            del hiker['journal'][unmapped_entry]

    """
    write_validated_hiker -Writes a geocoded hiker to the specified storage directory in json format.
    :param hiker -The deserialized hiker object read from the json file and mapped.
    """
    def write_validated_hiker(self, hiker):
        validated_hikers_data_path = "C:/Users/Chris/Documents/GitHub/AppalachianTrailGuide/Data/HikerData/ValidatedHikers"
        hiker_id = hiker['identifier']
        with open(validated_hikers_data_path + "/" + str(hiker_id) + ".json", 'w') as fp:
            json.dump(hiker, fp=fp)

"""
get_validated_shelters -Returns a dictionary of the shelters validated using the combined TNL and ATC data sets.
@param validated_shelters_path -The path to the CSV file containing the validated shelters.
@return validated_shelters -A dictionary containing the geocoded shelters.
"""
def get_validated_shelters(validated_shelters_path):
    validated_shelters = {}
    line_num = 0
    with open(validated_shelters_path, 'r') as fp:
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
"""
def get_validated_hostels(validated_hostels_path):
    pass

"""
"""
def get_validated_places(validated_places_path):
    pass

"""
main -Main method for hiker validation. Goes through every unvalidated hiker and maps their location to an entry in the
    AT Shelters database.
"""
def main():
    unvalidated_hikers_data_path = "C:/Users/Chris/Documents/GitHub/AppalachianTrailGuide/Data/HikerData/UnvalidatedHikers/"
    validated_hikers_data_path = "C:/Users/Chris/Documents/GitHub/AppalachianTrailGuide/Data/HikerData/ValidatedHikers/"
    validated_shelter_data_path = "C:/Users/Chris/Documents/GitHub/AppalachianTrailGuide/Data/TrailShelters/"

    # Go through the list of unvalidated hikers and validate.
    for filename in os.listdir(unvalidated_hikers_data_path):
        if filename not in os.listdir(validated_hikers_data_path):
            # Load the unvalidated json file into memory.
            with open(unvalidated_hikers_data_path + "/" + filename, 'r') as fp:
                hiker = json.load(fp=fp)
            # Load the validated AT shelters into memory:
            validated_shelters = get_validated_shelters(validated_shelters_path=validated_shelter_data_path + "newShelters.csv")
            # TODO: Load validated hostels into memory:
            # validated_hostels = get_validated_hostels(validated_hostels_path=validated_shelter_data_path + "/validated_hostels.csv")
            # TODO: Load validated places (that are not recognized shelters or hostels) into memory:
            # validated_places = get_validated_places(validated_places_path=validated_shelter_data_path + "/validated_places.csv")

            # TODO: Validate using hostels, shelters, and places; not just shelters.
            # Instantiate validator object.
            validator = HikerValidator(validated_shelters=validated_shelters,
                                       validated_hostels=None, validated_places=None)
            # Execute shelter validation.
            validator.validate_shelters(hiker)
            # If there are any successfully mapped journal entries, write them to validated hikers.
            if len(hiker['journal']) > 0:
                validator.write_validated_hiker(hiker)
        else:
            print("Hiker %s Has Already ben Validated." % filename)

if __name__ == '__main__':
    main()
