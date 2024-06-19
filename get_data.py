#!/usr/bin/env python3

import math
import arrow
import requests
import json



# API endpoint = GET https://api.stormglass.io/v2

API_KEY="5c9db1cc-145a-11ef-9da7-0242ac130004-5c9db26c-145a-11ef-9da7-0242ac130004"

WHITESANDS_LAT = 51.8969 
WHITESANDS_LNG = -5.2977

# -- send request --

# TODO: get sunrise and sunset times and only get forcasts for these times, TODO get forcast for the next 7 days in one request if possible 

# Get first hour of today
TIME_AT_START_OF_DAY = arrow.now().floor('day')

# Get last hour of today
TIME_AT_END_OF_DAY = arrow.now().ceil('day')

def fetch_surf_forecast(start_time, end_time, lat, lng, api_key):
    response = requests.get(
        'https://api.stormglass.io/v2/weather/point',
        params={
            'lat': lat,
            'lng': lng,
            'params': ','.join(['swellDirection', 'swellHeight', 'swellPeriod', 'windDirection', 'windSpeed']),
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
	return responce.json()


#TODO create function that creates a new surf_break_configuration
#TODO create function that changes a surf_break_configuration
	
# configure good conditions for each spot TODO:tide height TODO:secondary swell TODO: put this in another file and import it here.
class Surf_Break_Config:
	def __init__(self, name='Default name', latitude=None, longitude=None, break_direction=None,ideal_swell_direction=225, min_swell_height=1, min_swell_period=7, max_wind_speed=30):
		self.name 					= name
		self.latitude				= latitude
		self.longitude				= longitude
		self.break_direction 		= break_direction # the angle that the beach or reef break faces in degrees
		self.ideal_swell_direction 	= ideal_swell_direction
		self.min_swell_height 		= min_swell_height
		self.min_swell_period 		= min_swell_period
		self.max_wind_speed 		= max_wind_speed

	def update_name(self, name):
		self.name = name

	def update_latitude(self, latitude):
		self.latitude = latitude

	def update_longitude(self, longitude):
		self.longitude = longitude

	def update_break_direction(self, break_direction):
		self.break_direction = break_direction

	def update_ideal_swell_direction(self, ideal_swell_direction):
		self.ideal_swell_direction = ideal_swell_direction

	def update_min_swell_height(self, min_swell_height):
		self.min_swell_height = min_swell_height

	def update_min_swell_period(self, min_swell_period):
		self.min_swell_period = min_swell_period

	def update_max_wind_speed(self, max_wind_speed):
		self.max_wind_speed = max_wind_speed

	def save_to_file(self, file_path):
		with open(file_path, 'w') as file:
			json.dump(self.__dict__, file)

	def load_from_file(self, file_path):
		try:
			with open(file_path, 'r') as file:
				data = json.load(file)
				self.name 		= data['name']
				self.break_direction 		= data['break_direction']
				self.ideal_swell_direction 	= data['ideal_swell_direction']
				self.min_swell_height 		= data['min_swell_height']
				self.min_swell_period 		= data['min_swell_period']
				self.max_wind_speed 		= data['max_wind_speed']
		except FileNotFoundError:
			print("Configuration file not found. Using default settings.")

# function that calculates if conditions meet preferences
#def check_the_surf(spot_config, latest_forcast):
	# is there wind?
		# yes - (function relative_direction(break_direction, wind_or_swell_direction)) use break_direction and wind direction to determin relative_wind_direction (to the beach)
			# determin using relative_wind_direction and wind_speed it the surf will be clean or sloppy
		# no - good
	# is there swell?
	# (function) i need wave_power unit which factors height and period
	# what is the wave_power of the secondary swell?
	# Do the primary and secondary swells combine? (are comming from simmilar directions)
		# yes - what is the combined_wave_power?
		# no - will the surf be messy as a result?
	# calculate relative swell direction
	# use combined_wave_power and swell_direction to determin if there will be swell at the specified beach

def get_relative_direction(break_direction, wind_or_swell_direction):
	result = wind_or_swell_direction - break_diresction
	return result

def get_wave_energy(swell_period, swell_height):
	swell_frequency = 1/swell_period
	wave_energy = swell_frequency * swell_height
	return wave_energy

def get_combined_wave_energy(energy_wave_one, energy_wave_two, relative_direction):
	relative_direction_radians = math.radians(relative_direction)
	combined_wave_energy = energy_wave_one + energy_wave_two + math.sqrt(energy_wave_one * energy_wave_two) * math.cos(relative_energy_radians)
	return combined_wave_energy

# function that returns the tide hight when given a location

# function that takes time and location when the surf is good and it saves all the conditions into a file. the file can be used when configuring max and min values for a spot.

# function that sends notification


if __name__ == "__main__":
	
	# load spot configurations

	whitesands_config = Surf_Break_Config()
	whitesands_config.update_name('whitesands')
	whitesands_config.update_latitude(51.8969)
	whitesands_config.update_longitude(-5.2977)
	whitesands_config.update_break_direction(270)
	whitesands_config.update_ideal_swell_direction(270)
	whitesands_config.update_min_swell_height(1)
	whitesands_config.update_min_swell_period(7)
	whitesands_config.update_max_wind_speed(30)

	whitesands_config.save_to_file('whitesands_config.json')

	# get latest forcast

	# latest_forcast = fetch_surf_forecast(TIME_AT_START_OF_DAY, TIME_AT_END_OF_DAY, whitesands_config.latitude, whitesands_config.longitude, API_KEY)
	# latest_tides = fetch_tide(TIME_AT_START_OF_DAY, TIME_AT_END_OF_DAY, whitesands_config.latitude, whitesands_config.longitude, API_KEY)
	
	# save forcast (for debuggin and later for archiving)
	#with open('forcast.json', 'w') as json_file:
	#	json.dump(latest_forcast, json_file, indent=4)
	# save tide (for debuggin and later for archiving)
	#with open('tide.json', 'w') as json_file:
	#	json.dump(latest_tides, json_file, indent=4)
