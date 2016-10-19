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
calculate_initial_compass_bearing -Calculates the bearing between two points.
The formulae used is the following:
    θ = atan2(sin(Δlong).cos(lat2),
              cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
:Parameters:
  - `pointA: The tuple representing the latitude/longitude for the
    first point. Latitude and longitude must be in decimal degrees
  - `pointB: The tuple representing the latitude/longitude for the
    second point. Latitude and longitude must be in decimal degrees
:Returns:
  The bearing in degrees
:Returns Type:
  float
@Author: jeromer
@Source: https://gist.github.com/jeromer/2005586
"""
def calculate_initial_compass_bearing(pointA, pointB):
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")
    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])
    diffLong = math.radians(pointB[1] - pointA[1])
    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))
    initial_bearing = math.atan2(x, y)
    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return compass_bearing

"""
determine_cardinal_direction -Given a compass bearing, returns the cardinal direction associated with that bearing.
@param compass_bearing -The initial compass bearing between two validated shelters.
@return cardinal_dir -The cardinal direction of the compass rose associated with the provided compass bearing.
"""
def determine_cardinal_direction(compass_bearing):
    if compass_bearing >= 0 and compass_bearing < 45:
        return 'North'
    elif compass_bearing >= 45 and compass_bearing < 90:
        return 'Northeast'
    elif compass_bearing >= 90 and compass_bearing < 135:
        return 'East'
    elif compass_bearing >= 135 and compass_bearing < 180:
        return 'Southeast'
    elif compass_bearing >= 180 and compass_bearing < 225:
        return 'South'
    elif compass_bearing >= 225 and compass_bearing < 270:
        return 'Southwest'
    elif compass_bearing >= 270 and compass_bearing < 315:
        return 'West'
    elif compass_bearing >= 315 and compass_bearing < 360:
        return 'Northwest'
    elif compass_bearing == 360:
        return 'North'

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
    for enum1, enum2 in zip(validated_hiker_journal.keys(),list(validated_hiker_journal.keys())[1:]):
        # print("enum1: %s" % enum1)
        # print("enum2: %s" % enum2)
        shelter_one = validated_hiker_journal[enum1]['start_loc']
        shelter_two = validated_hiker_journal[enum2]['start_loc']
        start_coordinate = (shelter_one['lat'], shelter_one['lon'])
        end_coordinate = (shelter_two['lat'], shelter_two['lon'])
        compass_bearing = calculate_initial_compass_bearing(start_coordinate, end_coordinate)
        cardinal_direction = determine_cardinal_direction(compass_bearing=compass_bearing)
        # TODO: modify hiker_id #10's second entry should be NorthWest not West.
        if cardinal_direction:
            if "North" in cardinal_direction:
                validated_hiker_journal[enum1]['start_loc']['dir'] = "N"
            elif "South" in cardinal_direction:
                validated_hiker_journal[enum1]['start_loc']['dir'] = "S"
            else:
                validated_hiker_journal[enum1]['start_loc']['dir'] = "UK"
        else:
            print("Cardinal Direction Between SID #%d and SID #%d was incalculable!"
                  % (shelter_one['SID'], shelter_two['SID']))
    return validated_hiker_journal

"""
update_hiker -Updates the hiker's json file with the newly generated
    hiker journal (complete with hiker direction for each shelter).
:param outdated_file_pointer: A reference to the hiker's json file still open in memory.
    The file pointer needs to be closed before the hiker's json file can be overwritten.
:param filename: The path to the hiker's outdated json file.
:param outdated_hiker: The outdated hiker object in memory.
:param updated_journal: The revised hiker journal, which now contains a direction of
    travel associated with each journal entry.
"""
def update_hiker(outdated_file_pointer, filename, outdated_hiker, updated_journal):
    # Close the file pointer so the file can be deleted and re-created:
    outdated_file_pointer.close()
    # Remove the file from the hard-drive:
    os.remove(filename)
    # Update the hiker with the new journal:
    outdated_hiker['journal'] = updated_journal
    # Delete the direction associated with the hiker (it is now associated with the shelter).
    if outdated_hiker['dir']:
        del outdated_hiker['dir']
    # Recreate the file with the updated data:
    with open(filename, 'w') as fp:
        json.dump(fp=outdated_hiker)

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
    # Go through the list of validated hikers.
    for filename in os.listdir(validated_hikers_data_path):
        with open(validated_hikers_data_path + "/" + filename, 'r') as fp:
            hiker = json.load(fp=fp)
            # Sort the geo-validated hiker journal chronologically by entry number:
            sorted_hiker_journal = sort_hiker_journal(hiker['journal'])
            # For the sake of distance predictions, remove any journal entries that contain no valid start location:
            cleaned_hiker_journal = clean_hiker_journal(sorted_hiker_journal)
            # Assign direction of travel to each shelter:
            updated_hiker_journal = assign_shelter_directions(cleaned_hiker_journal)
            # Updated the hiker's journal
            hiker['journal'] = updated_hiker_journal
            # Write the updated journal to the ATG/Data/HikerData/VHDistancePrediction directory:
            storage_location = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/VHDistancePrediction/'))
            with open(storage_location + "/" + filename, 'w') as fp2:
                json.dump(hiker, fp=fp2)
            '''
            update_hiker(outdated_file_pointer=fp, filename=(validated_hikers_data_path + "/" + filename),
                         outdated_hiker=hiker, updated_journal=updated_hiker_journal)
            '''

if __name__ == '__main__':
    main()
