#!/usr/bin/env python3

import arrow
import requests
import json
import os

# TODO get sunrise and sunset times and only get forecasts for these times
# TODO get forecast for the next 7 days in one request if possible 
# TODO either average out the data providers (e.g. NOAA) or select the best one

FORECAST_PATH = "./forecast.json"
TIDE_PATH = "./tide.json"


#TODO consider putting in a class
def fetch_forecast(start_time, end_time, lat, lng, api_key):
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


def check_forecast_exists(path):
    if os.path.exists(path) and os.path.isfile(path):
        return True
    else:
        return False


def last_fetched_date(path):
    with open(path, 'r') as file:
        last_forecast = json.load(file)
    forecast_date = arrow.get(last_forecast['hours'][3]['time']).format('YYYY-MM-DD')
    return forecast_date


def fetched_today(current_date, last_fetch_date):
    '''
    Parameters:
        time_now: Should be formatted like this ('YYYY-MM-DD')
        latest_forcast_date: Should be formatted like this ('YYYY-MM-DD') 
    '''
    # TODO check if the dates are formatted correctly
    if current_date != last_fetch_date:
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
        print(f"Failed updateing the forcast for {path}:"\
              f"{json.dump(latest_forecast['errors'])}")
        return False


def open_forecast(path):
    with open(path, 'r') as file:
       forecast =json.load(file)
    return forecast


def get_api_key():
    api_file = open('api_key', 'r')
    api_key= api_file.read().rstrip()
    api_file.close()
    return api_key


def update_forecast(lat, lng, path, forecast_len=5):
    if lat > 180 or lat < -180:
        raise ValueError("latitude can only be in range from -180 to 180")
    
    if lng > 90 or lng < -90:
        raise ValueError("Longetude can only be in range from -90 to 90")

    if check_forecast_exists(path):
        current_date = arrow.utcnow().to('Europe/London').format('YYYY-MM-DD')
        print(f"current_date: {current_date}\n last_fetched:"
              f"{last_fetched_date(path)}")
        if fetched_today(current_date, last_fetched_date(path)):
           print("Forecast already updated today.")
           return False
    
    # Get first hour of today
    start_time = arrow.now().floor('day')

    # Get last hour of last day of the forecast length
    end_time = arrow.now().shift(days=+forecast_len).ceil('day')

    forecast = fetch_forecast(start_time, end_time, lat, lng, get_api_key())
    
    if store_forecast(path, forecast):
        return True
    else:
        return False


# fetch forcast library
    # check if forecast exists
        # if yes : get_last_fetch_date()
        # if no : fetch_forecast
    # check if forecast has been checked already today "if already_fetched(current_date, last_fetch_date)"
        # returns true or false
    # fetch forecast
        # returns forecast
    # fetch_tide
        # returns tide_info
    # put forecast in database
        #returns true or false
    # update_forecast(forecast_path, lat, lng, forecast_length)
        # get start and end times(length_of_forecast)
        # returns true or false
    # get_api_key()
        # return api_key


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
