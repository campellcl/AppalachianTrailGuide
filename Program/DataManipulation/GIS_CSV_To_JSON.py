"""

"""

import os
import json

def main():
    pass

if __name__ == '__main__':
    trail_centerline_gis_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../..', 'Data/TrailCenterline/'))
    json_dict = {}
    with open(trail_centerline_gis_path + "/sorted_at_centerline_gis.csv", 'r') as fp:
        i = 0
        for line in iter(fp):
            if i != 0:
                split_lat_lon = line.split(",")
                lat = float(split_lat_lon[0])
                lon = float(split_lat_lon[1])
                json_dict[i] = {'lat': lat, 'lon': lon}
            i += 1
    with open(trail_centerline_gis_path + "/sorted_at_centerline_gis.json", 'w') as fp:
        json.dump(json_dict, fp=fp, sort_keys=True, indent=2)
