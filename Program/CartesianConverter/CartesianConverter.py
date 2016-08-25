"""
CartesianConverter.py
Converts a Latitude,Longitude pair to a Cartesian Coordinate (x,y,z).
:Author -Chris Campell, Charles Savoie
:Date -8/20/2016
"""

import os
import urllib.request
import collections
import googleapiclient
import googlemaps
import json

"""
main -Main method for
"""
def main():
    os.chdir("..")
    os.chdir("..")
    cwd = os.getcwd()
    cwd = str.replace(cwd, "\\", "/")
    storage_dir = cwd + "/Data/TrailCenterline"
    file_loc = storage_dir + "/AT_Centerline_GIS.csv"
    os.chdir(storage_dir)
    geo_points = collections.OrderedDict()
    with open(file_loc, 'r') as fp:
        line_num = 0
        for line in iter(fp):
            if line_num != 0:
                entry = line.split(sep=",")
                lon = entry[0]
                lat = entry[1]
                alt = 0
                geo_point = {
                    'lat': lat,
                    'lon': lon,
                    'alt': alt
                }
                geo_points[line_num-1] = geo_point
            line_num += 1
    os.chdir(cwd)
    get_altitude(geo_points)

def get_altitude(points):
    gmaps = googlemaps.Client(key='AIzaSyBFzVC0hDI4Ru6vbjmYsfignFkoP_Faoak')
    locations = ""
    point_number = 0
    api_limiter = 100

    for key, value in points.items():
        locations += str(value['lat']) + "," + str(value['lon'])
        if point_number < api_limiter - 1:
            locations += "|"
        point_number += 1
        if point_number == api_limiter - 2:
            break
    request_url = "http://maps.googleapis.com/maps/api/elevation/json?locations=" + locations + "&key=AIzaSyBCjde_rx_Fe0v4G_vD-uI33M1o9toMF2A"
    print(request_url)
    response = urllib.request.urlopen(url=request_url)
    print(response)

if __name__ == '__main__':
    main()