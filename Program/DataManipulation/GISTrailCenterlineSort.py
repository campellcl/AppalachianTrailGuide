"""
GISTrailCenterlineSort.py
Sorts the gis coordinates of the trail profile in order from south to north using nearest neighbor.
:author: Chris Campell
:version: 11/15/2016
"""

__author__ = "Chris Campell"
__version__ = "11/15/2016"

import sys
import os
import json
from haversine import haversine

def get_trail_centerline_gis(storage_dir):
    trail_centerline_gis = []
    line_num = 0
    with open(storage_dir + "/AT_Centerline_GIS.csv", 'r') as fp:
        for line in iter(fp):
            if not line_num == 0:
                lat_lon_str = str.split(line, ",")
                lon = lat_lon_str[0]
                lat = lat_lon_str[1]
                trail_centerline_gis.append((lat, lon))
            line_num += 1
    return trail_centerline_gis

def get_min_distance_index(centerline_gis, point_of_origin):
    smallest_haversine = sys.maxsize
    min_distance_index = -1
    i = 0
    for lat, lon in centerline_gis:
        hvrsin = haversine(point_of_origin, (float(lat), float(lon)))
        if hvrsin < smallest_haversine:
            smallest_haversine = hvrsin
            min_distance_index = i
        i += 1
    return min_distance_index

def main():
    trail_centerline_gis_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/TrailCenterline/'))
    centerline_gis = get_trail_centerline_gis(storage_dir=trail_centerline_gis_path)
    sorted_centerline_gis = []
    southern_terminus = None
    southern_terminus_index = None
    i = 0
    for lat, lon in centerline_gis:
        if lat == '34.62669316200002' and lon == '-84.19382841799994':
            southern_terminus = (float(lat), float(lon))
            southern_terminus_index = i
        i += 1
    # Remove southern terminus:
    del centerline_gis[southern_terminus_index]
    i = 0
    while centerline_gis:
        if i == 0:
            min_dist_index = get_min_distance_index(centerline_gis, southern_terminus)
            min_dist_point = centerline_gis[min_dist_index]
            print("min_dist_point: %s" %(min_dist_point,))
            sorted_centerline_gis.append((float(min_dist_point[0]), float(min_dist_point[1])))
            del centerline_gis[min_dist_index]
        else:
            min_dist_index = get_min_distance_index(centerline_gis, sorted_centerline_gis[len(sorted_centerline_gis) - 1])
            min_dist_point = centerline_gis[min_dist_index]
            print("min_dist_point: %s" %(min_dist_point,))
            sorted_centerline_gis.append((float(min_dist_point[0]), float(min_dist_point[1])))
            del centerline_gis[min_dist_index]

        i += 1
    # Write to JSON:
    json_dict = {}
    i = 0
    for lat, lon in sorted_centerline_gis:
        json_dict[i] = (lat, lon)
        i += 1
    with open(trail_centerline_gis_path + "/sorted_at_centerline_gis.json", 'w') as fp:
        json.dump(obj=json_dict, fp=fp, sort_keys=True)

if __name__ == '__main__':
    main()
