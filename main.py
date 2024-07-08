#!/usr/bin/env python3

import spot_conf
import process_forecast
import fetch_forecast
import arrow
import json

from plyer import notification

#TODO put api key in a config file
API_KEY="5c9db1cc-145a-11ef-9da7-0242ac130004-5c9db26c-145a-11ef-9da7-0242ac130004"

# TODO get sunrise and sunset times and only get forecasts for these times
# TODO get forecast for the next 7 days in one request if possible 

# Get first hour of today
TIME_AT_START_OF_DAY = arrow.now().floor('day')

# Get last hour of today
TIME_AT_END_OF_DAY = arrow.now().ceil('day')

#TODO create function that creates a new surf_break_configuration
#TODO create function that changes a surf_break_configuration
#TODO historic back testing
#TODO function that takes time and location when the surf is good and it saves
# ... all the conditions into a file. the file can be used when configuring max
# ... and min values for a spot.
# TODO make a widget

if __name__ == "__main__":
    
    # load spot configurations
    whitesands_conf_path = "whitesands_conf.json"
    whitesands_conf = spot_conf.Surf_Break_Config()
    whitesands_conf.load_from_file(whitesands_conf_path)

    # spot conditions
    whitesands_conditions = process_forecast.Surf_Break_Conditions()

    # fetch forecast
    latest_forecast = fetch_forecast.update_forecast()

    # fetch tides
    latest_tides = fetch_forecast.update_tides()

    # process forecast
    process_forecast.process_forecast(whitesands_conf, latest_forecast, whitesands_conditions)
    process_forecast.check_surf_cleanliness(whitesands_conf, whitesands_conditions,
                           latest_forecast['hours'][0]['windSpeed']['noaa'])
    
    # print everything for debugging
    print(json.dumps(latest_forecast['hours'][0], indent=4))
    print(json.dumps(latest_tides['data'], indent=4))
    print(whitesands_conf)
    print(whitesands_conditions)

    # Get the current time in Germany (CET/CEST)
    time_now_germany = arrow.now('Europe/Berlin')

    # Format the time in the desired format
    
    tide_height_now = process_forecast.calculate_tide_height(latest_tides,
                                                             time_now_germany)

    print(f"The tide height at {time_now_germany} is {tide_height_now}.")

    # get check surf at spot
    if process_forecast.check_surf_at_spot(whitesands_conf, whitesands_conditions):
        print("Surfs up bro!!! Whitesands has surf!!!")

        # send notification
        notify.send_notification("SURF ALERT", "Surfs up bro!!!")
