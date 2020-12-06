import pandas as pd
import numpy as np
import math
import haversine as hs
import requests
import json
from haversine import Unit
import getFlightData

try:  # import tracks from csv
    df_path = pd.read_csv('path.csv')
    df_airSpeed = pd.read_csv('air_speed.csv')
except OSError:
    print("Could not connect to database...")


# calculations and get functions:
def clc_dist_between_2points(lat1, lon1, lat2, lon2):
    coordinate1 = (lat1, lon1)
    coordinate2 = (lat2, lon2)
    dist_metre = hs.haversine(coordinate1, coordinate2, unit=Unit.METERS)
    return dist_metre


def clc_azimuth(lat1, lon1, lat2, lon2):
    dL = lon2 - lon1
    X = math.cos(lat2) * math.sin(dL)
    Y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dL)
    bearing_rad = np.arctan2(X, Y)  # radian
    bearing_deg = ((np.degrees(bearing_rad) + 360) % 360)  # degrees
    return bearing_deg


def get_Aspeed(weight):
    weight_modol = weight - (weight % 50)  # rounding down
    try:
        Aspeed = int(df_airSpeed['air speed'][df_airSpeed[df_airSpeed['weight'] == weight_modol].index])  # air speed in csv
    except:
        print("fuel is to low- good luck coming back")
        Aspeed = 0
    return Aspeed


def get_weather(lat, lon, request):
    api_key = "c80b790a2fd8650bc690c41a4c001f0a"
    url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, api_key)
    response = requests.get(url)
    data = json.loads(response.text)
    weather_request = data["current"][request]
    return weather_request


def clc_Gspeed(az, wind_speed, wind_deg, Aspeed):
    Gspeed = Aspeed + wind_speed * math.cos((wind_deg + 180) - az)  #pleas confirm me
    return Gspeed
# add yaw


'''main function:
- calculate time of flight in each leg- 
    get the coordinates from DataFrame for a specific leg (leg_number). using our function we clc the distance, az, and high difference. using the get_weather function for wind information we clc the true speed of the aircraft (ground speed).
    we have 2 options- climbing takes more time then flying between the two points. in this case we will climb in place when getting to point b, and the time of flight in this leg will be the time of climbing. otherwise, the time will be determine by the time of flight between two coordinates.
- add all our calculations to path.csv'''


def clc_leg_FlightTime_FuelWeist(leg_number, wind_ref_point, aircraftType, current_fuel):
    aircraft_weight = 10  # (need to add aircraft weight by aircraft type)
    weight_tot = current_fuel + aircraft_weight  # (need to add aircraft weight by aircraft type)

    distance = clc_dist_between_2points(df_path['lat_a'][leg_number], df_path['lon_a'][leg_number], df_path['lat_b'][leg_number], df_path['lon_b'][leg_number])
    high_diff = df_path['high_b(m)'][leg_number] - df_path['high_a(m)'][leg_number]
    az = clc_azimuth(df_path['lat_a'][leg_number], df_path['lon_a'][leg_number], df_path['lat_b'][leg_number], df_path['lon_b'][leg_number])
    startTemp, endTemp = get_weather(df_path['lat_a'][leg_number], df_path['lon_a'][leg_number], "temp"), get_weather(df_path['lat_b'][leg_number], df_path['lon_b'][leg_number], "temp")

    if high_diff < 0:
        flightPattern = "descend"
    if high_diff > 0:
        flightPattern = "climb"
    # avgROC, avgFC = getFlightData.getFlightLegData(aircraftType, flightPattern, weight_tot, current_fuel, startTemp, endTemp, df_path['high_a(m)'][leg_number], df_path['high_b(m)'][leg_number])
    # avgROC_lev, avgFC_lev = getFlightData.getFlightLegData(aircraftType, ["leveled flight"], weight_tot, current_fuel, startTemp, endTemp, df_path['high_a(m)'][leg_number], df_path['high_b(m)'][leg_number])
    avgROC = 10  ##
    avgFC = 0.007  ##
    avgFC_lev = 0.006  ##

    if (wind_ref_point == 'start'):  # option for later
        wind_speed = get_weather(df_path['lat_a'][leg_number], df_path['lon_a'][leg_number], "wind_speed")
        wind_deg = get_weather(df_path['lat_a'][leg_number], df_path['lon_a'][leg_number], "wind_deg")
    else:
        wind_speed = get_weather(df_path['lat_b'][leg_number], df_path['lon_b'][leg_number], "wind_speed")
        wind_deg = get_weather(df_path['lat_b'][leg_number], df_path['lon_b'][leg_number], "wind_deg")
    Aspeed = get_Aspeed(aircraft_weight + current_fuel)
    Gspeed = clc_Gspeed(az, wind_speed, wind_deg, Aspeed)

    # calculate flight time from a to b
    time_dist = (distance / Gspeed) * 100 / 6  # 6min/100 -- time of flight from point a to b in minutes
    time_alt = high_diff / avgROC  # min -- time to climb or descend from point 1 to point b in minutes
    time_of_leg = max(time_dist, time_alt)

    # Fuel consumption from a to b
    if time_of_leg == time_alt:
        fuel_decrease = avgFC * time_of_leg
    elif time_of_leg == time_dist:
        fuel_decrease = avgFC * time_alt
        fuel_decrease += avgFC_lev * (time_dist - time_alt)
    new_fuel = current_fuel - fuel_decrease
    if new_fuel <= 0:
        print("out of fuel")
        new_fuel = 0

    # add data to dataFrame
    df_path.loc[leg_number, 'dist'] = distance
    df_path.loc[leg_number, 'high_diff'] = high_diff
    df_path.loc[leg_number, 'az'] = az
    df_path.loc[leg_number, 'Gspeed'] = Gspeed
    df_path.loc[leg_number, 'Aspeed'] = Aspeed
    df_path.loc[leg_number, 'time_dist'] = time_dist
    df_path.loc[leg_number, 'time_climb/descend'] = time_alt
    df_path.loc[leg_number, 'time_of_leg'] = time_of_leg
    df_path.loc[leg_number, 'current_fuel'] = new_fuel

    return time_of_leg, new_fuel


def clc_path_FlightTime_FuelWeist(start_fuel, aircraftType):
    leg_number = int(len(df_path['lat_a']))
    wind_ref_point = 'start'  ###
    current_fuel = start_fuel
    total = 0
    for i in range(leg_number):
        time_of_leg, current_fuel = clc_leg_FlightTime_FuelWeist(i, wind_ref_point, aircraftType, current_fuel)
        total += time_of_leg
    # add total time to csv at the last row of time_of_leg
    df_path.loc[leg_number+1, 'time_of_leg'] = total
    df_path.to_csv("path.csv")  #update csv
    return total, current_fuel

# -----------------------------------------------------------------
test_total, test_fuel = clc_path_FlightTime_FuelWeist(550, 'Airbus')
print(test_total, test_fuel)
# verify units between all codes (my code- minutes for time and meter for distance)
# wind calculate reference point add sometime
# yaw (wind)
# start fuel, aircraftType, aircraft_weight - add a csv file
