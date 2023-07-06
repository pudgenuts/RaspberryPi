#!/usr/bin/env python3

import sys
import os
import urllib.request
# import logging
import time
import requests
import json     
from datetime import date, timedelta, datetime
import argparse 

# sys.path.insert(1, '/path/to/application/app/folder')
from waveshare_epd import epd7in5_V2

version = "0.1" 

global args 

parser = argparse.ArgumentParser()
parser.add_argument('--street', help='insert help here')
parser.add_argument('--city', help='insert help here')
parser.add_argument('--state', help='insert help here')
parser.add_argument('--zip', help='insert help here')
parser.add_argument('--long', help='insert help here')
parser.add_argument('--lat', help='insert help here')
parser.add_argument('--token', help='insert help here')
parser.add_argument('--overwrite', help='add help here')
parser.add_argument('--apiKey')
parser.add_argument('--stationID')
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
    if args.debug is True: 
        print(URL)
    response = requests.get(URL) 
    jsonResponse = json.loads(response.content) 

    try:
        
        for match in jsonResponse['result']['addressMatches']:
            fileOUT = open("frame.config",'w+')
            fileOUT.write( "matched adress: {}\n".format(match['matchedAddress']))
            fileOUT.write( "coordinates: {}/{}\n".format("{:.3f}".format(match['coordinates']['y']) ,"{:.3f}".format(match['coordinates']['x']) ))
            fileOUT.flush()
                                                         
            if args.verbose is True:
                print(match)
                print()
                print("\tmatched adress {}".format(match['matchedAddress']))
                print("\tcoordinates: {}".format(match['coordinates']))
            

        # fetch other URLs for this LAT / LONG 
        URL = "https://api.weather.gov/points/{},{}".format("{:.3f}".format(match['coordinates']['y']) ,"{:.3f}".format(match['coordinates']['x']))
        responseJSON = json.loads(response.content)

        if args.debug is True: 
            print("\t>>{}".format(URL))
        response = requests.get(URL) 
        
        if args.debug is True:
            print("++ {}".format(response))

        responseJSON = json.loads(response.content) 

        if args.debug is True:
            print("\tdebug: {}".format(responseJSON['properties']))

        forcastOfficeURL = responseJSON['properties']['forecastOffice']
        forecastURL = responseJSON['properties']['forecast']
        hourlyForecastURL = responseJSON['properties']['forecastHourly']

        forecastZoneURL = responseJSON['properties']['forecastZone']
        forecastZone = requests.get(forecastZoneURL)
        forecastZoneJSON = json.loads(forecastZone.content)

        forecastOfficeURL = responseJSON['properties']['forecastOffice']
        forecastOffice = requests.get(forecastOfficeURL)
        forecastOfficeJSON = json.loads(forecastOffice.content)

        radarStation = responseJSON['properties']['radarStation']
        fireWeatherZoneURL = responseJSON['properties']['fireWeatherZone']
        countyURL = responseJSON['properties']['county']
        countyData = requests.get(countyURL)
        countyDataJSON = json.loads(countyData.content) 
        # print(countyDataJSON)

        timeZone = responseJSON['properties']['county']

        observationStations = requests.get(responseJSON['properties']['observationStations'])
        observationStationsJSON = json.loads(observationStations.content)
        # fileOUT = open("frame.config",'w+')
        fileOUT.write("forecastOfficeURL: {}\n".format(forecastOfficeURL))
        fileOUT.write("forecastOffice: {}\n".format(forecastOfficeJSON['name']))
        fileOUT.write("forecastZoneURL: {}\n".format(forecastZoneURL))
        fileOUT.write("forecastZoneName: {}\n".format(forecastZoneJSON['properties']['name']))
        fileOUT.write("forecastURL: {}\n".format(forecastURL))
        fileOUT.write("forecastHourlyURL: {}\n".format(hourlyForecastURL) )
        fileOUT.write("county: {}\n".format(countyDataJSON['properties']['name']) )
        fileOUT.write("countyID: {}\n".format(countyDataJSON['properties']['id']) )
        fileOUT.write("countyURL: {}\n".format(responseJSON['properties']['county']) )
        fileOUT.write("alertsURL: https://api.weather.gov/alerts/active?area={}\n".format(match['addressComponents']['state']) )

        # https://api.weather.gov/alerts/active?area=MD


        if args.apiKey is not None: 
            fileOUT.write("AQI_URL: https://www.airnowapi.org/aq/observation/latLong/current/?format=application/json&latitude={}&longitude={}&distance=50&API_KEY={}\n"
                          .format("{:.4f}".format(match['coordinates']['y']) ,"{:.4f}".format(match['coordinates']['x']),args.apiKey))
        
        # fileOUT.write("\n\n")
        # fileOUT.write("")
        # fileOUT.write("")
        # fileOUT.write("")
        # fileOUT.write("")
        # fileOUT.write("")
        # fileOUT.write("")
        fileOUT.flush()
        fileOUT.close()


        if args.verbose is True:
            print()

            print("\tforecastOffice: {} ({})".format(forecastOfficeJSON['name'],forecastOfficeURL))
            print("\tforecastZone: {} ({})".format(forecastZoneJSON['properties']['name'],forecastZoneURL ))
            print("\tforecastHourly URL: {}".format(hourlyForecastURL))
            print("\tobservationStations URL: {}".format(responseJSON['properties']['observationStations'] ))
            for feature in observationStationsJSON['features']:
                print("\t\t{}".format(feature['properties']['name']))



            # print("\tforecastZone: {} ({})".format(zoneJSON['properties']['name'],ResponseJSON['properties']['forecastZone']))
            # print("\tradarStation: {}".format(ResponseJSON['properties']['radarStation']))

            
            # # observationStations = requests.get("https://api.weather.gov/gridpoints/LWX/109,91/stations")
            # observationStations = requests.get(ResponseJSON['properties']['observationStations'])
            # observationJSON = json.loads(observationStations.content)
            # print("\tObervation Stations")

    except: 
        print("except error")

        
    print("\n---\n") 
    return 

def main(): 
    print("main")
    sucess = lookupAddress(args.street,args.city,args.state,args.zip)

if __name__ == '__main__': 
    if args.verbose is True: 
        print("verbose output: ON")
    if args.debug is True:
        print("debug mode: ON")
    
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

