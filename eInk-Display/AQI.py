#!/usr/bin/env python3

import sys
import os
import urllib.request

import logging
import time
# from PIL import Image,ImageDraw,ImageFont
# import traceback
# import textwrap
import lnetatmo

import requests
import json 

from datetime import date, timedelta, datetime
import argparse 

# sys.path.insert(1, '/path/to/application/app/folder')
from waveshare_epd import epd7in5_V2

version = "0.1" 
global APIKEY 

global args 

parser = argparse.ArgumentParser()
parser.add_argument('--street', help='insert help here')
parser.add_argument('--city', help='insert help here')
parser.add_argument('--state', help='insert help here')
parser.add_argument('--zip', help='insert help here')
parser.add_argument('--long', help='insert help here')
parser.add_argument('--lat', help='insert help here')
parser.add_argument('--apikey', help='insert help here')
parser.add_argument('-v', dest='verbose', action='store_true')
parser.add_argument('-d', dest='debug', action='store_true')

args = parser.parse_args()

fontDir = '/usr/local/share/fonts/';
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

# --------------------
def lookupAddress(street,city,state,zip):
    print("lookupAddress")

    arguements = ["format=json", "benchmark=2020"]
    if street is not None: 
        arguements.append("street={}".format(street.replace(" ","+")))
    if city is not None:
        arguements.append("city={}".format(city))
    if state is not None: 
        arguements.append("state={}".format(state))
    if zip is not None: 
        arguements.append("zip={}".format(zip))
    arguementStrinfg="&".join(arguements)

    URL = "https://geocoding.geo.census.gov/geocoder/locations/address?{}".format("&".join(arguements))
    response = requests.get(URL) 
    jsonResponse = json.loads(response.content) 

    try:
        for match in jsonResponse['result']['addressMatches']:
            if args.verbose is True:
                print("\tmatched adress {}".format(match['matchedAddress']))
                print("\tcoordinates: {}".format(match['coordinates']))

        URL = "https://api.weather.gov/points/{},{}".format("{:.3f}".format(match['coordinates']['y']) ,"{:.3f}".format(match['coordinates']['x']))
        if args.debug is True: 
            print("\t>>{}".format(URL))
        response = requests.get(URL) 
        if args.debug is True:
            print("++ {}".format(response))
        ResponseJSON = json.loads(response.content) 

        if args.debug is True:
            print("\t{}".format(ResponseJSON['properties']))

        if args.verbose is True:

            print("\tforecastOffice URL: {}".format(ResponseJSON['properties']['forecastOffice']))
            print("\tforecastHourly URL: {}".format(ResponseJSON['properties']['forecastHourly']))
            print("\tforecastZone URL: {}".format(ResponseJSON['properties']['forecastZone']))
            forecastZone = requests.get(ResponseJSON['properties']['forecastZone'])
            zoneJSON = json.loads(forecastZone.content)
            # print(zoneJSON['properties']['name'])
            print("\tforecastZone: {} ({})".format(zoneJSON['properties']['name'],ResponseJSON['properties']['forecastZone']))
            print("\tradarStation: {}".format(ResponseJSON['properties']['radarStation']))

            print("\tobservationStations URL: {}".format(ResponseJSON['properties']['observationStations']))
            # observationStations = requests.get("https://api.weather.gov/gridpoints/LWX/109,91/stations")
            observationStations = requests.get(ResponseJSON['properties']['observationStations'])
            observationJSON = json.loads(observationStations.content)
            print("\tObervation Stations")
            for feature in observationJSON['features']:
                print("\t\t{}".format(feature['properties']['name']))

    except: 
        print("except error")

        
    print("\n---\n") 
    return 

def main(): 
    print("main")
    lookupAddress(args.street,args.city,args.state,args.zip)

if __name__ == '__main__': 
    if args.verbose is True: 
        print("verbose output: ON")
    if args.debug is True:
        print("debug mode: ON")
    # currentObservation = "https://www.airnowapi.org/aq/observation/zipCode/current/?format=application/json&zipCode=21211&distance=25&API_KEY={}"
    # current  = requests.get(currentObservation)
    # JSONreturned  = json.loads(current.content)
    # print(JSONreturned)

    # forecastURL = "https://www.airnowapi.org/aq/forecast/zipCode/?format=application/json&zipCode=21211&date=2023-06-28&distance=25&API_KEY={}"
    # forecast = requests.get(forecastURL)
    # JSONreturned  = json.loads(current.content)
    # print(JSONreturned)


    currentByLongLatURL = "https://www.airnowapi.org/aq/observation/latLong/current/?format=application/json&latitude=38.956&longitude=-74.852&distance=50&API_KEY={}"
    currentByLongLat = requests.get(currentByLongLatURL)
    JSONreturned  = json.loads(currentByLongLat.content)
    for data in JSONreturned:
        print("{} / {} / {}".format(data['ParameterName'],data['AQI'],data['Category']['Name'] ))
        # print("\n")
    print("---")
    # print(JSONreturned)

    main()

    exit();


# 1 => Sunny # 3 => Partly Cloudy?  # 5 => Cloudy # 6 => lightning cloud # 7 => little rain /drizzle # 8 => rain
# 9 => windy # 0 > lightning (white clouds) # ! => windy rain # \ =>  snow # " => heavy snow 
# # => hail # $ => cloudy # % => lightning # ' => thermometer # & => # , => # ( => compass 
# ) => n/a # * => C # + => F # A => Fog # B => Sunny # C => moon (clear) # D => Eclipse # E => Mist # F => Windy
# G => Snowflake # H => partly cloudy/sunny?  # I => partly cloudy / moon # J => fog + sun # K => fog + moon
# L => fog + clouds # M => FOG # N => cloud # O => cloud + lightning # P => cloud + lightning
# Q => drizzle # R => rain # S => windy  + cloud # T => windy + cloud + rain  # U => snow # V => snow # W => heavy snow 
# X => hail # Y => clody # Z => clouds + lightning

# to geocode an address 
# https://geocoding.geo.census.gov/geocoder/locations/address?street=4600+Silver+Hill+Rd&city=Washington&state=DC&benchmark=2020&format=json
# https://geocoding.geo.census.gov/geocoder/locations/address?street=411+Washington+St&City=Cape+May&atate=NJ&zip=08204&benchmark=2020&format=json

