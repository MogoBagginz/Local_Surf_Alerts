#!/usr/bin/env python3
"""
surf cam = https://www.surfline.com/surf-report/whitesands/584204204e65fad6a77090ce?view=table
"""
# TODO look for a language server
# TODO find addon that list classes function files 
import notify
import spot_conf
import process_forecast as pf
import fetch_forecast as ff
import arrow
import json

#from plyer import notification

#TODO put api key in local file, add to .gitignore
API_KEY="5c9db1cc-145a-11ef-9da7-0242ac130004-5c9db26c-145a-11ef-9da7-0242ac130004"

# Get first hour of today
TIME_START_FORECAST = arrow.now().floor('day')

# Get last hour of 7 days from now
TIME_END_FORECAST = arrow.now().shift(days=+7).ceil('day')

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
    # load spot configurations
    whitesands_conf_path = "whitesands_conf.json"
    whitesands_conf = spot_conf.Surf_Break_Config()
    whitesands_conf.load_from_file(whitesands_conf_path)
    #whitesands_conf.save_to_file(whitesands_conf_path)
    WHITESANDS_FORECAST_PATH = f"forecasts/{whitesands_conf.name}_forecast.json"
    popit_conf_path = "popit_conf.json"
    popit_conf = spot_conf.Surf_Break_Config()
    popit_conf.load_from_file(popit_conf_path)
    POPIT_FORECAST_PATH = f"forecasts/{popit_conf.name}_forecast.json"
    #whitesands_conf.save_to_file(whitesands_conf_path)

    # fetch forecast
    current_date = arrow.utcnow().to('Europe/London').format('YYYY-MM-DD')
    with open(WHITESANDS_FORECAST_PATH, 'r') as file:
        last_forecast = json.load(file)
    forecast_date = arrow.get(last_forecast['hours'][3]['time']).format('YYYY-MM-DD')
    #TODO use logger                                                             
    print(f"last_forecast['meta']['requestCount'] : {last_forecast['meta']['requestCount']}\n"\
          f"current_date: {current_date}\t\tforecast_date: {forecast_date}")
    latest_forecast_whitesands = ff.update_forecast(whitesands_conf.latitude,
                                                     whitesands_conf.longitude,
                                                     TIME_START_FORECAST,
                                                     TIME_END_FORECAST,
                                                     current_date, forecast_date, 
                                                     WHITESANDS_FORECAST_PATH,
                                                     API_KEY, last_forecast)
    latest_forecast_popit = ff.update_forecast(popit_conf.latitude,
                                               popit_conf.longitude,
                                               TIME_START_FORECAST,
                                               TIME_END_FORECAST,
                                               current_date, forecast_date, 
                                               POPIT_FORECAST_PATH,
                                               API_KEY, last_forecast)

    # fetch tides
    tide_path = 'tide.json'
    #latest_tides = ff.update_tides(whitesands_conf.latitude,
    #                                          whitesands_conf.longitude,
    #                                          TIME_START_FORECAST,
    #                                          TIME_END_FORECAST,
    #                                          tide_path,
    #                                          #current_date, forcast_date, 
    #                                          #WHITESANDS_FORCAST_PATH,
    #                                          API_KEY)

    # spot conditions
    #whitesands_conditions = pf.process_forecast(whitesands_conf,
    #                                            latest_forecast_whitesands,
    #                                            desired_hour)
   
    # print everything
    #print(json.dumps(latest_forecast_whitesands['hours'][6+LOCAL_OFFSET], indent=4))
    #print(json.dumps(latest_tides['data'], indent=4))
    #print(whitesands_conf)
    #print(whitesands_conditions)
    #print(whitesands_conditions.summary())
    
    notify_string = ""
    for days in range(0, 7, 1):
        for hour in range(6, 22, 3): 
            whitesands_conditions = pf.process_forecast(whitesands_conf,
                                                        latest_forecast_whitesands,
                                                        hour + (days * 24))
            popit_conditions = pf.process_forecast(popit_conf,
                                                   latest_forecast_popit,
                                                   hour + (days * 24))
            if pf.check_surf_at_spot(whitesands_conf, whitesands_conditions):
                notify_string += whitesands_conditions.summary(days, hour)
            if pf.check_surf_at_spot(popit_conf, popit_conditions):
                notify_string += popit_conditions.summary(days, hour)
    if notify_string:
        notify.send_notification("Surfs up bro!!!", notify_string)
        
    # Get the current time in Germany (CET/CEST)
    time_now_germany = arrow.now('Europe/Berlin')
    #tide_height_now = pf.calculate_tide_height(latest_tides,
    #                                                         time_now_germany)
    #print(f"The tide height at {time_now_germany} is {tide_height_now}.")
