#!/usr/bin/env python3

import process_forcast #TODO replace all forcasts for forecasts
import fetch_forcast
import math
import arrow
import requests
import json

from plyer import notification

API_KEY="5c9db1cc-145a-11ef-9da7-0242ac130004-5c9db26c-145a-11ef-9da7-0242ac130004"

# -- send request --

# TODO: get sunrise and sunset times and only get forcasts for these times
# TODO get forcast for the next 7 days in one request if possible 

# Get first hour of today
TIME_AT_START_OF_DAY = arrow.now().floor('day')

# Get last hour of today
TIME_AT_END_OF_DAY = arrow.now().ceil('day')

#TODO create function that creates a new surf_break_configuration
#TODO create function that changes a surf_break_configuration

# use Object --- Surf_Break_Config(Object)  
class Surf_Break_Config:
    def __init__(self, name='Default name', latitude=None, longitude=None,
                 break_direction=None,ideal_swell_direction=225,
                 min_wave_energy=0.43, max_onshore_wind_speed=20,
                 max_offshore_wind_speed=30):
        self.name                       = name
        self.latitude                   = latitude
        self.longitude                  = longitude
        # break_direction = the angle that the beach or reef break faces in degrees
        self.break_direction            = break_direction
        self.ideal_swell_direction      = ideal_swell_direction
        self.min_wave_energy            = min_wave_energy
        self.max_onshore_wind_speed     = max_onshore_wind_speed
        self.max_offshore_wind_speed    = max_offshore_wind_speed

    def save_to_file(self, file_path):
        with open(file_path, 'w') as file:
            json.dump(self.__dict__, file)

    def load_from_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                self.name                       = data['name']
                self.latitude                   = data['latitude']
                self.longitude                  = data['longitude']
                self.break_direction            = data['break_direction']
                self.ideal_swell_direction      = data['ideal_swell_direction']
                self.min_wave_energy            = data['min_wave_energy']
                self.max_onshore_wind_speed     = data['max_onshore_wind_speed']
                self.max_offshore_wind_speed    = data['max_offshore_wind_speed']
        except FileNotFoundError:
            print("Configuration file not found. Using default settings.")

    def __str__(self):
        # Print class name
        rtnVal = f"\nClass: {self.__class__.__name__}\n\nAttributes:\n"

        # Print instance attributes
        for attr, value in vars(self).items():
            rtnVal += f"{attr}: {value}\n"
        return rtnVal

# function that takes time and location when the surf is good and it saves all the conditions into a file. the file can be used when configuring max and min values for a spot.

# function that sends notification

def send_notification(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            app_name='Your Application Name'
        )
        print("Notification sent successfully!")
    except Exception as e:
        print(f"Failed to send notification: {e}")

# TODO make a widget

if __name__ == "__main__":
    
    # load spot configurations

    whitesands_conf = Surf_Break_Config()
    whitesands_conf.name = 'whitesands'
    whitesands_conf.latitude = 51.8969
    whitesands_conf.longitude = -5.2977
    whitesands_conf.break_direction = 270
    whitesands_conf.ideal_swell_direction = 270
    whitesands_conf.min_wave_energy = process_forcast.get_wave_energy(7,0.3)
    whitesands_conf.max_offshore_wind_speed = 30
    whitesands_conf.max_onshore_wind_speed = 20
    whitesands_conf.save_to_file('whitesands_conf.json')

    # spot conditions
    whitesands_conditions = process_forcast.Surf_Break_Conditions()

    # get latest forcast

    file_path = "./forcast.json"
    with open(file_path, 'r') as file:
        latest_forcast = json.load(file)

    current_time = arrow.now() #TODO: USE DATETIME
    
    last_forcast_date = arrow.get(latest_forcast['hours'][3]['time']) 
    #TODO:factor in daylight savings time and time zones
    
    if current_time.format('YYYY-MM-DD') != last_forcast_date.format('YYYY-MM-DD'):
        print("current time != last forcast")
        latest_forcast = fetch_forcast.fetch_surf_forecast(TIME_AT_START_OF_DAY,
                                              TIME_AT_END_OF_DAY,
                                              whitesands_conf.latitude,
                                              whitesands_conf.longitude,
                                              API_KEY)
        latest_tides = fetch_tide(TIME_AT_START_OF_DAY, TIME_AT_END_OF_DAY,
                                 whitesands_conf.latitude,
                                 whitesands_conf.longitude, API_KEY)
        if 'errors' not in latest_forcast:#TODO add to a historical forcasts file/list 
            # TODO: use sqlite, u can use json string into the db
            # key=date, value={tide: 1233}
            with open('forcast.json', 'w') as json_file:
                json.dump(latest_forcast, json_file, indent=4)

        if 'errors' not in latest_tides:
           with open('tide.json', 'w') as json_file:
               json.dump(latest_tides, json_file, indent=4)

        print("--- fetched new forcast ---")

    # process forcast
    process_forcast.process_forcast(whitesands_conf, latest_forcast, whitesands_conditions)
    process_forcast.check_surf_cleanliness(whitesands_conf, whitesands_conditions,
                           latest_forcast['hours'][0]['windSpeed']['noaa'])
    
    # print everything for debugging
    print(json.dumps(latest_forcast['hours'][0], indent=4))
    print(whitesands_conf)
    print(whitesands_conditions)

    # get the prefered tyde times

    # get check surf at spot
    if process_forcast.check_surf_at_spot(whitesands_conf, whitesands_conditions):
        print("Surfs up bro!!! Whitesands has surf!!!")

        # send notification
        send_notification("SURF ALERT", "Surfs up bro!!!")

# main (main purpose: 
            # > check the surf conditions for n spots for the next n days.
            # > Notify someone)
    #process_forcast (purpose : > checks the surf conditions for one spot
                             # for one time stamp)
    #fetch_forcast (purpose: > fetches the forcast)
    #spot_conf (purpose: > handles spot configurations)
    #notify (purpose: > sends a notification to the user)
