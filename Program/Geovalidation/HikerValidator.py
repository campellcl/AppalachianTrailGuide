"""
HikerValidator.py
Handles the mapping between user entered text and GPS coordinates for shelters.
:Author: Chris Campell
:Version: 9/1/2016
"""

import os
import json

class HikerValidator(object):
    """
    HikerValidator(object) -Wrapper for ShelterValidator, HostelValidator, and GeoValidator. Maps a hiker's entered
        locations to validated GPS coordinates in the appropriate data sets.
    :Author: Chris Campell
    :Version: 7/22/2016
    """

    """
    __init__ -Constructor for objects of type HikerValidator.
    :param validated_shelters: The AT_Shelters dataset loaded into memory from json file.
    :param validated_hostels: The AT_Hostels data set loaded into memory from json file.
    :param validated_places: The AT_Places data set loaded into memory from json file.
    """
    def __init__(self, validated_shelters, validated_hostels, validated_places):
        self.validated_shelters = validated_shelters
        self.validated_hostels = validated_hostels
        self.validated_places = validated_places
        self.storage_location = "C:/Users/Chris/Documents/GitHub/ATS/Data"

    """
    validate_start_loc -Maps the unvalidated hiker['start_loc'] to a valid location in the AT_Shelters data set. Returns
        the unique identifier (lookup key) for the mapped shelter in the validated_shelters dictionary.
    :param unvalidated_start_loc: The un-mapped string the hiker entered online for the starting location field.
    :return shelter_name: The unique identifier (lookup key) for the mapped shelter in the
        validated_shelters dictionary.
    """
    def validate_start_loc(self, unvalidated_start_loc):
        # TODO: Rewrite this method to return shelter_id instead of shelter_name.
        if unvalidated_start_loc is None:
            return None
        unvalidated_start_loc = str.lower(unvalidated_start_loc)
        # print("Mapping Start Location: %s..." % unvalidated_start_loc)
        for shelter_name, entry in self.validated_shelters.items():
            shelter_name = str.lower(shelter_name)
            # TODO: Fuzzy string comparison.
            if unvalidated_start_loc == shelter_name:
                # print("Success! Start Location: %s Mapped to Lookup Key: %s" % (unvalidated_start_loc, shelter_name))
                return shelter_name
        # print("Failure. Start Location: %s was unable to be mapped to a shelter dictionary lookup key." % unvalidated_start_loc)
        return None

    """
    validate_dest -Maps the unvalidated hiker['dest'] to a valid location in the AT_Shelters data set. Returns the
        unique identifier (lookup key) for the mapped shelter in the validated_shelters dictionary.
    :param unvalidated_destination: The un-mapped string the hiker entered online for the destination field.
    :return shelter_name: The unique identifier (lookup key) for the mapped shelter in the
        validated_shelters dictionary.
    """
    def validate_dest(self, unvalidated_destination):
        # TODO: Rewrite this method to return shelter_id instead of shelter_name.
        if unvalidated_destination is None:
            return None
        unvalidated_dest = str.lower(unvalidated_destination)
        # print("Mapping Destination Location: %s..." % unvalidated_dest)
        for shelter_name, entry in self.validated_shelters.items():
            shelter_name = str.lower(shelter_name)
            # TODO: Fuzzy string comparison.
            if unvalidated_dest == shelter_name:
                # print("Success! Destination: %s Mapped to Lookup Key: %s" % (unvalidated_dest, shelter_name))
                return shelter_name
        # print("Failure. Destination: %s was unable to be mapped to a shelter dictionary lookup key." % unvalidated_dest)
        return None

    """
    validate_entry -Maps an unvalidated hiker's trail journal entry to a validated entry in one of the data sets.
    :param entry: An entry from the hiker's trail journal which is unmapped to a GPS location.
    :return entry: The same entry now mapped to a valid shelter object from one of the data sets.
    """
    def validate_entry(self, entry):
        start_loc_lookup_key = self.validate_start_loc(entry['start_loc'])
        dest_lookup_key = self.validate_dest(entry['dest'])
        if start_loc_lookup_key is not None:
            entry['start_loc'] = {
                'shelter_name': start_loc_lookup_key,
                'shelter_id': self.validated_shelters[start_loc_lookup_key]['id'],
                'lat': self.validated_shelters[start_loc_lookup_key]['lat'],
                'lon': self.validated_shelters[start_loc_lookup_key]['lon'],
                'type': self.validated_shelters[start_loc_lookup_key]['type']
            }
        else:
            entry['start_loc'] = None
        if dest_lookup_key is not None:
            entry['dest'] = {
                'shelter_name': dest_lookup_key,
                'shelter_id': self.validated_shelters[dest_lookup_key]['id'],
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
        unmapped_entries = []
        unvalidated_journal = hiker['journal']
        for entry_num, entry in unvalidated_journal.items():
            geocoded_entry = self.validate_entry(entry)
            if geocoded_entry['start_loc'] is None and geocoded_entry['dest'] is None:
                unmapped_entries.append(entry_num)
            else:
                hiker[entry_num] = geocoded_entry
        num_mapped = len(unvalidated_journal) - len(unmapped_entries)
        print("Hiker %s (%s)'s Geocoding Statistics: There were %d entries successfully mapped out of %d." %(hiker['identifier'], hiker['name'], num_mapped, len(unvalidated_journal)))
        for unmapped_entry in unmapped_entries:
            del hiker['journal'][unmapped_entry]

    """
    write_validated_hiker -Writes a geocoded hiker to the specified storage directory in json format.
    :param hiker -The deserialized hiker object read from the json file and mapped.
    """
    def write_validated_hiker(self, hiker):
        validated_hikers_data_path = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data/Validated_Hikers"
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
                shelter_name = split_string[0]
                shelter_id = split_string[1]
                data_set = split_string[2]
                lat = float(split_string[3])
                lon = float(split_string[4])
                type = split_string[5]
                validated_shelters[str.lower(shelter_name)] = {
                    'id': shelter_id, 'num': 0, 'dataset': data_set,
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
    unvalidated_hikers_data_path = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data/UnvalidatedHikers/"
    validated_hikers_data_path = "C:/Users/Chris/Documents/GitHub/ATS/Data/Hiker_Data/ValidatedHikers/"
    validated_shelter_data_path = "C:/Users/Chris/Documents/GitHub/ATS/Data/Shelter_Data"

    # Go through the list of unvalidated hikers and validate.
    for filename in os.listdir(unvalidated_hikers_data_path):
        if filename not in os.listdir(validated_hikers_data_path):
            # Load the unvalidated json file into memory.
            with open(unvalidated_hikers_data_path + "/" + filename, 'r') as fp:
                hiker = json.load(fp=fp)
            # Load the validated AT shelters into memory:
            validated_shelters = get_validated_shelters(validated_shelters_path=validated_shelter_data_path + "validated_shelters.csv")
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
            # If there are any
            if len(hiker['journal']) > 0:
                validator.write_validated_hiker(hiker)
        else:
            print("Hiker %s Has Already ben Validated." % filename)

if __name__ == '__main__':
    main()
