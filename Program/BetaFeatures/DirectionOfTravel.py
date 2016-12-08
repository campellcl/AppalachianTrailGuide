"""
DirectionOfTravel.py
TODO: Class Descriptor
:author: Chris Campell
:version: 11/23/2016
"""
__author__ = "Chris Campell"
__version__ = "11/23/2016"

import os
import json
from collections import OrderedDict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

def main(valid_hikers_path):
    valid_hikers = get_validated_hikers(validated_hikers_path=valid_hikers_path)
    # For each hiker determine if they are going northbound or southbound by summing the direction counts associated
    #   with each start_loc.
    for hid, hiker_info in valid_hikers.items():
        # If a direction was recorded from the website, we don't want it. Its not accurate.
        hiker_info['dir'] = None
        num_northbound_start_loc = 0
        num_southbound_start_loc = 0
        for enum, entry in hiker_info['journal'].items():
            if entry['start_loc']['dir'] == 'N':
                num_northbound_start_loc += 1
            elif entry['start_loc']['dir'] == 'S':
                num_southbound_start_loc += 1
        # Classify the hiker as northbound or southbound hiker based on the majority direction traveled:
        if num_northbound_start_loc > num_southbound_start_loc:
           valid_hikers[hid]['dir'] = "N"
        elif num_northbound_start_loc < num_southbound_start_loc:
            valid_hikers[hid]['dir'] = "S"
    # Tally the hikers
    num_northbound_hikers = 0
    num_southbound_hikers = 0
    for hid, hiker_info in valid_hikers.items():
        if hiker_info['dir'] == "N":
            num_northbound_hikers += 1
        elif hiker_info['dir'] == "S":
            num_southbound_hikers += 1
    print("Total Number of Hikers: %d" % len(valid_hikers))
    print("Number of Northbound Hikers: %d" %num_northbound_hikers)
    print("Number of Southbound Hikers: %d" %num_southbound_hikers)
    plt.title('Hiker Direction of Travel on the Appalachian Trail')
    labels = ['northbound', 'southbound']
    explode = (0, 0)
    colors = ['#488ec4', '#456fcc']
    fraction_of_northbound_hikers = (num_northbound_hikers * 100)/len(valid_hikers)
    fraction_of_southbound_hikers = (num_southbound_hikers * 100)/len(valid_hikers)
    print("fraction of northbound hikers: %d" % fraction_of_northbound_hikers)
    print("fraction of southbound hikers: %d" % fraction_of_southbound_hikers)
    fractions = [fraction_of_northbound_hikers, fraction_of_southbound_hikers]
    plt.pie(fractions, explode=explode, labels=labels, colors=colors, autopct="%1.1f%%")
    plt.axis('square')
    storage_loc = os.path.abspath(os.path.join(os.path.dirname(__file__), 'direction_of_travel.png'))
    plt.savefig(storage_loc)
if __name__ == '__main__':
     validated_hikers_data_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/VHDistancePrediction/'))
     main(valid_hikers_path=validated_hikers_data_path)
