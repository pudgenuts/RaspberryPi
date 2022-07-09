#!/usr/bin/python

# -*- coding:utf-8 -*-
import sys
import os
fontDir = '/usr/local/share/fonts/';
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
# from textwrap import fill
import textwrap
import lnetatmo

# global font_weather; font_weather = ImageFont.truetype('fonts/Roboto-Black.ttf', 20)
# global font_weather_icons; font_weather_icons = ImageFont.truetype('fonts/meteocons-webfont.ttf', 45)

# global font_cal; font_cal = ImageFont.truetype('/usr/local/share/fonts/truetype/freefont/FreeMonoBold.ttf', 16)
global font36; font36 = ImageFont.truetype(os.path.join(fontDir, 'Font.ttc'), 36)
global font24; font24 = ImageFont.truetype(os.path.join(fontDir, 'Font.ttc'), 24)
global font18; font18 = ImageFont.truetype(os.path.join(fontDir, 'Font.ttc'), 18)

global font_day; font_day = ImageFont.truetype('/usr/local/share/fonts/Roboto-Black.ttf', 110)
global font_weather; font_weather = ImageFont.truetype('/usr/local/share/fonts/Roboto-Black.ttf', 20)
global font_day_str; font_day_str = ImageFont.truetype('/usr/local/share/fonts/Roboto-Light.ttf', 35)
global font_month_str; font_month_str = ImageFont.truetype('/usr/local/share/fonts/Roboto-Light.ttf', 25)
global font_weather_icons; font_weather_icons = ImageFont.truetype('/usr/local/share/fonts/meteocons-webfont.ttf', 45)
global font_tasks_list_title; font_tasks_list_title = ImageFont.truetype('/usr/local/share/fonts/Roboto-Light.ttf', 30)
global font_tasks_list; font_tasks_list = ImageFont.truetype('/usr/local/share/fonts/tahoma.ttf', 12)
global font_tasks_due_date; font_tasks_due_date = ImageFont.truetype('/usr/local/share/fonts/tahoma.ttf', 11)
global font_tasks_priority; font_tasks_priority = ImageFont.truetype('/usr/local/share/fonts/tahoma.ttf', 9)
global font_update_moment; font_update_moment = ImageFont.truetype('/usr/local/share/fonts/tahoma.ttf', 9)
global icons_list; icons_list = {u'01d':u'B',u'01n':u'C',u'02d':u'H',u'02n':u'I',u'03d':u'N',u'03n':u'N',u'04d':u'Y',u'04n':u'Y',u'09d':u'R',u'09n':u'R',u'10d':u'R',u'10n':u'R',u'11d':u'P',u'11n':u'P',u'13d':u'W',u'13n':u'W',u'50d':u'M',u'50n':u'W'}

# --------------------
from datetime import date,datetime
import urllib.request, json


def convertC2F(C):
        return ((C * 9/5) +32)

def fetchCurrentTemp():
    global weather_response
    authorization = lnetatmo.ClientAuth()
    print(authorization)
    weatherData = lnetatmo.WeatherStationData(authorization)
    outdoorData = weatherData.moduleById('02:00:00:33:d5:56')
    tempC = outdoorData['dashboard_data']['Temperature']
    fahrenheit = convertC2F(tempC)

    return fahrenheit

def query_weather(url):
    # global weather_response
    # global forecast_response
    print('-= Ping Weather API =- %s' %(url))
    while True:
        try:
            # response = requests.get(url).json()
            response = urllib.request.urlopen(url)
            print(response)
            break
        except:
            print('-= Weather API JSON Failed - Will Try Again =-')
            time.sleep(5)

    return response

today = date.today()
day = query_weather("https://api.weather.gov/gridpoints/LWX/107,91/forecast?units=us")
dayForecast = json.loads(day.read().decode())
hourly = query_weather("https://api.weather.gov/gridpoints/LWX/107,91/forecast/hourly")
hourlyForecast = json.loads(hourly.read().decode())

try: 
    F = fetchCurrentTemp()
except:
    F = "unk"

count = 0

try:
    epd = epd7in5_V2.EPD()
    
    epd.init()
    epd.Clear()


    # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...")
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    
    now = datetime.now()
    N = now.strftime("%B %d, %Y  %H:%M")
    draw.text((15, 20), N , font = font24, fill = 0)
    if type(F) is str: 
        currentTemp = "curent temp: unknown"
    else: 
        currentTemp = "curent temp: {:.2f} F".format(F)
    draw.text((550, 20), currentTemp , font = font24, fill = 0)

    # (start pix, start line, stop pix, stop line)
    draw.line((0, 60, 800, 60), fill = 0,width = 5 ) # horizontal line 
    off = 70
    for item in dayForecast['properties']['periods']:
        count = count+1
        lineNumber = 1
        forecast = textwrap.wrap(item['detailedForecast'],width=85)
        for line in forecast: 
            if lineNumber == 1: 
                 LINE = "{}: {}".format(item['name'],line)
                 print("%s" % (LINE))
                 draw.text((0,off), LINE, font=font18, fill = 0)
                 off = off + 23
            else: 
                 LINE = "  {}".format(line)
                 print("%s" % (LINE))
                 draw.text((0,off), LINE, font=font18, fill = 0)
                 off = off + 23
            lineNumber = lineNumber +1

	
        # print("%s: %s" % (item['name'], item['detailedForecast']))
        # line = "{}: {}".format(item['name'], item['detailedForecast'])
        # draw.text((0,off), line, font=font18, fill = 0)
        # off = off + 23
        if count == 2: 
            break
    draw.line((0,off, 800, off), fill = 0,width = 5 )  # horizontal line 
    # draw.line((0, 120, 800, 120), fill = 0,width = 5 )  # horizontal line 
    # draw.line((350, 120, 350, 600), fill = 0,width = 5 )  # vertical line 
    draw.line((350, off, 350, 600), fill = 0,width = 5 )  # vertical line 
    hour = 0
    offset = off + 5
    for item in hourlyForecast['properties']['periods']:
        hour = hour +1 
        # StartTime = datetime.datetime.strptime(item['startTime'])
        start = datetime.strptime(item['startTime'].replace("T", " ",1) ,  "%Y-%m-%d %H:%M:%S%z")
        # print(start.strftime("%-I %p"))


        draw.text((10,offset), start.strftime("%-I %p").rjust(5), font=font18, fill = 0)
        draw.text((75,offset), str(item['temperature']).rjust(3), font=font18, fill = 0)
        draw.text((100,offset), str(item['temperatureUnit']), font=font18, fill = 0)
        # if item['shortForecast'] == "Mostly Sunny" : 
            # draw.text((155,offset), "B", font=font_weather_icons, fille=0)
        # elif item['shortForecast'] == "Mostly Sunny" : 
        # elif item['shortForecast'] == "Mostly Sunny" : 
        # elif item['shortForecast'] == "Mostly Sunny" : 
        # elif item['shortForecast'] == "Mostly Sunny" : 
        # elif item['shortForecast'] == "Mostly Sunny" : 
        # elif item['shortForecast'] == "Mostly Sunny" : 
        # elif item['shortForecast'] == "Mostly Sunny" : 


        # hourly = "{}   {} {}   {} winds {} from the {}".format(start.strftime("%-I %p").rjust(5),str(item['temperature']).rjust(3),item['temperatureUnit'],item['shortForecast'],item['windSpeed'],item['windDirection'])
        # hourly = "{} winds {} from the {}".format(item['shortForecast'],item['windSpeed'],item['windDirection'])
        hourly = "{}".format(item['shortForecast'])
        draw.text((145,offset), hourly, font=font_weather, fill = 0)
        offset = offset+25
        if hour == 10: 
            break

    # offset=75
    # draw.text((10,offset ), ",'&" , font = font_weather_icons , fill = 0)
    # 1 => Sunny
    # 3 => Partly Cloudy? 
    # 5 => Cloudy 
    # 6 => lightning cloud 
    # 7 => little rain /drizzle
    # 8 => rain
    # 9 => windy 
    # 0 > lightning (white clouds) 
    # ! => windy rain
    # \ =>  snow 
    # " => heavy snow 
    # # => hail 
    # $ => cloudy 
    # % => lightning 
    # ' => thermometer
    # & => 
    # , => 
    # ( => compass 
    # ) => n/a 
    # * => C 
    # + => F
    # A => Fog
    # B => Sunny 
    # C => moon (clear) 
    # D => Eclipse 
    # E => Mist
    # F => Windy
    # G => Snowflake
    # H => partly cloudy/sunny?
    # I => partly cloudy / moon
    # J => fog + sun 
    # K => fog + moon
    # L => fog + clouds
    # M => FOG
    # N => cloud
    # O => cloud + lightning
    # P => cloud + lightning
    # Q => drizzle
    # R => rain
    # S => windy  + cloud
    # T => windy + cloud + rain  
    # U => snow
    # V => snow 
    # W => heavy snow 
    # X => hail 
    # Y => clody 
    # Z => clouds + lightning


    # draw.rectangle((10, 150, 60, 200), fill = 0)
    # draw.line((10, 90, 60, 140), fill = 0)
    # draw.line((60, 90, 10, 140), fill = 0)
    # draw.text((10, 20), '7.5inch e-Paper', font = font24, fill = 0)
    # draw.text((150, 0), u'微雪电子', font = font24, fill = 0)
    # draw.line((20, 50, 70, 100), fill = 0)
    # draw.line((70, 50, 20, 100), fill = 0)
    # draw.rectangle((20, 50, 70, 100), outline = 0)
    # draw.line((165, 50, 165, 100), fill = 0)
    # draw.line((140, 75, 190, 75), fill = 0)
    # draw.arc((140, 50, 190, 100), 0, 360, fill = 0)
    # draw.rectangle((80, 50, 130, 100), fill = 0)
    # draw.chord((200, 50, 250, 100), 0, 360, fill = 0)
    epd.display(epd.getbuffer(Himage))
    # time.sleep(10)

    # Drawing on the Vertical image

    # == logging.info("2.Drawing on the Vertical image...")
    # == Limage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    # == draw = ImageDraw.Draw(Limage)
    # == draw.text((2, 0), 'hello world', font = font18, fill = 0)
    # == draw.text((2, 20), '7.5inch epd', font = font18, fill = 0)
    # == draw.text((20, 50), u'微雪电子', font = font18, fill = 0)
    # == draw.line((10, 90, 60, 140), fill = 0)
    # == draw.line((60, 90, 10, 140), fill = 0)
    # == draw.rectangle((10, 90, 60, 140), outline = 0)
    # == draw.line((95, 90, 95, 140), fill = 0)
    # == draw.line((70, 115, 120, 115), fill = 0)
    # == draw.arc((70, 90, 120, 140), 0, 360, fill = 0)
    # == draw.rectangle((10, 150, 60, 200), fill = 0)
    # == draw.chord((70, 150, 120, 200), 0, 360, fill = 0)
    # == epd.display(epd.getbuffer(Limage))
    # time.sleep(2)

    # == logging.info("3.read bmp file")
    # DIR="/home/pi/"
    # Himage = Image.open(os.path.join(DIR, '3741355_light rain_rain_rainny_weather_icon.png'))
    # epd.display(epd.getbuffer(Himage))
    # time.sleep(20)

    # == logging.info("4.read bmp file on window")
    # == Himage2 = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    # == bmp = Image.open(os.path.join(picdir, '100x100.bmp'))
    # == Himage2.paste(bmp, (50,10))
    # == epd.display(epd.getbuffer(Himage2))
    # == time.sleep(2)

    # logging.info("Clear...")
    # epd.init()
    # epd.Clear()

    # logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5_V2.epdconfig.module_exit()
    exit()
