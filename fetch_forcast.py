#!/usr/bin/env python3

import arrow
import requests
import json

API_KEY="5c9db1cc-145a-11ef-9da7-0242ac130004-5c9db26c-145a-11ef-9da7-0242ac130004"

# -- send request --

# TODO: get sunrise and sunset times and only get forcasts for these times
# TODO get forcast for the next 7 days in one request if possible 
# TODO either average out the data providers (e.g. NOAA) or select the best one

# Get first hour of today
#TIME_AT_START_OF_DAY = arrow.now().floor('day')

# Get last hour of today
#TIME_AT_END_OF_DAY = arrow.now().ceil('day')

def fetch_surf_forecast(start_time, end_time, lat, lng, api_key):

    print(f"latest_forcast['meta']['requestCount'] : {latest_forcast['meta']['requestCount']}")
    
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
