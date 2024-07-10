#!/usr/bin/env python3

import arrow
import requests
import json

# -- send request --

# TODO get sunrise and sunset times and only get forecasts for these times
# TODO get forecast for the next 7 days in one request if possible 
# TODO either average out the data providers (e.g. NOAA) or select the best one

FORECAST_PATH = "./forecast.json"
TIDE_PATH = "./tide.json"

# Get first hour of today
#TIME_AT_START_OF_DAY = arrow.now().floor('day')

# Get last hour of today
#TIME_AT_END_OF_DAY = arrow.now().ceil('day')

def fetch_surf_forecast(start_time, end_time, lat, lng, api_key):
    """
    Parameters:
    start_time : local time
    end_time : local time
    """
    
    response = requests.get(
        'https://api.stormglass.io/v2/weather/point',
        params={
            'lat': lat,
            'lng': lng,
            'params': ','.join(['swellDirection', 'swellHeight', 'swellPeriod',
                                'secondarySwellDirection',
                                'secondarySwellHeight', 'secondarySwellPeriod',
                                'windDirection', 'windSpeed']),
            'start': start_time.to('UTC').timestamp(),  # Convert to UTC timestamp
            'end': end_time.to('UTC').timestamp()  # Convert to UTC timestamp
        },
        headers={
            'Authorization': api_key
        }
    )
    return response.json()

def fetch_tide(start_time, end_time, lat, lng, api_key):
    responce = requests.get(
        'https://api.stormglass.io/v2/tide/extremes/point',
        params={
            'lat': lat,
            'lng': lng,
            'start': start_time.to('UTC').timestamp(), # Convert to UTC timestamp
            'end': end_time.to('UTC').timestamp() # Convert to UTC timestamp
        },
        headers={
            'Authorization': api_key
        }
    )
    return responce.json()

def update_forecast(lat, lng, start_time, end_time, api_key):

    with open(FORECAST_PATH, 'r') as file:
        latest_forecast = json.load(file)
    
    print(f"latest_forecast['meta']['requestCount'] : {latest_forecast['meta']['requestCount']}")

    current_time = arrow.now() #TODO: USE DATETIME
    
    last_forecast_date = arrow.get(latest_forecast['hours'][3]['time']) 
    #TODO:factor in daylight savings time and time zones
    
    if current_time.format('YYYY-MM-DD') != last_forecast_date.format('YYYY-MM-DD'):
        print("current time != last forecast")
        latest_forecast = fetch_surf_forecast(start_time, end_time, lat, lng, 
                                              api_key)
        if 'errors' not in latest_forecast:#TODO add to a historical forecasts file/list 
            # TODO: use sqlite, u can use json string into the db
            # key=date, value={tide: 1233}
            with open(FORECAST_PATH, 'w') as json_file:
                json.dump(latest_forecast, json_file, indent=4)

        print("--- fetched new forecast ---")

    return latest_forecast

def update_tides(lat, lng, start_time, end_time, api_key):

    with open(TIDE_PATH, 'r') as file:
        latest_tides = json.load(file)
    
    current_time = arrow.now() #TODO: USE DATETIME
    last_tide_date = arrow.get(latest_tides['data'][0]['time']) 
    if current_time.format('YYYY-MM-DD') != last_tide_date.format('YYYY-MM-DD'):
        print("current time != last forecast")
        latest_tides = fetch_tide(start_time, end_time, lat, lng, api_key)
        if 'errors' not in latest_tides:
           with open(TIDE_PATH, 'w') as json_file:
               json.dump(latest_tides, json_file, indent=4)

        print("--- fetched new tide data ---")

    return latest_tides
