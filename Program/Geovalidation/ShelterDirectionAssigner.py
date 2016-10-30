"""
ShelterDirectionAssigner.py
Goes through all hikers in the ValidatedHikers directory and assigns each shelter
    a direction of travel (northbound or southbound). The direction of travel is determined using the
    start_location of the following journal entry.
:Author: Chris Campell
:Version: 10/11/2016
"""

import os
import json
import math
from collections import OrderedDict

"""
assign_shelter_directions -Goes through every shelter in the hiker's validated trail journal and assigns a direction of
    travel. Each shelter has an associated direction of travel corresponding to the start_loc of the following entry.
    If the entry has no following entry, the direction is set to undetermined 'U'.
:param validated_hiker_trail_journal: The hiker's geovalidated trail journal.
:return validated_hiker_journal: The validated hiker journal with hiker direction now recorded for each shelter.
"""
def assign_shelter_directions(validated_hiker_journal):
    # print("hiker_journal_keys: %s" % validated_hiker_journal.keys())
    '''
    for enum1, enum2 in zip(list(validated_hiker_journal.keys())[0::2], list(validated_hiker_journal.keys())[1::2]):
        print("enum1: %s" % enum1)
        print("enum2: %s" % enum2)
    '''
    # The first shelter will have no associated direction of travel.
    first_enum = list(validated_hiker_journal.keys())[0]
    validated_hiker_journal[first_enum]['start_loc']['dir'] = "UD"
    for enum1, enum2 in zip(validated_hiker_journal.keys(), list(validated_hiker_journal.keys())[1:]):
        # print("enum1: %s" % enum1)
        # print("enum2: %s" % enum2)
        shelter_one = validated_hiker_journal[enum1]['start_loc']
        shelter_two = validated_hiker_journal[enum2]['start_loc']
        if int(shelter_two['SID']) < int(shelter_one['SID']):
            validated_hiker_journal[enum2]['start_loc']['dir'] = "S"
        elif int(shelter_two['SID']) > int(shelter_one['SID']):
            validated_hiker_journal[enum2]['start_loc']['dir'] = "N"
        elif int(shelter_two['SID']) == int(shelter_one['SID']):
            validated_hiker_journal[enum2]['start_loc']['dir'] = "UD"
        else:
            print("Cardinal Direction Between SID #%d and SID #%d was incalculable!"
                  % (shelter_one['SID'], shelter_two['SID']))
    return validated_hiker_journal

"""
sort_hiker_journal -Sorts a hiker journal chronologically by entry number.
:param hiker_journal: The hiker journal to be sorted chronologically by entry number.
:return sorted_hiker_journal: The original hiker journal now sorted chronologically by entry number.
"""
def sort_hiker_journal(hiker_journal):
    keys = [int(key) for key in hiker_journal.keys()]
    sorted_keys = sorted(keys)
    sorted_hiker_journal = OrderedDict()
    for key in sorted_keys:
        sorted_hiker_journal[str(key)] = hiker_journal[str(key)]
    return sorted_hiker_journal

"""
clean_hiker_journal -Takes a geo-validated and sorted (chronologically by entry number) hiker trail journal, and removes
    any entries with unvalidated start_locations. After cleaning, only journal entries with a geo-validated start_loc
    remain.
:param sorted_hiker_journal: A geo-validated and sorted (chronologically by entry number) hiker trail journal
    to be cleaned.
:return cleaned_hiker_journal: The same hiker journal as provided, with entries containing
    non-validated start_locations removed.
"""
def clean_hiker_journal(sorted_hiker_journal):
    cleaned_hiker_journal = OrderedDict()
    for enum, entry in sorted_hiker_journal.items():
        if not entry['start_loc']:
            pass
        else:
            if not entry['start_loc'] == "None":
                cleaned_hiker_journal[enum] = entry
    return cleaned_hiker_journal

"""
main -Main method for ShelterDirectionAssigner, goes through every validated hiker and retrieves only the
    journal entries with valid starting locations. Those journal entries are assigned a direction of travel.
"""
def main():
    validated_hikers_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/ValidatedHikers/'))
    validated_hikers_with_directions_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/VHDistancePrediction/'))
    # Go through the list of validated hikers.
    for filename in os.listdir(validated_hikers_data_path):
        # If the hiker has already been assigned directions, don't re-assign.
        if filename not in os.listdir(validated_hikers_with_directions_data_path):
            with open(validated_hikers_data_path + "/" + filename, 'r') as fp:
                hiker = json.load(fp=fp)
                # Sort the geo-validated hiker journal chronologically by entry number:
                sorted_hiker_journal = sort_hiker_journal(hiker['journal'])
                # For the sake of distance predictions, remove any journal entries that contain no valid start location:
                cleaned_hiker_journal = clean_hiker_journal(sorted_hiker_journal)
                # Ensure that there is at least two shelters in the cleaned journal, else discard the hiker as we can't determine the direction.
                if cleaned_hiker_journal:
                    # Assign direction of travel to each shelter:
                    updated_hiker_journal = assign_shelter_directions(cleaned_hiker_journal)
                    # Updated the hiker's journal
                    hiker['journal'] = updated_hiker_journal
                    # Delete the direction associated with the hiker (it is now associated with the shelter).
                    try:
                       dir = hiker['dir']
                       del hiker['dir']
                    except KeyError:
                        pass
                    # Write the updated journal to the ATG/Data/HikerData/VHDistancePrediction directory:
                    storage_location = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/VHDistancePrediction/'))
                    with open(storage_location + "/" + filename, 'w') as fp2:
                        json.dump(hiker, fp=fp2)

if __name__ == '__main__':
    main()
