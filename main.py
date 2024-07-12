#!/usr/bin/env python3
"""
surf cam = https://www.surfline.com/surf-report/whitesands/584204204e65fad6a77090ce?view=table
"""

import notify
import spot_conf
import process_forecast
import fetch_forecast
import arrow
import json
import sqlite3

#from plyer import notification

#TODO put api key in a local variable file
API_KEY="5c9db1cc-145a-11ef-9da7-0242ac130004-5c9db26c-145a-11ef-9da7-0242ac130004"

# Get first hour of today
TIME_AT_START_OF_DAY = arrow.now().floor('day')

# Get last hour of today
TIME_AT_END_OF_DAY_NEXT_WEEK = arrow.now().shift(days=+7).ceil('day')

LOCAL_OFFSET = 1 # UK local time with no daylight saving TODO add daylight savings

# TODO get sunrise and sunset times and only get forecasts for these times
# TODO make a spot condition overview

#TODO create function that creates a new surf_break_configuration
#TODO create function that changes a surf_break_configuration
#TODO historic back testing
#TODO function that takes time and location when the surf is good and it saves
# ... all conditions into a file. the file can be used when configuring max
# ... and min values for a spot.
# TODO make a widget
   
if __name__ == "__main__":

    print(f"TIME_AT_END_OF_DAY_NEXT_WEEK : {TIME_AT_END_OF_DAY_NEXT_WEEK}")
    print(f"TIME_AT_START_OF_DAY : {TIME_AT_START_OF_DAY}")

    # load spot configurations
    whitesands_conf_path = "whitesands_conf.json"
    whitesands_conf = spot_conf.Surf_Break_Config()
    whitesands_conf.load_from_file(whitesands_conf_path)
    #whitesands_conf.save_to_file(whitesands_conf_path)
    
    # spot conditions
    whitesands_conditions = process_forecast.Surf_Break_Conditions()

    # fetch forecast
    latest_forecast = fetch_forecast.update_forecast(whitesands_conf.latitude,
                                                     whitesands_conf.longitude,
                                                     TIME_AT_START_OF_DAY,
                                                     TIME_AT_END_OF_DAY_NEXT_WEEK,
                                                     API_KEY)

    # fetch tides
    latest_tides = fetch_forecast.update_tides(whitesands_conf.latitude,
                                              whitesands_conf.longitude,
                                              TIME_AT_START_OF_DAY,
                                              TIME_AT_END_OF_DAY_NEXT_WEEK,
                                              API_KEY)

    desired_hour = 6 # desired hour 
    # process forecast
    process_forecast.process_forecast(whitesands_conf, latest_forecast,
                                      whitesands_conditions, desired_hour)
    process_forecast.check_surf_cleanliness(whitesands_conf, whitesands_conditions)
   
    # print everything
    #print(json.dumps(latest_forecast['hours'][6+LOCAL_OFFSET], indent=4))
    #print(json.dumps(latest_tides['data'], indent=4))
    print(whitesands_conf)
    print(whitesands_conditions)
    print(whitesands_conditions.summary())
    
    notify_string = ""
    for days in range(0, 7, 1):
        for hour in range(6, 22, 3): 
            process_forecast.process_forecast(whitesands_conf, latest_forecast,
                                              whitesands_conditions,
                                              hour + (days * 24))
            process_forecast.check_surf_cleanliness(whitesands_conf, whitesands_conditions)
            if process_forecast.check_surf_at_spot(whitesands_conf,
                                                   whitesands_conditions):
                notify_string += whitesands_conditions.short_summary(days, hour)   
    if notify_string:
        notify.send_notification("Surfs up bro!!!", notify_string)
        
    # Get the current time in Germany (CET/CEST)
    time_now_germany = arrow.now('Europe/Berlin')
    tide_height_now = process_forecast.calculate_tide_height(latest_tides,
                                                             time_now_germany)
    print(f"The tide height at {time_now_germany} is {tide_height_now}.")
