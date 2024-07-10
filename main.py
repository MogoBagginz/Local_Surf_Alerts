#!/usr/bin/env python3

import spot_conf
import process_forecast
import fetch_forecast
import arrow
import json

from plyer import notification

#TODO put api key in a local variable file
API_KEY="5c9db1cc-145a-11ef-9da7-0242ac130004-5c9db26c-145a-11ef-9da7-0242ac130004"

# Get first hour of today
TIME_AT_START_OF_DAY = arrow.now().floor('day')

# Get last hour of today
TIME_AT_END_OF_DAY_NEXT_WEEK = arrow.now().shift(days=+7).ceil('day')

LOCAL_OFSET = 1

# TODO get sunrise and sunset times and only get forecasts for these times
# TODO get forecast for the next 7 days in one request if possible 
# TODO make a spot condition overview

#TODO create function that creates a new surf_break_configuration
#TODO create function that changes a surf_break_configuration
#TODO historic back testing
#TODO function that takes time and location when the surf is good and it saves
# ... all the conditions into a file. the file can be used when configuring max
# ... and min values for a spot.
# TODO make a widget

if __name__ == "__main__":

    print(f"TIME_AT_END_OF_DAY_NEXT_WEEK : {TIME_AT_END_OF_DAY_NEXT_WEEK}")
    print(f"TIME_AT_START_OF_DAY : {TIME_AT_START_OF_DAY}")

    # load spot configurations
    whitesands_conf_path = "whitesands_conf.json"
    whitesands_conf = spot_conf.Surf_Break_Config()
    whitesands_conf.load_from_file(whitesands_conf_path)

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

    # process forecast
    process_forecast.process_forecast(whitesands_conf, latest_forecast,
                                      whitesands_conditions)
    process_forecast.check_surf_cleanliness(whitesands_conf, whitesands_conditions,
                           latest_forecast['hours'][6+LOCAL_OFSET]['windSpeed']['noaa'])
    
    # print everyth?!?jedi=0, ing for debugging?!? (*_*obj: Any*_*, skipkeys: bool=..., ensure_ascii: bool=..., check_circular: bool=..., allow_nan: bool=..., cls: Optional[Type[JSONEncoder]]=..., indent: Union[None, int, str]=..., separators: Optional[Tuple[str, str]]=..., default: Optional[Callable[[Any], Any]]=..., sort_keys: bool=..., **kwds: Any) ?!?jedi?!?
    print(json.dumps(latest_forecast['hours'][6+LOCAL_OFSET], indent=4))
    print(json.dumps(latest_tides['data'], indent=4))
    print(whitesands_conf)
    print(whitesands_conditions)

    # Get the current time in Germany (CET/CEST)
    time_now_germany = arrow.now('Europe/Berlin')

    tide_height_now = process_forecast.calculate_tide_height(latest_tides,
                                                             time_now_germany)

    print(f"The tide height at {time_now_germany} is {tide_height_now}.")

    # get check surf at spot
    if process_forecast.check_surf_at_spot(whitesands_conf, whitesands_conditions):
        print("Surfs up bro!!! Whitesands has surf!!!")

        # send notification
        notify.send_notification("SURF ALERT", "Surfs up bro!!!")
