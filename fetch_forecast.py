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

#TODO consider putting in a class
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
                                'windDirection', 'windSpeed', 'gust']),
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
    return responce

def update_forecast(lat, lng, start_time, end_time, current_date,
                    last_forecast_date, path, api_key, latest_forecast, allow_duplicates=False):
    '''
    Parameters:
        time_now: Should be formatted like this ('YYYY-MM-DD')
        latest_forcast_date: Should be formatted like this ('YYYY-MM-DD') 
    '''

    #TODO factor in daylight savings time and time zones
    if current_date != last_forecast_date or allow_duplicates == True:
        print("current time != last forecast")
        latest_forecast = fetch_surf_forecast(start_time, end_time, lat, lng, 
                                              api_key)
        if 'errors' not in latest_forecast:#TODO add to a historical forecasts file/list 
            # TODO use sqlite, u can use json string into the db
            # key=date, value={tide: 1233}
            print("----------------no errors----------")
            with open(path, 'w') as json_file:
                json.dump(latest_forecast, json_file, indent=4)
        else:
            print(f"Failed updateing the forcast for {latest_forecast_path}:"\
                  f"{json.dump(latest_forecast['errors'])}")

    return latest_forecast

def already_fetched(current_date, last_fetch_date):
    '''
    Parameters:
        time_now: Should be formatted like this ('YYYY-MM-DD')
        latest_forcast_date: Should be formatted like this ('YYYY-MM-DD') 
    '''
    # TODO check if the dates are formatted correctly
    if current_date != last_forecast_date:
        print("current time != last forecast")
        return False
    else:
        return True

def store_forecast(path, latest_forecast):
    if 'errors' not in latest_forecast:#TODO add to a historical forecasts file/list 
        # TODO use sqlite, u can use json string into the db
        # key=date, value={tide: 1233}
        print("----------------no errors----------")
        with open(path, 'w') as json_file:
            json.dump(latest_forecast, json_file, indent=4)
        return True
    else:
        print(f"Failed updateing the forcast for {latest_forecast_path}:"\
              f"{json.dump(latest_forecast['errors'])}")
        return False

# fetch_forcast(api_key, allow_duplicates=False) 
    # check if forecast has been checked already "if already_fetched(current_date, last_fetch_date)"
        # returns true or false
    # fetch forecast
        # returns forecast
    # fetch_tide
        # returns tide_info
    # put forecast in database
        #returns true or false

def update_tides(lat, lng, start_time, end_time, tide_path, api_key, 
                 allow_duplicates=False):

    with open(tide_path, 'r') as file:
        latest_tides = json.load(file)
 
    #TODO put the result of the next two lines in the class for cleanness 
    current_date = arrow.now() #TODO USE DATETIME
    last_tide_date = arrow.get(latest_tides['data'][0]['time']) 
    if current_date.format('YYYY-MM-DD') != last_tide_date.format('YYYY-MM-DD')\
        or allow_duplicates == True:
        print("current time != last forecast")
        latest_tides = fetch_tide(start_time, end_time, lat, lng, api_key)
        if 'errors' not in latest_tides:
           with open(tide_path, 'w') as json_file:
               json.dump(latest_tides, json_file, indent=4)

        print("--- fetched new tide data ---")

    return latest_tides
