#!/usr/bin/env python3

# station IDs: 
	# https://tidesandcurrents.noaa.gov/map/index.html
	# Baltimore - Fort McHenry 8574680
	# Savannah - Fort Pulaski 8670870
	# Hilton Head Island - Port Royal Plantation - 8669167
	# Cape May NJ 8536110
# draw.text((X ,Y), "text", font = font14, fill = 0)

import sys
import os
import urllib.request

import logging
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import textwrap
import lnetatmo

import requests
import json 
from datetime import date, timedelta, datetime
import argparse 

# sys.path.insert(1, '/path/to/application/app/folder')
from waveshare_epd import epd7in5_V2

version = "0.2.01" 

global args 

parser = argparse.ArgumentParser()
parser.add_argument('--config')
parser.add_argument('--stationID', help='stationID to process')
parser.add_argument('-v', dest='verbose', action='store_true')
parser.add_argument('-d', dest='debug', action='store_true')

args = parser.parse_args()

global CONFIG 
CONFIG = {} 

fontDir = '/usr/local/share/fonts/';
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

# station IDs: 
# https://tidesandcurrents.noaa.gov/map/index.html
# Baltimore - Fort McHenry 8574680
# Savannah - Fort Pulaski 8670870
# Hilton Head Island - Port Royal Plantation - 8669167
# Cape May NJ 8536110

# -*- coding:utf-8 -*-

global font36; font36 = ImageFont.truetype(os.path.join(fontDir, 'Font.ttc'), 36)
global font24; font24 = ImageFont.truetype(os.path.join(fontDir, 'Font.ttc'), 24)
global font22; font22 = ImageFont.truetype(os.path.join(fontDir, 'Font.ttc'), 22)
global font20; font20 = ImageFont.truetype(os.path.join(fontDir, 'Font.ttc'), 20)
global font18; font18 = ImageFont.truetype(os.path.join(fontDir, 'Font.ttc'), 18)
global font16; font16 = ImageFont.truetype(os.path.join(fontDir, 'Font.ttc'), 16)
global font14; font14 = ImageFont.truetype(os.path.join(fontDir, 'Font.ttc'), 14)
global font12; font12 = ImageFont.truetype(os.path.join(fontDir, 'Font.ttc'), 12)
global font10; font10 = ImageFont.truetype(os.path.join(fontDir, 'Font.ttc'), 10)

global font_day; font_day = ImageFont.truetype('/usr/local/share/fonts/Roboto-Black.ttf', 110)
global font_weather; font_weather = ImageFont.truetype('/usr/local/share/fonts/Roboto-Black.ttf', 18)
global font_day_str; font_day_str = ImageFont.truetype('/usr/local/share/fonts/Roboto-Light.ttf', 28)
global font_month_str; font_month_str = ImageFont.truetype('/usr/local/share/fonts/Roboto-Light.ttf', 25)
global font_weather_icons; font_weather_icons = ImageFont.truetype('/usr/local/share/fonts/meteocons-webfont.ttf', 45)
global font_tasks_list_title; font_tasks_list_title = ImageFont.truetype('/usr/local/share/fonts/Roboto-Light.ttf', 30)

global icons_list; icons_list = {u'01d':u'B',u'01n':u'C',u'02d':u'H',u'02n':u'I',u'03d':u'N',u'03n':u'N',u'04d':u'Y',u'04n':u'Y',u'09d':u'R',u'09n':u'R',u'10d':u'R',u'10n':u'R',u'11d':u'P',u'11n':u'P',u'13d':u'W',u'13n':u'W',u'50d':u'M',u'50n':u'W'}

# --------------------

def processConfigFile(file):
    fileIN = open(file,"r")
    for line in fileIN: 
        if len(line.strip()) >  0 : 
            line = line.rstrip('\n') 
            lineData = line.split(":",1)
            CONFIG[lineData[0]] = lineData[1].strip()
            if args.debug is True: 
                print("{} => {}".format(lineData[0], lineData[1]) )
    
    if args.verbose is True: 
        print(CONFIG)
        for key, value in CONFIG.items():
            print("{} => {}".format(key,value))

def fetchActiveAlerts(): 

    alerts = {'headline': 'no active alerts'}
    response = requests.get(CONFIG['alertsURL']) 
    json_object = json.loads(response.content) 
    # print(json_object)
    for activeAlert in json_object['features']: 
        for zone in activeAlert['properties']['affectedZones']:
            if CONFIG['countyURL'] == zone: 
                if args.verbose is True: 
                    print(activeAlert['properties']['headline'])
                alerts['headline'] = activeAlert['properties']['headline']
                alerts['onset'] = activeAlert['properties']['onset']
                alerts['expires'] =  activeAlert['properties']['expires']

    return alerts


def fetchTides(stationID,today,tomorrow): 
    tides = []
    URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?begin_date={}&end_date={}&station={}&product=predictions&datum=STND&time_zone=lst_ldt&interval=hilo&units=english&format=json".format(today,tomorrow,stationID) 
    if args.debug is True: 
        print(URL)
    response = requests.get(URL) 
    json_object = json.loads(response.content) 
    
    for prediction in json_object['predictions']: 
        predictionTime = datetime.strptime( prediction['t'], '%Y-%m-%d %H:%M') 
        now = datetime.now() 
        DELTA = (predictionTime- now); 
        if DELTA.total_seconds() > 0: 
            seconds = DELTA.total_seconds() 
            hours = seconds // 3600 
            seconds = seconds - (hours * 3600) 
            minutes = seconds // 60 
            seconds = seconds - (minutes * 60) 
            TimeUntilNextTide = "{:02} hours {:02} minutes".format(int(hours), int(minutes)) 
            
            if prediction['type'] == "L": 
                tides.append({"type": "LOW", "time" : predictionTime.strftime("%I:%M %p %m-%d"), "timeUntilTide" : TimeUntilNextTide, "tideHeight" : prediction['v'] })
                if args.debug is True: 
                    print("prediction LOW tide: {} in {}  at {} feet".format(predictionTime.strftime("%I:%M %p %m-%d"), TimeUntilNextTide, prediction['v'])) 
            elif prediction['type'] == "H": 
                tides.append({"type": "HIGH", "time" : predictionTime.strftime("%I:%M %p %m-%d"), "timeUntilTide" : TimeUntilNextTide, "tideHeight" : prediction['v'] })
                if args.debug is True: 
                    print("prediction HIGH tide: {} in {}  at {} feet".format(predictionTime.strftime("%I:%M %p %m-%d"), TimeUntilNextTide, prediction['v'])) 

    return tides 


def fetchWaterTemps(stationID,today,tomorrow): 
    temps = []
    URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?begin_date={}&end_date={}&station={}&product=water_temperature&datum=STND&time_zone=lst_ldt&interval=h&units=english&format=json".format(today,tomorrow,stationID)
    if args.debug is True:
        print(URL) 

    try: 
        response = requests.get(URL) 
        json_object = json.loads(response.content) 
        if args.debug is True: 
            print("debug:") 
            print(json_object) 

        for waterTemp in json_object['data']: 
            start = datetime.strptime(waterTemp['t'],  "%Y-%m-%d %H:%M") 
            value = "{} F at {}".format( waterTemp['v'], start.strftime("%-I %p").rjust(5) ) 
            temps.append(value)
    except: 
        temps.append(" No data was found.")
            
    return temps


def convertC2F(C):
        return ((C * 9/5) +32)

def fetchCurrentTempNetamo(stationID,today,tomorrow):

    # https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?begin_date=20230620&end_date=20230621&station=8536110&product=air_temperature&datum=STND&time_zone=lst_ldt&units=english&format=json
    print("fetchCurrentTempNetamo")

    try: 
        global weather_response 
        authorization = lnetatmo.ClientAuth() 
        print(authorization) 
        weatherData = lnetatmo.WeatherStationData(authorization) 
        outdoorData = weatherData.moduleById('02:00:00:33:d5:56') 
        tempC = outdoorData['dashboard_data']['Temperature'] 
        fahrenheit = convertC2F(tempC)
        print("try")
    except: 
        if args.debug is True:
            print("except")
        F = "unknown"
    return fahrenheit

def query_weather(url):
    # global weather_response
    # global forecast_response
    if args.debug is True: 
        print('-= Ping Weather API =- %s' %(url))
    while True:
        try:
            response = urllib.request.urlopen(url)
            break
        except:
            print('-= Weather API JSON Failed - Will Try Again =-')
            time.sleep(5)

    return response

def fetchNOAAhourly(today): 
    # Baltimore
    # hourly = query_weather("https://api.weather.gov/gridpoints/LWX/107,91/forecast/hourly")
    # Cape May
    if CONFIG['forecastHourlyURL'] is not None: 
        if args.debug is True: 
            print("using URL: {} for hourly forecast".format(CONFIG['forecastHourlyURL']))
        URL =  CONFIG['forecastHourlyURL']
    else:
        URL = "https://api.weather.gov/gridpoints/LWX/107,91/forecast/hourly"

    hourly = query_weather(URL)
    hourlyForecast = json.loads(hourly.read().decode())

    return hourlyForecast

def fetchAQI(): 

    if CONFIG['AQI_URL'] is not None: 
        URL =  CONFIG['AQI_URL']
    else:
        URL = "https://api.weather.gov/gridpoints/LWX/107,91/forecast/hourly"

    try: 
        # print(URL)
        AQI = requests.get(URL)
        if len(AQI.content) > 10: 
            JSONreturned = json.loads(AQI.content)
        else:
            JSONreturned = { "error": "no content in response to AQI request"}

    except: 
        JSONreturned = { "error", AQI}

    if args.debug is True: 
        print(JSONreturned)
        print(type(JSONreturned))
        elementCount = len(JSONreturned)
        print("items in list:{}".format(elementCount))
        print("+++++")

    return JSONreturned

def fetchNOAAdaily(today): 
    # today = date.today()
    #  Hilton Head: https://api.weather.gov/gridpoints/CHS/59,46/forecast?units=us
    # Baltimore   : https://api.weather.gov/gridpoints/LWX/107,91/forecast?units=us

    # day = query_weather("https://api.weather.gov/gridpoints/LWX/107,91/forecast?units=us")
    # day = query_weather("https://api.weather.gov/gridpoints/CHS/59,46/forecast?units=us") 
    # day = query_weather("https://api.weather.gov/gridpoints/LWX/107,91/forecast?units=us")
    day = query_weather("https://api.weather.gov/gridpoints/PHI/65,32/forecast?units=us")
    dayForecast = json.loads(day.read().decode())

    return dayForecast

def drawFrame(OutsideTemp, dayForcast, hours, tidePredictions, WaterTempratures, aqi, alerts):

    now = datetime.now()
    epd = epd7in5_V2.EPD() 
    epd.init() 
    epd.Clear() 
    logging.info("1.Drawing on the Horizontal image...") 
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame 
    draw = ImageDraw.Draw(Himage)

    # new header row code
    if type(OutsideTemp) is str:
        currentTemp = "current temp: unk" 
    else: 
        currentTemp = "{:.2f} F".format(OutsideTemp) 

    header = "{} / {} / {}".format(now.strftime("%B %d, %Y  %H:%M"),CONFIG['forecastZoneName'], currentTemp )

    if args.debug is True: 
        print(header)
    draw.text((15, 10), header , font = font24, fill = 0) 

    if len(aqi) == 2:    
        airQuality = "Ozone / {} / {}  , PM2.5 / {} / {}".format(aqi[0]['AQI'],aqi[0]['Category']['Name'],aqi[1]['AQI'],aqi[1]['Category']['Name'] ) 
        Ozone = "Ozone / {} / {}".format(aqi[0]['AQI'],aqi[0]['Category']['Name'] )
        PM25 = "PM2.5 / {} / {}".format(aqi[1]['AQI'],aqi[1]['Category']['Name'] )
        draw.text((600, 10), Ozone, font = font14, fill = 0)
        draw.text((600, 30), PM25, font = font14, fill = 0)
        if args.verbose is True:
            print(Ozone)
            print(PM25) 
    else: 
        Ozone = "Ozone / {} / {}".format(aqi[0]['AQI'],aqi[0]['Category']['Name'] )
        draw.text((600, 10), Ozone, font = font14, fill = 0)
        if args.verbose is True:
            print(Ozone)

    draw.line((0, 53, 800, 55), fill = 0,width = 5 ) # horizontal line
    off = 60
    
    if alerts['headline'] != 'no active alerts': 
        if args.verbose is True: 
            print(alerts)
        headline = alerts['headline']
        draw.text((5, 60), headline, font = font22, fill = 0)
        draw.line((0, 100, 800, 100), fill = 0,width = 5 ) # horizontal line
        off = 110


    # old header row code  
    # N = now.strftime("%B %d, %Y  %H:%M") 
    # draw.text((15, 20), N , font = font24, fill = 0) 
    # if type(OutsideTemp) is str:
    #     currentTemp = "current temp: unknown" 
    # else: 
    #     currentTemp = "current temp: {:.2f} F".format(OutsideTemp) 
    # draw.text((500, 20), currentTemp , font = font24, fill = 0) # was font24..... 
    # draw.line((0, 60, 800, 60), fill = 0,width = 5 ) # horizontal line

    # off = 110
    totalLines = 0 
    for line in dayForcast: 
        if off >= 470: 
            break
        totalLines = totalLines + 1
        lineNumber = 1
        forecast = textwrap.wrap(line, width=90) 
        for text in forecast: 
            if lineNumber == 1: 
                draw.text((0,off), text, font=font18, fill = 0) 
                off = off + 23 
            else: 
                draw.text((25,off), text, font=font18, fill = 0) 
                off = off + 23 
                lineNumber = lineNumber +1
        off = off+10
        # draw.text((0,off), line, font=font18, fill = 0) 

    if args.debug is True: 
        print("lines: {} ".format(lineNumber))
        print("offset: {}".format(off))

    draw.line((0,off, 800, off), fill = 0,width = 5 )  # horizontal line 
    # draw.line((0, 120, 800, 120), fill = 0,width = 5 )  # horizontal line 
    # draw.line((350, 120, 350, 600), fill = 0,width = 5 )  # vertical line 
    draw.line((400, off, 400, 600), fill = 0,width = 5 )  # vertical linep 

    offset = off + 8 
    START = offset 
    #  2 AM 47 F / 93% -- Slight Chance Rain Showers
    for item in hours: 
        item = item.replace("And", "&")
        
        if args.verbose is True: 
            stringLength = len(item)
            print("forecast: {} [{}] (len: {})".format(item,offset,stringLength))
            
        draw.text((5,offset), item, font=font16, fill = 0)
        offset = offset+25

    if args.debug is True: 
        print("offset after Hourly: {}".format(offset))

    count = 0
    offset = START 
    for tide in tidePredictions: 
        # print(tide)
        prediction = "{} Tide at {}".format(tide['type'],tide['time'])
        draw.text((410,offset), prediction, font=font18, fill = 0) 
        count = count + 1
        offset = offset+25
        if count == 3: 
            break

    offset = offset+5
    if WaterTempratures== "No data was found.": 

        print(WaterTempratures)
        newLine = 0
        string = "" 
        draw.line((400,offset, 800, offset), fill = 0,width = 5 )  # horizontal line 
        offset = offset+25
        draw.text((410,offset), "Water Tempratures", font=font18, fill = 0) 
        offset = offset+25
        draw.line((400,offset, 800, offset), fill = 0,width = 5 )  # horizontal line 
        offset = offset+10
        for item in WaterTempratures:
            # stringLength = len(item)
            # print(stringLength)
            if newLine == 1: 
                draw.text((610,offset), item, font=font16, fill = 0) 
                newLine = 0 
                offset = offset+20
            else: 
                draw.text((410,offset), item, font=font16, fill = 0) 
                newLine = newLine + 1
            # offset = offset+20\]

    epd.display(epd.getbuffer(Himage)) 

    epd.sleep()

def main(): 
    # stationID=8574680
    stationID=8536110

    if args.stationID is not None: 
        stationID = args.stationID

    TODAY = datetime.now() 
    updated = ( datetime.now() + timedelta( hours=18 ))

    TOMORROW = TODAY + timedelta(1) 
    today= TODAY.strftime("%Y%m%d") 
    # tomorrow = TOMORROW.strftime("%Y%m%d")
    tomorrow = updated.strftime("%Y%m%d")
    if args.debug is True: 
        print(tomorrow)
    
    Tides = fetchTides(stationID,today,tomorrow)
    if args.debug is True: 
        for tidePrediction in Tides: 
            print(tidePrediction)

    waterTempratures = fetchWaterTemps(stationID,today,tomorrow) 
    # print(waterTempratures)

    day = fetchNOAAdaily(today)

    dayForcast = []
    for item in day['properties']['periods']:
        dayForcast.append("{}: {}".format(item['name'],item['detailedForecast']))
        if args.debug is True:
            print(item)
        if item['number'] == 2: 
            break

    hourly = fetchNOAAhourly(today)
    hours = [] 
    for item in hourly['properties']['periods']: 
        # {'number': 10, 'name': '', 'startTime': '2023-02-22T06:00:00-05:00', 'endTime': '2023-02-22T07:00:00-05:00', 'isDaytime': True, 'temperature': 36, 'temperatureUnit': 'F', 'temperatureTrend': None, 'probabilityOfPrecipitation': {'unitCode': 'wmoUnit:percent', 'value': 2}, 'dewpoint': {'unitCode': 'wmoUnit:degC', 'value': -3.888888888888889}, 'relativeHumidity': {'unitCode': 'wmoUnit:percent', 'value': 64}, 'windSpeed': '5 mph', 'windDirection': 'NE', 'icon': 'https://api.weather.gov/icons/land/day/bkn,2?size=small', 'shortForecast': 'Mostly Cloudy', 'detailedForecast': ''}
        start = datetime.strptime(item['startTime'].replace("T", " ",1) ,  "%Y-%m-%d %H:%M:%S%z")
        if args.verbose is True: 
            print("{} {} {} / {}% -- {}".format(start.strftime("%-I %p").rjust(5), item['temperature'],item['temperatureUnit'], item['relativeHumidity']['value'],item['shortForecast']))
        hours.append("{} {} {} / {}% -- {}".format(start.strftime("%-I %p").rjust(5), item['temperature'],item['temperatureUnit'], item['relativeHumidity']['value'],item['shortForecast']))
        # print("\tdew point{}".format(item['dewpoint']['value']))
        # print()
        if item['number'] == 16: 
            break
    
    aqi = fetchAQI()
    alerts = fetchActiveAlerts()


    try: 
        F = fetchCurrentTempNetamo()
    except:
        if args.debug is True: 
            print("except fail fetchCurrentTempNetamo()") 

        try: 
            URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?begin_date={}&end_date={}&station={}&product=air_temperature&datum=STND&time_zone=lst_ldt&interval=h&units=english&format=json".format(today,tomorrow,stationID) 
            response = requests.get(URL)
            json_object = json.loads(response.content) 
            
            # {'metadata': {'id': '8536110', 'name': 'Cape May', 'lat': '38.9683', 'lon': '-74.9600'}, 'data': [{'t': '2023-06-22 00:00', 'v': '63.1', 'f': '0,0,0'}, {'t': '2023-06-22 01:00', 'v': '63.0', 'f': '0,0,0'}, {'t': '2023-06-22 02:00', 'v': '63.1', 'f': '0,0,0'}, {'t': '2023-06-22 03:00', 'v': '63.1', 'f': '0,0,0'}, {'t': '2023-06-22 04:00', 'v': '62.4', 'f': '0,0,0'}, {'t': '2023-06-22 05:00', 'v': '62.2', 'f': '0,0,0'}, {'t': '2023-06-22 06:00', 'v': '61.7', 'f': '0,0,0'}, {'t': '2023-06-22 07:00', 'v': '62.2', 'f': '0,0,0'}, {'t': '2023-06-22 08:00', 'v': '62.1', 'f': '0,0,0'}, {'t': '2023-06-22 09:00', 'v': '62.2', 'f': '0,0,0'}, {'t': '2023-06-22 10:00', 'v': '62.4', 'f': '0,0,0'}, {'t': '2023-06-22 11:00', 'v': '63.3', 'f': '0,0,0'}, {'t': '2023-06-22 12:00', 'v': '63.9', 'f': '0,0,0'}, {'t': '2023-06-22 13:00', 'v': '64.9', 'f': '0,0,0'}, {'t': '2023-06-22 14:00', 'v': '65.5', 'f': '0,0,0'}, {'t': '2023-06-22 15:00', 'v': '64.8', 'f': '0,0,0'}, {'t': '2023-06-22 16:00', 'v': '64.2', 'f': '0,0,0'}, {'t': '2023-06-22 17:00', 'v': '63.5', 'f': '0,0,0'}, {'t': '2023-06-22 18:00', 'v': '64.0', 'f': '0,0,0'}]} 
            for reading in json_object['data']: 
                if args.verbose is True: 
                    # print(">> {}".format(reading))
                    print("?? {} F".format( reading['v']))
                F = float(reading['v'])


            if args.debug is True: 
                print("debug: temp: {}".format(F)) 
                print(json_object) 
            if args.verbose is True: 
                print("setting F to {} ".format(F))
        except: 
            print("hello") 
            F = "unk"

    drawFrame(F,dayForcast,hours, Tides, waterTempratures,aqi,alerts)

if __name__ == '__main__': 
    if args.verbose is True: 
        print("verbose output: ON")
    if args.debug is True:
        print("debug mode: ON")
    
    configFile = "/home/pjohnson/git/RaspberryPi/eInk-Display/frame.config"
    if args.config is not None: 
        configFile = args.config
    processConfigFile(configFile)
    
    if args.stationID is not None: 
        print("stationID set to: {}".format(args.stationID))
    main() 
    print("\n") 
    # new_noaa = NOAA(obtained_token)
    # ans = requests.get('https://www.ncei.noaa.gov/cdo-web/api/v2/stations?limit=100', headers={'token': 'pCOcMqTnRPOjkFtkBjKHNdKyplVPRwfy'})
    # print(ans.content)

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





# https://www.airnowapi.org/aq/observation/latLong/current/?format=application/json&latitude=42.2669&longitude=-71.2506&distance=25&API_KEY=65EC2E3C-C5A4-41D9-A1FB-3D7CAADC3B97
# https://www.airnowapi.org/aq/observation/latLong/current/?format=application/json&latitude=42.147&longitude=-71.252&distance=50&API_KEY=65EC2E3C-C5A4-41D9-A1FB-3D7CAADC3B97
