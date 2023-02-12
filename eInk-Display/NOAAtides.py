import requests
import json 
from datetime import date, timedelta, datetime

TODAY = datetime.now()
today= TODAY.strftime("%Y%m%d")
TOMORROW = TODAY + timedelta(1)
tomorrow = TOMORROW.strftime("%Y%m%d")


# Tides 
URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?begin_date={}&end_date={}&station=8574680&product=predictions&datum=STND&time_zone=lst_ldt&interval=hilo&units=english&format=json".format(today,tomorrow)

response = requests.get(URL)

json_object = json.loads(response.content)
# print(json_object)
for prediction in json_object['predictions']: 
    predictionTime = datetime.strptime( prediction['t'], '%Y-%m-%d %H:%M') 
    now = datetime.now()
    DELTA = (predictionTime- now); 
    if DELTA.total_seconds() > 0: 
        # print(DELTA.total_seconds())
        seconds = DELTA.total_seconds()
        hours = seconds // 3600 
        seconds = seconds - (hours * 3600)
        minutes = seconds // 60
        seconds = seconds - (minutes * 60)
        # total time
        TimeUntilNextTide = "{:02} hours {:02} minutes".format(int(hours), int(minutes))
        # result: 03:43:40

        if prediction['type'] == "L": 
            # print("prediction LOW time: {} in {} hours {} minutes ".format(datetime.datetime(predictionTime, "%H:%M %m-%d"), DELTA.total.hours,DELTA.total.minutes)
            print("prediction LOW tide: {} in {}  at {} feet".format(predictionTime.strftime("%I:%M %p %m-%d"), TimeUntilNextTide, prediction['v'])) 
        elif prediction['type'] == "H": 
            print("prediction HIGH time: {}".format(predictionTime)) 
            # print("---")

 #json_formatted_str = json.dumps(json_object, indent=2)

 #print(json_formatted_str)



# Water tempratues 

URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?begin_date={}&end_date={}&station=8574680&product=water_temperature&datum=STND&time_zone=lst_ldt&interval=h&units=english&format=json".format(today,tomorrow)
print(URL)
response = requests.get(URL)
json_object = json.loads(response.content)
for waterTemp in json_object['data']: 
    predictionTime = datetime.strptime( waterTemp['t'], '%Y-%m-%d %H:%M') 
    DELTA = (predictionTime - datetime.now()) 
    if DELTA.total_seconds() > 0: 
        print("{} F at {}".format( waterTemp['v'], waterTemp['t']))

# json_formatted_str = json.dumps(json_object, indent=2)

# print(json_formatted_str)

# current water temprature 
https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=latest&station=8574680&product=water_temperature&datum=STND&time_zone=lst_ldt&units=english&format=json
https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=la

