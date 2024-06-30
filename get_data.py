#!/usr/bin/env python3

import math
import arrow
import requests
import json

API_KEY="5c9db1cc-145a-11ef-9da7-0242ac130004-5c9db26c-145a-11ef-9da7-0242ac130004"

# -- send request --

# TODO: get sunrise and sunset times and only get forcasts for these times
# TODO get forcast for the next 7 days in one request if possible 

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
            'params': ','.join(['swellDirection', 'swellHeight', 'swellPeriod',
								'secondarySwellDirection',
								'secondarySwellHeight', 'secondarySwellPeriod',
								'windDirection', 'windSpeed']),
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
	
class Surf_Break_Config:
	def __init__(self, name='Default name', latitude=None, longitude=None,
				 break_direction=None,ideal_swell_direction=225,
				 min_swell_height=1, min_swell_period=7, max_wind_speed=30):
		self.name 					= name
		self.latitude				= latitude
		self.longitude				= longitude
		# break_direction = the angle that the beach or reef break faces in degrees
		self.break_direction 		= break_direction
		self.ideal_swell_direction 	= ideal_swell_direction
		self.min_swell_height 		= min_swell_height
		self.min_swell_period 		= min_swell_period
		self.max_wind_speed 		= max_wind_speed
		self.max_wind_speed 		= max_wind_speed

	def save_to_file(self, file_path):
		with open(file_path, 'w') as file:
			json.dump(self.__dict__, file)

	def load_from_file(self, file_path):
		try:
			with open(file_path, 'r') as file:
				data = json.load(file)
				self.name 					= data['name']
				self.latitude				= data['latitude']
				self.longitude				= data['longitude']
				self.break_direction 		= data['break_direction']
				self.ideal_swell_direction 	= data['ideal_swell_direction']
				self.min_swell_height 		= data['min_swell_height']
				self.min_swell_period 		= data['min_swell_period']
				self.max_wind_speed 		= data['max_wind_speed']
		except FileNotFoundError:
			print("Configuration file not found. Using default settings.")

	def print_class_details(obj):
		# Print class name
		print(f"Class: {obj.__class__.__name__}")

    	# Print instance attributes
		print("\nAttributes:")
		for attr, value in vars(obj).items():
			print(f"{attr}: {value}")

class Surf_Break_Conditions:
	def __init__(self, name=None, lat=None, long=None, time=None,
				 primary_wave_energy=None, secondary_wave_energy=None,
				 combined_wave_energy=None, relative_swell_direction=None,
				 effective_power=None, relative_wind_direction=None):
		self.name = name
		self.lat = lat
		self.long = long
		self.time = time
		self.primary_wave_energy = primary_wave_energy
		self.secondry_wave_energy = secondary_wave_energy
		self.combined_wave_energy = combined_wave_energy
		self.relative_swell_direction = relative_swell_direction
		self.effective_power = effective_power
		self.relative_wind_direction = relative_wind_direction

	def print_class_details(obj):
		# Print class name
		print(f"Class: {obj.__class__.__name__}")

    	# Print instance attributes
		print("\nAttributes:")
		for attr, value in vars(obj).items():
			print(f"{attr}: {value}")

# check_surf_at_spot() 
	# store surf break name, lat and long, time/date in the data storge
	# -- is there spell --
	# -- is it clean --

def process_forcast(spot_conf, forcast, spot_conditions):
	primary_wave_energy = get_wave_energy(float(forcast['hours'][0]['swellPeriod']['noaa']),
										  float(forcast['hours'][0]['swellHeight']['noaa']))
	print("--- secondary wave energy ---")
	secondary_wave_energy = get_wave_energy(float(forcast['hours'][0]['secondarySwellPeriod']['noaa']),
										    float(forcast['hours'][0]['secondarySwellHeight']['noaa']))
	combined_swell_direction = get_relative_direction(forcast['hours'][0]['swellDirection']['noaa'],
													  forcast['hours'][0]['secondarySwellDirection']['noaa'])
	combined_wave_energy = get_combined_wave_energy(primary_wave_energy,
												    secondary_wave_energy,
													combined_swell_direction)
	relative_swell_direction = get_relative_direction(spot_conf.break_direction, combined_swell_direction)
	effective_power = calculate_effective_power(combined_wave_energy, relative_swell_direction)
	
	spot_conditions.name = spot_conf.name
	spot_conditions.lat = spot_conf.latitude
	spot_conditions.long = spot_conf.longitude
	spot_conditions.time = arrow.now()
	spot_conditions.primary_wave_energy = primary_wave_energy
	spot_conditions.secondary_wave_energy = secondary_wave_energy
	spot_conditions.combined_wave_energy = combined_wave_energy
	spot_conditions.combined_swell_direction = combined_swell_direction
	spot_conditions.relative_swell_direction = relative_swell_direction
	spot_conditions.effective_power = effective_power

# is it clean func
	# -- is it clean --
		# does the swell make it messy?
			# if primary and secondary swells have equalish energy and are less than 90 relative to the break
				# get relative primary and secondary swell direction (100 messy 0 not messy)
		# does the wind make it massy?
			# is the reladive wind direction offsure
				# (yes) is the wind above max_offsure_wind_speed (100 to 0 messy)
				# (no) grade messyness in relation to max_offshore_wind_speed

def calculate_effective_power(P, theta):
    """Calculate the effective power of the wave hitting the beach at an angle."""
    P_eff = P * math.cos(math.radians(theta))
    return P_eff

# TODO give option to make it only return a positive integer			
def get_relative_direction(primary_direction, secondary_direction):	
	result = secondary_direction - primary_direction
	return result

def get_wave_energy(swell_period, swell_height):
	swell_frequency = 1/swell_period
	wave_energy = swell_frequency * swell_height
	return wave_energy

def get_combined_wave_energy(e_1, e_2, relative_direction):
	relative_direction_radians = math.radians(relative_direction)
	combined_wave_energy = e_1 + e_2 + math.sqrt(e_1 * e_2) * math.cos(relative_direction_radians)
	return combined_wave_energy

# function that returns the tide hight when given a location

# function that takes time and location when the surf is good and it saves all the conditions into a file. the file can be used when configuring max and min values for a spot.

# function that sends notification


if __name__ == "__main__":
	
	# load spot configurations

	whitesands_conf = Surf_Break_Config()
	whitesands_conf.name = 'whitesands'
	whitesands_conf.latitude = 51.8969
	whitesands_conf.longitude = -5.2977
	whitesands_conf.break_direction = 270
	whitesands_conf.ideal_swell_direction = 270
	whitesands_conf.min_swell_height = 1
	whitesands_conf.min_swell_period = 7
	whitesands_conf.max_wind_speed = 30
	whitesands_conf.save_to_file('whitesands_conf.json')

	# spot conditions
	whitesands_conditions = Surf_Break_Conditions()

	# get latest forcast

	file_path = "./forcast.json"
	with open(file_path, 'r') as file:
		latest_forcast = json.load(file)

	print("latest_forcast['meta']['requestCount'] : ",
		   latest_forcast['meta']['requestCount'])

	current_time = arrow.now()
	last_forcast_date = arrow.get(latest_forcast['hours'][3]['time']) # TODO:factor in daylight savings time
	print("current_time.format('YYYY-MM-DD') : ",
		  current_time.format('YYYY-MM-DD'),
		  "last_forcast_date.format('YYYY-MM-DD') : ",
		  last_forcast_date.format('YYYY-MM-DD'))
	if current_time.format('YYYY-MM-DD') != last_forcast_date.format('YYYY-MM-DD'):
		print("current time != last forcast")
		latest_forcast = fetch_surf_forecast(TIME_AT_START_OF_DAY,
											  TIME_AT_END_OF_DAY,
											  whitesands_conf.latitude,
											  whitesands_conf.longitude,
											  API_KEY)
		#latest_tides = fetch_tide(TIME_AT_START_OF_DAY, TIME_AT_END_OF_DAY,
	#							  whitesands_conf.latitude,
#								  whitesands_conf.longitude, API_KEY)
		if 'errors' not in latest_forcast:
			with open('forcast.json', 'w') as json_file:
				json.dump(latest_forcast, json_file, indent=4)

		#if 'errors' not in latest_tides:
	#		with open('tide.json', 'w') as json_file:
#				json.dump(latest_tides, json_file, indent=4)

		print("--- fetched new forcast ---")

	# process forcast
	process_forcast(whitesands_conf, latest_forcast, whitesands_conditions)

	# print everything for debugging
	print(json.dumps(latest_forcast['hours'][0], indent=4))
	whitesands_conf.print_class_details()
	whitesands_conditions.print_class_details()

	# get check surf at spot

	# get the prefered tyde times

	# send notification
