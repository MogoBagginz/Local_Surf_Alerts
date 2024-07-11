#!/usr/bin/env python3

"""
this class takes the spot config obj and a time stamp

- fetch forecast
- process forecast
- create summary

it returns a spot condition overview 
"""

import math
import arrow
import json
import datetime

# TODO: get sunrise and sunset times and only get forecasts for these times
# TODO either average out the data providers (e.g. NOAA) or select the best one

class Surf_Break_Conditions: #TODO think about removing the Nones
    def __init__(self, name=None, lat=None, long=None, time=None, primary_wave_energy=None,
                 secondary_wave_energy=None, combined_wave_energy=None,
                 combined_swell_dir=None, rel_swell_dir=None,
                 effective_power=None, rel_wind_dir=None, messiness_wind=None, messiness_swell=None,
                 messiness_total=None, primary_height=None, primary_period=None, primary_dir=None,
                 secondary_wave_rel_dir=None, wind_speed=None, wind_gust=None):
        self.name = name
        self.lat = lat
        self.long = long
        self.time = time
        self.primary_wave_energy = primary_wave_energy
        self.secondary_wave_energy = secondary_wave_energy
        self.combined_wave_energy = combined_wave_energy
        self.combined_swell_dir = combined_swell_dir
        self.rel_swell_dir = rel_swell_dir
        self.effective_power = effective_power
        self.rel_wind_dir = rel_wind_dir
        self.messiness_wind = messiness_wind
        self.messiness_swell = messiness_swell
        self.messiness_total = messiness_total
        self.primary_height = primary_height
        self.primary_period = primary_period
        self.primary_dir = primary_dir
        self.secondary_wave_rel_dir = secondary_wave_rel_dir
        self.wind_speed = wind_speed
        self.wind_gust = wind_gust
   
    def short_summary(self, day=0, hour=0):
        rtn_val = f"\n--- Simple {self.name} condition summary ---\n\n"\
                f"In {day} days at {hour} o'clock\n"\
                f"Effective power: {self.effective_power:.2f}\n"\
                f"Messiness from swell: {self.messiness_swell:.0f}%\n"\
                f"Messiness from wind: {self.messiness_wind:.0f}%\n"
        return rtn_val

    def summary(self, day=0, hour=0):
        rtn_val = f"\n--- {self.name} condition summary ---\n\n"\
                  f"In {day} days at {hour} o'clock\n"\
                  f"Effective power: {self.effective_power:.2f}\n"\
                  f"Primary height: {self.primary_height:.2f} meters\n"\
                  f"Primary period: {self.primary_period:.2f} seconds\n"\
                  f"Primary direction: {self.primary_dir:.2f}\n"\
                  f"Secondary wave power: {self.secondary_wave_energy:.2f}\n"\
                  f"Secondary wave relative direction: {self.secondary_wave_rel_dir:.2f}\n"\
                  f"Messiness: {self.messiness_total:.0f}%\n"\
                  f"Relative wind direction: {self.rel_wind_dir:.2f}\n"\
                  f"Wind speed: {self.wind_speed:.2f} kph\n"\
                  f"Wind gust: {self.wind_gust:.2f} kph\n"
        return rtn_val

    def __str__(self):
        # Print class name
        rtn_val = f"\nClass: {self.__class__.__name__}\n\nAttributes:\n"

        # Print instance attributes
        for attr, value in vars(self).items():
            rtn_val += f"{attr}: {value}\n"
        return rtn_val

def check_surf_at_spot(spot_conf, spot_conditions): 
    if spot_conditions.effective_power >= spot_conf.min_wave_energy \
    and spot_conditions.messiness_total <= 100:
        return True 
    else:
        return False

def process_forecast(spot_conf, forecast, spot_conditions, hour):
    primary_wave_energy = get_wave_energy(float(forecast['hours'][hour]['swellPeriod']['noaa']),
                                          float(forecast['hours'][hour]['swellHeight']['noaa']))
    secondary_wave_energy = get_wave_energy(float(forecast['hours'][hour]['secondarySwellPeriod']['noaa']),
                                            float(forecast['hours'][hour]['secondarySwellHeight']['noaa']))
    combined_swell_dir = get_relative_dir(forecast['hours'][hour]['swellDirection']['noaa'],
                                          forecast['hours'][hour]['secondarySwellDirection']['noaa'])
    combined_wave_energy = get_combined_wave_energy(primary_wave_energy,
                                                    secondary_wave_energy,
                                                    combined_swell_dir)
    rel_swell_dir = get_relative_dir(spot_conf.break_direction, combined_swell_dir)
    effective_power = calculate_effective_power(combined_wave_energy, rel_swell_dir)
    rel_wind_dir = get_relative_dir(spot_conf.break_direction,
                                    forecast['hours'][hour]['windDirection']['noaa'])
    spot_conditions.rel_wind_dir = rel_wind_dir
    spot_conditions.name = spot_conf.name
    spot_conditions.lat = spot_conf.latitude
    spot_conditions.long = spot_conf.longitude
    spot_conditions.time = hour
    spot_conditions.primary_wave_energy = primary_wave_energy
    spot_conditions.secondary_wave_energy = secondary_wave_energy
    spot_conditions.combined_wave_energy = combined_wave_energy
    spot_conditions.combined_swell_dir = combined_swell_dir
    spot_conditions.rel_swell_dir = rel_swell_dir
    spot_conditions.effective_power = effective_power
    spot_conditions.primary_height = forecast['hours'][hour]['swellHeight']['noaa']
    spot_conditions.primary_period = forecast['hours'][hour]['swellPeriod']['noaa']
    spot_conditions.primary_dir = forecast['hours'][hour]['swellDirection']['noaa']
    spot_conditions.secondary_wave_rel_dir = get_relative_dir(spot_conf.break_direction,
                                                              forecast['hours'][hour]['swellDirection']['noaa']) 
    spot_conditions.wind_speed = mps_to_kph(forecast['hours'][hour]['windSpeed']['noaa'])
    spot_conditions.wind_gust = mps_to_kph(forecast['hours'][hour]['gust']['noaa'])

def mps_to_kph(mps):
    return mps * 3.6

def check_surf_cleanliness(spot_conf, spot_conditions):
    wave_e_1 = spot_conditions.primary_wave_energy
    wave_e_2 = spot_conditions.secondary_wave_energy

    # - check if the swell make it messy -
    if check_relatively_equal(wave_e_1, wave_e_2) \
    and abs(spot_conditions.rel_swell_dir) > 30:
        # divide the higher by the lower and turn into percentage
        if wave_e_1 > wave_e_2:
            swell_messiness =  (wave_e_1 / wave_e_2) * 100
        else:
            swell_messiness =  (wave_e_2 / wave_e_1) * 100
    else:
        swell_messiness = 0
    
    # - check if the wind make it massy -
    if abs(spot_conditions.rel_wind_dir) >= 180: # offshore
        wind_messiness = (spot_conditions.wind_speed / spot_conf.max_offshore_wind_speed) * 100
    else:
        wind_messiness = (spot_conditions.wind_speed / spot_conf.max_onshore_wind_speed) * 100

    spot_conditions.messiness_wind = wind_messiness
    spot_conditions.messiness_swell = swell_messiness
    spot_conditions.messiness_total = wind_messiness + swell_messiness

    return spot_conditions.messiness_total

def check_relatively_equal(a, b, rel_tol=0.5):
    return abs(a - b) <= rel_tol

def calculate_effective_power(P, theta):
    # Calculate the effective power of the wave hitting the beach at an angle.
    P = float(P)
    theta = float(theta)
    if P < 0:
        raise ValueError("P must be a positive number.")
    if abs(theta) > 360:
        raise ValueError("Direction is in degrees and can not be greater"
                         "than or less than +-360")
    P_eff = P * abs(math.cos(math.radians(theta/2)))
    return P_eff

def get_relative_dir(primary_dir, secondary_dir):
    # normalize angles
    secondary_dir = secondary_dir % 360
    primary_dir = primary_dir % 360

    relative_angle = secondary_dir - primary_dir
    
    if relative_angle < -180: 
        relative_angle += 360
    elif relative_angle >= 180:
        relative_angle -= 360

    return relative_angle

def get_wave_energy(period, height):
    # https://techiescience.com/how-to-calculate-wave-energy-in-ocean-engineering/
    # Wave energy density calculated using linear wave theory
    # args: height = from top of crest to bottom of trough
    # returns energy_density = kJ/m^2
    water_density = 1025 #kg/m^3
    gravity = 9.8 #m/s^2
    
    period = float(period)
    height = float(height)

    energy_density = 1 / 8 * water_density * gravity * height**2 * period

    return energy_density

def get_combined_wave_energy(e_1, e_2, relative_dir):
    e_1 = float(e_1)
    e_2 = float(e_2)
    relative_dir = float(relative_dir)

    if e_1 < 0 or e_2 < 0:
        raise ValueError("e_1 and e_1 both need to be positive numbers")
    if abs(relative_dir) > 360:
        raise ValueError("relative_dir is in degrees and can not be greater"
                         "than or less than +-360")
    relative_dir_radians = math.radians(relative_dir)
    combined_wave_energy = e_1 + e_2 + math.sqrt(e_1 * e_2) * math.cos(relative_dir_radians)

    return combined_wave_energy

def calculate_tide_height(tide_data, target_time):
    """
    Calculate the tide height at a given time from JSON tide data.
    
    Parameters:
    tide_data (dict): JSON object containing tide data.
    target_time (str): Time at which to calculate the tide height in
                       YYYY-MM-DDTHH:MM:SS+00:00 format.
    
    Returns:
    float: The calculated tide height at the given time.
    """
    # Extract tide data
    high_tides = [item for item in tide_data['data'] if item['type'] == 'high']
    low_tides = [item for item in tide_data['data'] if item['type'] == 'low']
    
    if not high_tides or not low_tides:
        raise ValueError("Insufficient tide data in JSON.")

    high_tide = high_tides[0]
    low_tide = low_tides[0]

    high_tide_height = high_tide['height']
    high_tide_time = arrow.get(high_tide['time'])
    
    low_tide_height = low_tide['height']
    low_tide_time = arrow.get(low_tide['time'])
    
    # Convert target_time
    target_time = arrow.get(target_time)

    # Calculate the average tide height
    avg_tide_height = (high_tide_height + low_tide_height) / 2

    # Calculate the tidal range (e.g. avg to high)
    tidal_range = (high_tide_height - low_tide_height) / 2

    tidal_period = 12.42

    # Calculate the time difference in hours from the high tide time to the
    # target time
    delta_t = (target_time - high_tide_time).total_seconds() / 3600

    # Calculate the tide height at the target time
    tide_height = avg_tide_height + tidal_range * math.cos((2 * math.pi / tidal_period) * delta_t)

    return tide_height
