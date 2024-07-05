#!/usr/bin/env python3

"""
this class takes the spot config obj and a time stamp

- fetch forcast
- process forcast
- create summary

it returns a spot condition overview 
"""

import math
import arrow
import json

# TODO: get sunrise and sunset times and only get forcasts for these times
# TODO either average out the data providers (e.g. NOAA) or select the best one

class Surf_Break_Conditions: #TODO think about removing the Nones
    def __init__(self, name=None, lat=None, long=None, time=None,
                 primary_wave_energy=None, secondary_wave_energy=None,
                 combined_wave_energy=None, rel_swell_dir=None,
                 effective_power=None, rel_wind_dir=None,
                 messiness_wind=None, messiness_swell=None,
                 messiness_total=None):
        self.name = name
        self.lat = lat
        self.long = long
        self.time = time
        self.primary_wave_energy = primary_wave_energy
        self.secondary_wave_energy = secondary_wave_energy
        self.combined_wave_energy = combined_wave_energy
        self.rel_swell_dir = rel_swell_dir
        self.effective_power = effective_power
        self.rel_wind_dir = rel_wind_dir
        self.messiness_wind = messiness_wind
        self.messiness_swell = messiness_swell
        self.messiness_total = messiness_total
    
    def __str__(self):
        # Print class name
        rtnVal = f"\nClass: {self.__class__.__name__}\n\nAttributes:\n"

        # Print instance attributes
        for attr, value in vars(self).items():
            rtnVal += f"{attr}: {value}\n"
        return rtnVal

def check_surf_at_spot(spot_conf, spot_conditions): 
    if spot_conditions.effective_power >= spot_conf.min_wave_energy \
    and spot_conditions.messiness < 100:
        return True 
    else:
        return False

def process_forcast(spot_conf, forcast, spot_conditions):
    primary_wave_energy = get_wave_energy(float(forcast['hours'][0]['swellPeriod']['noaa']),
                                          float(forcast['hours'][0]['swellHeight']['noaa']))
    secondary_wave_energy = get_wave_energy(float(forcast['hours'][0]['secondarySwellPeriod']['noaa']),
                                            float(forcast['hours'][0]['secondarySwellHeight']['noaa']))
    combined_swell_dir = get_relative_dir(forcast['hours'][0]['swellDirection']['noaa'],
                                          forcast['hours'][0]['secondarySwellDirection']['noaa'])
    combined_wave_energy = get_combined_wave_energy(primary_wave_energy,
                                                    secondary_wave_energy,
                                                    combined_swell_dir)
    rel_swell_dir = get_relative_dir(spot_conf.break_direction, combined_swell_dir)
    effective_power = calculate_effective_power(combined_wave_energy, rel_swell_dir)
    rel_wind_dir = get_relative_dir(spot_conf.break_direction,
                                    forcast['hours'][0]['windDirection']['noaa'])
    spot_conditions.rel_wind_dir = rel_wind_dir
    spot_conditions.name = spot_conf.name
    spot_conditions.lat = spot_conf.latitude
    spot_conditions.long = spot_conf.longitude
    spot_conditions.time = arrow.now()
    spot_conditions.primary_wave_energy = primary_wave_energy
    spot_conditions.secondary_wave_energy = secondary_wave_energy
    spot_conditions.combined_wave_energy = combined_wave_energy
    spot_conditions.combined_swell_dir = combined_swell_dir
    spot_conditions.rel_swell_dir = rel_swell_dir
    spot_conditions.effective_power = effective_power

def check_surf_cleanliness(spot_conf, spot_conditions, wind_speed):
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
            wind_messiness = (wind_speed / spot_conf.max_offshore_wind_speed) * 100
    else:
            wind_messiness = (wind_speed / spot_conf.max_onshore_wind_speed) *  100

    spot_conditions.messiness_wind = wind_messiness
    spot_conditions.messiness_swell = swell_messiness
    spot_conditions.messiness_total = wind_messiness + swell_messiness

    return spot_conditions.messiness_total

def check_relatively_equal(a, b, rel_tol=0.5):#TODO function unecesary
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
    P_eff = P * math.cos(math.radians(theta))
    return P_eff

def normalize_angle(angle):# TODO function unnecesary
    return angle % 360

def get_relative_dir(primary_dir, secondary_dir):   
    secondary_dir = normalize_angle(secondary_dir)
    primary_dir = normalize_angle(primary_dir)

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

# function that returns the tide hight when given a location

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
