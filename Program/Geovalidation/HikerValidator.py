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
import numpy as np
import copy

class HikerValidator(object):
    """
    HikerValidator(object) -Wrapper for ShelterValidator, HostelValidator, and GeoValidator. Maps a hiker's entered
        locations to validated GPS coordinates in the appropriate data sets.
    :Author: Chris Campell
    :Version: 9/8/2016
    """
    # TODO: Declare data structure to hold statistics for each hiker

    """
    __init__ -Constructor for objects of type HikerValidator.
    :param validated_shelters: The AT_Shelters data set loaded into memory from json file.
    :param validated_hostels: The AT_Hostels data set loaded into memory from json file.
    :param validated_places: The AT_Places data set loaded into memory from json file.
    :param statistics: A boolean flag; if True then statistics regarding the geocoding success of hiker's journals
        will be recorded.
    """
    def __init__(self, validated_shelters, validated_hostels, validated_places, statistics=False):
        self.validated_shelters = validated_shelters
        self.validated_hostels = validated_hostels
        self.validated_places = validated_places
        self.storage_location = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/'))
        self.stats = statistics
        if statistics:
            self.geocode_stats = {}

    """
    validate_entry_locations -Takes a hiker journal entry and attempts to map the provided
        start_loc and dest to a validated shelter in the AT Shelters data set.
    :param unvalidated_start_loc: The user entered string for their starting location.
    :param unvalidated_dest: The user entered string for their destination location.
    :param comparison_threshold: The threshold by which a match is considered valid during fuzzy string comparison.
    :returns (comp_ratios_usl, comp_ratios_ud): The top three fuzzy string comparisons greater than the
            comparsion_threshold for both start_location and destination.
        :return comp_ratios_usl: The top three matching shelter strings for start_location as determined by
                fuzzy string comparison.
        :return comp_ratios_ud: The top three matching shelter strings for destination as determined by
                fuzzy string comparison.
    """
    def validate_entry_locations(self, unvalidated_start_loc, unvalidated_dest, comparison_threshold=90):
        # Create a container to store the first second and third most likely shelter matches for the hiker's USL
        comp_ratios_usl = {'comp_threshold': comparison_threshold,
                           'first': {'assoc_sid': None, 's_name': None, 'comp_ratio': -1},
                           'second': {'assoc_sid': None, 's_name': None, 'comp_ratio': -1},
                           'third': {'assoc_sid': None, 's_name': None, 'comp_ratio': -1}}
        # Create a container to store the first, second, and third most likely shelter matches for the hiker's UD.
        comp_ratios_ud = {'comp_threshold': comparison_threshold,
                          'first': {'assoc_sid': None, 's_name': None, 'comp_ratio': -1},
                          'second': {'assoc_sid': None, 's_name': None, 'comp_ratio': -1},
                          'third': {'assoc_sid': None, 's_name': None, 'comp_ratio': -1}}

        # If the user didn't enter any text then there can be no geovalidation.
        # TODO: Make sure that the code still performs as expected if one or the other is null; not just both.
        if unvalidated_start_loc is None and unvalidated_dest is None:
            return (comp_ratios_usl, comp_ratios_ud)

        for shelter_id, shelter_data in self.validated_shelters.items():
            # Create a comparison ratio for the hiker's entered start_loc and the validated shelter's name.
            comparison_ratio_usl = fuzz.partial_ratio(unvalidated_start_loc, shelter_data['name'])
            # Create a comparison ratio for the hiker's entered destination and the validated shelter's name.
            comparison_ratio_ud = fuzz.partial_ratio(unvalidated_dest, shelter_data['name'])

            # Perform comparison threshold check:
            if comparison_ratio_usl >= comparison_threshold:
                # Iterate through the comparison ratios and find the right place to store the comparison ratio.
                if comparison_ratio_usl >= comp_ratios_usl['third']['comp_ratio']:
                    if comparison_ratio_usl >= comp_ratios_usl['second']['comp_ratio']:
                        if comparison_ratio_usl >= comp_ratios_usl['first']['comp_ratio']:
                            # Comparison ratio is the new first highest.
                            comp_ratios_usl['first']['assoc_sid'] = shelter_id
                            comp_ratios_usl['first']['s_name'] = shelter_data['name']
                            comp_ratios_usl['first']['comp_ratio'] = comparison_ratio_usl
                        else:
                            # Comparison ratio is the new second highest.
                            comp_ratios_usl['second']['assoc_sid'] = shelter_id
                            comp_ratios_usl['second']['s_name'] = shelter_data['name']
                            comp_ratios_usl['second']['comp_ratio'] = comparison_ratio_usl
                    else:
                        # Comparison ratio is the new third highest.
                        comp_ratios_usl['third']['assoc_sid'] = shelter_id
                        comp_ratios_usl['third']['s_name'] = shelter_data['name']
                        comp_ratios_usl['third']['comp_ratio'] = comparison_ratio_usl

            # Perform comparison threshold check:
            if comparison_ratio_ud >= comparison_threshold:
                # Iterate through the comparison ratios and find the right place to store entry.
                if comparison_ratio_ud >= comp_ratios_ud['third']['comp_ratio']:
                    if comparison_ratio_ud >= comp_ratios_ud['second']['comp_ratio']:
                        if comparison_ratio_ud >= comp_ratios_ud['first']['comp_ratio']:
                            # Comparison ratio is the new first highest.
                            comp_ratios_ud['first']['assoc_sid'] = shelter_id
                            comp_ratios_ud['first']['s_name'] = shelter_data['name']
                            comp_ratios_ud['first']['comp_ratio'] = comparison_ratio_ud
                        else:
                            # Comparison ratio is the new second highest.
                            comp_ratios_ud['second']['assoc_sid'] = shelter_id
                            comp_ratios_ud['second']['s_name'] = shelter_data['name']
                            comp_ratios_ud['second']['comp_ratio'] = comparison_ratio_ud
                    else:
                        # Comparison ratio is the new third highest.
                        comp_ratios_ud['third']['assoc_sid'] = shelter_id
                        comp_ratios_ud['third']['s_name'] = shelter_data['name']
                        comp_ratios_ud['third']['comp_ratio'] = comparison_ratio_ud
        return (comp_ratios_usl, comp_ratios_ud)

    """
    validate_entry -Maps an unvalidated hiker's trail journal entry to a validated entry in one of the data sets.
    :param user_start_loc: The start location from the trail journal entry to be mapped to a GPS location.
    :param user_dest_loc: The destination location from the trail journal entry to be mapped to a GPS location.
    :returns (validated_entry, comp_ratios_start_loc, comp_ratios_dest_loc):
        :return validated_entry: The now mapped/validated user_start_location and user_destination_location; returns
            None for key 'start_loc' if not mappable, and None for key 'dest' if not mappable.
        :return comp_ratios_start_loc: The top three results and their associated comparision ratios from the geocoding
            fuzzy string comparision process for the user's starting location.
        :return comp_ratios_dest_loc: The top three results and their associated comparision ratios fromt he geocoding
            fuzzy string comparison process for the user's destination location.
    """
    def validate_entry(self, user_start_loc, user_dest_loc):
        validated_entry = {}
        # Get the three best results for geocoded solutions for both start_loc and destination.
        comp_ratios_start_loc, comp_ratios_dest_loc = self.validate_entry_locations(
            unvalidated_start_loc=user_start_loc, unvalidated_dest=user_dest_loc, comparison_threshold=85)

        # Determine if geovalidation was successful for the start_location
        if comp_ratios_start_loc['first']['assoc_sid'] is not None:
            validated_entry['start_loc'] = {
                'shelter_name': comp_ratios_start_loc['first']['s_name'],
                'SID': comp_ratios_start_loc['first']['assoc_sid'],
                'lat': self.validated_shelters[comp_ratios_start_loc['first']['assoc_sid']]['lat'],
                'lon': self.validated_shelters[comp_ratios_start_loc['first']['assoc_sid']]['lon'],
                'type': self.validated_shelters[comp_ratios_start_loc['first']['assoc_sid']]['lon'],
            }
        else:
            # Geovalidation for the provided start_location was unsuccessful.
            validated_entry['start_loc'] = None

        # Determine if geovalidation was successful for the destination.
        if comp_ratios_dest_loc['first']['assoc_sid'] is not None:
            validated_entry['dest'] = {
                'shelter_name': comp_ratios_dest_loc['first']['s_name'],
                'SID': comp_ratios_dest_loc['first']['assoc_sid'],
                'lat': self.validated_shelters[comp_ratios_dest_loc['first']['assoc_sid']]['lat'],
                'lon': self.validated_shelters[comp_ratios_dest_loc['first']['assoc_sid']]['lon'],
                'type': self.validated_shelters[comp_ratios_dest_loc['first']['assoc_sid']]['type']
            }
        else:
            # Geovalidation for the provided dest_location was unsuccessful.
            validated_entry['dest'] = None
        return (validated_entry, comp_ratios_start_loc, comp_ratios_dest_loc)

    """
    validate_shelters -Goes through the hiker's journal entries: geocoding each starting location and destination. If
        the self.stats flag was set to true during object instantiation then record geocoding statistics.
    :param hiker: The deserialized hiker object read from the json file.
    """
    def validate_shelters(self, hiker):
        failed_mappings_start_loc = {}
        failed_mappings_dest_loc = {}
        unvalidated_journal = hiker['journal']
        validated_journal = {}

        for entry_num, entry in unvalidated_journal.items():
            validated_entry, comp_ratios_start_loc, comp_ratios_dest_loc = self.validate_entry(
                user_start_loc=entry['start_loc'], user_dest_loc=entry['dest'])

            validated_journal[entry_num] = copy.deepcopy(entry)
            if validated_entry['start_loc'] is None:
                # The user entered start_location could not be mapped.
                # TODO: Record any other information that may be pertinent to analyzing Fuzzy string comparison.
                failed_mappings_start_loc[entry_num] = {
                    'entry_num': entry_num,
                    'start_loc': entry['start_loc'],
                    'geo_stats': comp_ratios_start_loc
                }
                validated_journal[entry_num]['start_loc'] = None
            else:
                # The user entered start_location was mapped.
                validated_journal[entry_num]['start_loc'] = validated_entry['start_loc']

            if validated_entry['dest'] is None:
                # The user entered destination location could not be mapped.
                # TODO: Record any other information that may be pertinent to analyzing Fuzzy string comparison.
                failed_mappings_dest_loc[entry_num] = {
                    'entry_num': entry_num,
                    'dest': entry['dest'],
                    'geo_stats': comp_ratios_dest_loc
                }
                validated_journal[entry_num]['dest'] = None
            else:
                # The user entered destination location was mapped.
                validated_journal[entry_num]['dest'] = validated_entry['dest']

        if self.stats:
            # TODO: Compute additional hiker statistics.
            geocode_stats = {
                'hiker_id': hiker['identifier'],
                'USLS': failed_mappings_start_loc,
                'UDLS': validated_journal,
                'num_unvalidated': len(failed_mappings_start_loc) + len(failed_mappings_dest_loc),
                'num_validated': len(validated_journal),
            }
        else:
            geocode_stats = None
        return (validated_journal, geocode_stats)

    """
    write_validated_hiker -Writes a geocoded hiker to the specified storage directory in json format.
    :param hiker -The deserialized hiker object read from the json file and mapped.
    """
    def write_validated_hiker(self, hiker):
        validated_hikers_data_path = self.storage_location + "/HikerData/ValidatedHikers/"
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
def main(stats=False,num_hikers_to_map=None):
    unvalidated_hikers_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/UnvalidatedHikers/'))
    validated_hikers_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/ValidatedHikers/'))
    validated_shelter_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/TrailShelters/'))
    geocoding_stats = {}
    num_hikers = 0

    # Go through the list of unvalidated hikers and validate.
    for filename in os.listdir(unvalidated_hikers_data_path):
        if num_hikers_to_map:
            if num_hikers == num_hikers_to_map:
                break
        # If the hiker has already been validated, don't re-validate.
        if filename not in os.listdir(validated_hikers_data_path):
            # Load the unvalidated json file into memory.
            with open(unvalidated_hikers_data_path + "/" + filename, 'r') as fp:
                hiker = json.load(fp=fp)
            # Load the validated AT shelters into memory:
            validated_shelters = get_validated_shelters(validated_shelters_path=validated_shelter_data_path + "/newShelters.csv")
            # TODO: Load validated hostels into memory:
            # validated_hostels = get_validated_hostels(validated_hostels_path=validated_shelter_data_path + "/validated_hostels.csv")
            # TODO: Load validated places (that are not recognized shelters or hostels) into memory:
            # validated_places = get_validated_places(validated_places_path=validated_shelter_data_path + "/validated_places.csv")

            # TODO: Validate using hostels, shelters, and places; not just shelters.
            # Instantiate validator object.
            validator = HikerValidator(validated_shelters=validated_shelters,
                                       validated_hostels=None, validated_places=None, statistics=stats)
            # Execute shelter validation.
            validated_journal, geovalidation_stats = validator.validate_shelters(hiker)
            # If the statistics flag was set to true during instantiation, retrieve the computed statistics:
            if stats:
                geocoding_stats[hiker['identifier']] = geovalidation_stats
            # If there are any successfully mapped journal entries, write them to validated hikers.
            if len(validated_journal) > 0:
                validator.write_validated_hiker(hiker)
            num_hikers += 1
        else:
            print("Hiker %s Has Already ben Validated." % filename)

    # If geocoding statistics are requested then perform analysis
    if stats:
        print(geocoding_stats)

if __name__ == '__main__':
    stats = True
    num_hikers_to_map = 1
    main(stats=stats,num_hikers_to_map=num_hikers_to_map)
