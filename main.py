#!/usr/bin/env python3
"""
surf cam = https://www.surfline.com/surf-report/whitesands/584204204e65fad6a77090ce?view=table
"""
# TODO look for a language server
# TODO find addon that list classes function files
import json
import arrow
import notify
import spot_conf
import process_forecast as pf
import fetch_forecast as ff

LOCAL_OFFSET = 1 # UK local time with no daylight saving TODO add daylight savings

# TODO get sunrise and sunset times and only get forecasts for these times
#TODO create function that creates a new SurfBreakConfiguration
#TODO create function that changes a SurfBreakConfiguration
#TODO historic back testing
#TODO function that takes time and location when the surf is good and it saves
# ... all conditions into a file. the file can be used when configuring max
# ... and min values for a spot.
# TODO make a widget

if __name__ == "__main__":
    FORECAST_LEN = 5
    # load spot configurations #################################################
    WHITESANDS_CONF_PATH = "whitesands_conf.json"
    whitesands_conf = spot_conf.SurfBreakConfig()
    whitesands_conf.load_from_file(WHITESANDS_CONF_PATH)
    #whitesands_conf.save_to_file(WHITESANDS_CONF_PATH)
    WHITESANDS_FORECAST_PATH = f"forecasts/{whitesands_conf.name}_forecast.json"
    POPIT_CONF_PATH = "popit_conf.json"
    popit_conf = spot_conf.SurfBreakConfig()
    popit_conf.load_from_file(POPIT_CONF_PATH)
    POPIT_FORECAST_PATH = f"forecasts/{popit_conf.name}_forecast.json"
    #whitesands_conf.save_to_file(WHITESANDS_CONF_PATH)

    # fetch forecast ###########################################################
    #TODO use logger

    ff.update_forecast(whitesands_conf.latitude, whitesands_conf.longitude,
                       WHITESANDS_FORECAST_PATH, FORECAST_LEN)
    ff.update_forecast(popit_conf.latitude, popit_conf.longitude,
                       POPIT_FORECAST_PATH, FORECAST_LEN)

    latest_forecast_whitesands = ff.open_forecast(WHITESANDS_FORECAST_PATH)
    latest_forecast_popit = ff.open_forecast(POPIT_FORECAST_PATH)

    # fetch tides ##############################################################
    TIDE_PATH = 'tide.json'
    #latest_tides = ff.update_tides(whitesands_conf.latitude,
    #                                          whitesands_conf.longitude,
    #                                          TIME_START_FORECAST,
    #                                          TIME_END_FORECAST,
    #                                          TIDE_PATH,
    #                                          #current_date, forcast_date,
    #                                          #WHITESANDS_FORCAST_PATH,
    #                                          API_KEY)

    # print everything #########################################################
    #print(json.dumps(latest_forecast_whitesands['hours'][6+LOCAL_OFFSET], indent=4))
    #print(json.dumps(latest_tides['data'], indent=4))
    #print(whitesands_conf)
    #print(whitesands_conditions)
    #print(whitesands_conditions.summary())

    # notification #############################################################
    NOTIFY_STRING = ""
    for days in range(0, FORECAST_LEN, 1):
        for hour in range(6, 22, 3):
            whitesands_conditions = pf.process_forecast(whitesands_conf,
                                                        latest_forecast_whitesands,
                                                        hour + (days * 24))
            popit_conditions = pf.process_forecast(popit_conf,
                                                   latest_forecast_popit,
                                                   hour + (days * 24))
            if pf.check_surf_at_spot(whitesands_conf, whitesands_conditions):
                NOTIFY_STRING += whitesands_conditions.summary(days, hour)
            if pf.check_surf_at_spot(popit_conf, popit_conditions):
                NOTIFY_STRING += popit_conditions.summary(days, hour)
    if NOTIFY_STRING:
        notify.send_notification("Surfs up bro!!!", NOTIFY_STRING)

    # Get the current time in Germany (CET/CEST)
    time_now_germany = arrow.now('Europe/Berlin')
    #tide_height_now = pf.calculate_tide_height(latest_tides,
    #                                                         time_now_germany)
    #print(f"The tide height at {time_now_germany} is {tide_height_now}.")
