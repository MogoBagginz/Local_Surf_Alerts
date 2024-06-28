#!/usr/bin/env python3

# CURRENTLY NOT RUNNING - not recognising json file in prosses_forcast func

import math
import arrow
import requests
import json



# API endpoint = GET https://api.stormglass.io/v2

API_KEY="5c9db1cc-145a-11ef-9da7-0242ac130004-5c9db26c-145a-11ef-9da7-0242ac130004"

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
            'params': ','.join(['swellDirection', 'swellHeight', 'swellPeriod', 'secondarySwellDirection', 'secondarySwellHeight', 'secondarySwellPeriod', 'windDirection', 'windSpeed']),
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

class Surf_Break_Conditions:
	def __init__(self, name=None, lat=None, long=None, time=None, date=None, primary_wave_energy=None, secondary_wave_energy=None, combined_wave_energy=None, relative_swell_direction=None, effective_power=None, relative_wind_direction=None):
		self.name = name
		self.lat = lat
		self.long = long
		self.time = time
		self.date = date
		self.primary_wave_energy = primary_wave_energy
		self.secondry_wave_energy = secondary_wave_energy
		self.combined_wave_energy = combined_wave_energy
		self.relative_swell_direction = relative_swell_direction
		self.effective_power = effective_power
		self.relative_wind_direction = relative_wind_direction

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

# ----psudo code round 2 -----
# check_surf_at_spot() 
	# store surf break name, lat and long, time/date in the data storge
	# -- is there spell --
	# -- is it clean --

# is there swell func ... or process forcast for spot and do it when you get the forcast for every spot
def process_forcast(spot_conf, forcast, spot_conditions):
	print("---- process_forcast () -----")
	print("swell Period from inside func : ", forcast['hours'][0]['swellPeriod']['noaa'])
	print("swell Height from inside func : ", forcast['hours'][0]['swellHeight']['noaa'])
	# get combined wave energies
	spot_conditions.primary_wave_energy = get_wave_energy(float(forcast['hours'][0]['swellPeriod']['noaa']), float(forcast['hours'][0]['swellHeight']['noaa']))
	# secondary_wave_energy = get_wave_energy(forcast['secondarySwellPeriod'], forcast['secondarySwellHeight'])
	# combined_wave_energy = get_combined_wave_energy(primary_wave_energy, secondary_wave_energy)
	# get relative energy
	# combined_swell_direction = get_relatice_direction(forcast['swellDirection'], forcast['secondarySwellDirection'])
	# relative_swell_direction = get_relative_direction(spot_conf.break_direction, combined_swell_direction)
		# get relative swell direction
	# effective_power = calculate_effective_power(combined_wave_energy, relative_swell_direction)
		# calculate relative energy
	
	# store relative energy in something

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
			
def get_relative_direction(primary_direction, secondary_direction): # TODO give option to make it only return a positive integer
	result = secondary_direction - primary_diresction
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
	whitesands_conditions.primary_wave_energy = 123
	

	# get latest forcast
	
	#TODO: check if forcast has been checked for today already, if it has then dont check again
	#TODO: open the last forcast
	latest_forcast = fetch_surf_forecast(TIME_AT_START_OF_DAY, TIME_AT_END_OF_DAY, whitesands_conf.latitude, whitesands_conf.longitude, API_KEY)
	latest_tides = fetch_tide(TIME_AT_START_OF_DAY, TIME_AT_END_OF_DAY, whitesands_conf.latitude, whitesands_conf.longitude, API_KEY)
	# process forcast
	process_forcast(whitesands_conf, latest_forcast, whitesands_conditions)
	print("primary wave energy : ", whitesands_conditions.primary_wave_energy)

	print("swell period: ", latest_forcast['hours'][0]['swellPeriod']['noaa'])
	# save forcast (for debuggin and later for archiving)
	#with open('forcast.json', 'w') as json_file:
	#	json.dump(latest_forcast, json_file, indent=4)
	# save tide (for debuggin and later for archiving)
	#with open('tide.json', 'w') as json_file:
	#	json.dump(latest_tides, json_file, indent=4)
