"""
AverageNumberOfDays.py
TODO: Class Descriptor.
:author: Chris Campell
:version: 11/23/2016
"""

__author__ = "Chris Campell"
__version__ = "11/23/2016"

import os
import json
from collections import OrderedDict
from datetime import datetime
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

def get_validated_thru_hikers(validated_hikers):
    """
    get_validated_thru_hikers - Returns the hiker objects with over 2,000 miles logged.
    :param validated_hikers: The dictionary of hikers with successfully mapped start locations.
    :return thru_hikers: A list of hikers who's total mileage was >= 2,000.
    """
    thru_hikers = OrderedDict()
    for hid, hiker_info in validated_hikers.items():
        for enum, entry in hiker_info['journal'].items():
            if entry['trip_mileage'] >= 2000:
                thru_hikers[hid] = hiker_info
    return thru_hikers

def get_southbound_hikers(validated_hikers):
    """
    get_southbound_hikers - Returns the hiker objects whose primary direction of travel is southbound.
    :param validated_hikers: The list of validated hikers read into memory by get_validated_hikers.
    :return southbound_hikers: The list of southbound hikers.
    """
    southbound_hikers = OrderedDict()
    for hid, hiker_info in validated_hikers.items():
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
           validated_hikers[hid]['dir'] = "N"
        elif num_northbound_start_loc < num_southbound_start_loc:
            validated_hikers[hid]['dir'] = "S"
            southbound_hikers[hid] = hiker_info
    return southbound_hikers

def get_northbound_hikers(validated_hikers):
    """
    get_northbound_hikers - Returns the hiker objects whose primary direction of travel is northbound.
    :param validated_hikers: The list of validated hikers read into memory by get_validated_hikers.
    :return northbound_hikers: The list of northbound hikers.
    """
    northbound_hikers = OrderedDict()
    for hid, hiker_info in validated_hikers.items():
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
           validated_hikers[hid]['dir'] = "N"
           northbound_hikers[hid] = hiker_info
        elif num_northbound_start_loc < num_southbound_start_loc:
            validated_hikers[hid]['dir'] = "S"
    return northbound_hikers

def get_thru_hiker_entry_num(hiker_journal):
    """
    get_thru_hiker_entry_num -Returns the number associated with the journal entry where the hiker passed the 2,000
        mile mark threshold.
    :param hiker_journal: The ordered list of journal entries.
    :return entry_num: The entry number corresponding to the journal entry in which the hiker surpassed 2,000 miles. If
        the hiker never reaches thru hiker status then -1 is returned as the entry number.
    """
    entry_num = -1
    for enum, entry in hiker_journal.items():
        if entry['trip_mileage'] >= 2000:
            entry_num = enum
            break
    return entry_num

def display_northbound_days_taken(northbound_days_taken, northbound_thru_hikers):
    print("Number of Northbound Thru-Hikers: %d" % len(northbound_thru_hikers))
    plt.hist(list(northbound_days_taken.values()), bins=50)
    plt.xlabel('Number of Days')
    plt.ylabel('Number of Hikers')
    plt.title("Number of Days Taken for Northbound Hikers to Hike 2,000 Miles of the AT")
    plt.show()
    '''
    num_categories_days_taken = len(northbound_days_taken)
    northbound_days_taken_bins = [key for key in northbound_days_taken.keys()]
    # northbound_days_taken_bins = np.arange(0, 100, step=10)
    northbound_days_taken_stats = [value for value in northbound_days_taken.values()]
    fig, ax = plt.subplots()
    # x locations for the groups:
    bar_heights = np.arange(num_categories_days_taken)
    # width of the bars:
    bar_width = 0.25
    rects1 = ax.bar(bar_heights + bar_width, northbound_days_taken_stats, color='b')
    ax.set_xlabel('Number of Days')
    ax.set_ylabel('Number of Hikers')
    ax.set_title("Number of Days Taken for Northbound Hikers to Hike 2,000 Miles of the AT")
    ax.set_xticks(northbound_days_taken_bins)
    ax.set_xticklabels(northbound_days_taken_bins)
    # plt.xlabel('Jan    Feb    Mar    Apr    May    Jun    July    Aug    Sep    Oct    Nov    Dec')
    storage_loc = os.path.abspath(os.path.join(os.path.dirname(__file__), 'northbound_avg_num_days.png'))
    plt.show()
    plt.savefig(storage_loc)
    ndt = plt.hist2d(list(northbound_days_taken.values()), list(northbound_days_taken.keys()), bins=5)
    plt.title("Number of Days Taken for Northbound Hikers to Hike 2,000 Miles of the AT")
    plt.xlabel("Number of Days Taken")
    plt.ylabel("Number of Hikers")
    plt.show()
    '''

def main(valid_hikers_path):
    valid_hikers = get_validated_hikers(validated_hikers_path=valid_hikers_path)
    thru_hikers = get_validated_thru_hikers(valid_hikers)
    northbound_thru_hikers = get_northbound_hikers(thru_hikers)
    southbound_thru_hikers = get_southbound_hikers(thru_hikers)

    northbound_days_taken = {}
    for hid, hiker_info in northbound_thru_hikers.items():
        first_entry_num = list(hiker_info['journal'].keys())[0]
        thru_hiker_threshold_enum = get_thru_hiker_entry_num(hiker_info['journal'])
        # last_entry_num = list(hiker_info['journal'].keys())[len(hiker_info['journal'].keys()) - 1]
        first_entry = hiker_info['journal'][first_entry_num]
        first_entry_date = first_entry['date'].replace(",", "")
        last_entry = hiker_info['journal'][thru_hiker_threshold_enum]
        last_entry_date = last_entry['date'].replace(",", "")
        try:
            first_entry_date = datetime.strptime(first_entry_date, "%A %B %d %Y")
        except Exception:
            print("Exception encountered with hid: %d. Entry number: %d." %(hid, first_entry_num))
        try:
            last_entry_date = datetime.strptime(last_entry_date, "%A %B %d %Y")
        except Exception:
            print("Exception encountered with hid: %d. Entry number: %d." %(hid, thru_hiker_threshold_enum))
        delta = last_entry_date - first_entry_date
        if delta.days in northbound_days_taken:
            northbound_days_taken[delta.days] += 1
        else:
            northbound_days_taken[delta.days] = 1

    southbound_days_taken = {}
    for hid, hiker_info in southbound_thru_hikers.items():
        first_entry_num = list(hiker_info['journal'].keys())[0]
        thru_hiker_threshold_enum = get_thru_hiker_entry_num(hiker_info['journal'])
        # last_entry_num = list(hiker_info['journal'].keys())[len(hiker_info['journal'].keys()) - 1]
        first_entry = hiker_info['journal'][first_entry_num]
        first_entry_date = first_entry['date'].replace(",", "")
        last_entry = hiker_info['journal'][thru_hiker_threshold_enum]
        last_entry_date = last_entry['date'].replace(",", "")
        try:
            first_entry_date = datetime.strptime(first_entry_date, "%A %B %d %Y")
        except Exception:
            print("Exception encountered with hid: %d. Entry number: %d." %(hid, first_entry_num))
        try:
            last_entry_date = datetime.strptime(last_entry_date, "%A %B %d %Y")
        except Exception:
            print("Exception encountered with hid: %d. Entry number: %d." %(hid, thru_hiker_threshold_enum))
        delta = last_entry_date - first_entry_date
        if delta.days in southbound_days_taken:
            southbound_days_taken[delta.days] += 1
        else:
            southbound_days_taken[delta.days] = 1
    # Filter out negative numbers:
    northbound_non_negative_keys = sorted([key for key in northbound_days_taken.keys() if key >= 0])
    southbound_non_negative_keys = sorted([key for key in southbound_days_taken.keys() if key >= 0])
    northbound_days_taken_non_negative = OrderedDict()
    southbound_days_taken_non_negative = OrderedDict()
    for key in northbound_non_negative_keys:
        northbound_days_taken_non_negative[key] = northbound_days_taken[key]
    for key in southbound_non_negative_keys:
        southbound_days_taken_non_negative[key] = southbound_days_taken[key]

    print("[Northbound Hikers] Days Taken to Complete at least 2,000 miles:")
    print(northbound_days_taken_non_negative)
    display_northbound_days_taken(northbound_days_taken_non_negative, northbound_thru_hikers)
    print("\n[Southbound Hikers] Days Taken to Complete at least 2,000 miles:")
    print(southbound_days_taken_non_negative)

if __name__ == '__main__':
    validated_hikers_data_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/VHDistancePrediction/'))
    main(valid_hikers_path=validated_hikers_data_path)
