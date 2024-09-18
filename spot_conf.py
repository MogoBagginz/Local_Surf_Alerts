#!/usr/bin/env python3

import json

# use Object --- SurfBreakConfig(Object)
class SurfBreakConfig:
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
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(self.__dict__, file)

    def load_from_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
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
        rtn_val = f"\nClass: {self.__class__.__name__}\n\nAttributes:\n"

        # Print instance attributes
        for attr, value in vars(self).items():
            rtn_val += f"{attr}: {value}\n"
        return rtn_val
