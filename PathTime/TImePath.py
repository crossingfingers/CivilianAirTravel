import pandas as pd
import numpy as np
import math
import haversine as hs
import requests
import json
import csv

# import tracks from csv
try:
    df_path = pd.read_csv('path.csv')
    df_airSpeed = pd.read_csv('air_speed.csv')
except OSError:
    print("Could not connect to database...")


# calculations and get functions:

def clc_dist_between_2points(lat1, lon1, lat2, lon2):
    coordinate1 = (lat1, lon1)
    coordinate2 = (lat2, lon2)
    # dist_mil= hs.haversine(coordinate1,coordinate2,unit=Unit.MILES)
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
    return int(df_airSpeed['air speed'][df_airSpeed[df_airSpeed['weight'] == weight_modol].index])  # air speed from csv


def get_weather(lat, lon, request):
    api_key = "c80b790a2fd8650bc690c41a4c001f0a"
    url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, api_key)
    response = requests.get(url)
    data = json.loads(response.text)
    weather_request = data["current"][request]
    return weather_request


# from israely site- not working
url = "https://api.ims.gov.il/v1/Envista/stations"
headers = {'Authorization': 'ApiToken f058958a-d8bd-47cc-95d7-7ecf98610e47'}
response = requests.request("GET", url, headers=headers)
data = json.loads(response.text.encode('utf8'))


# %%

def clc_Gspeed(az, wind_speed, wind_deg, Aspeed):
    Gspeed = Aspeed + wind_speed * math.cos((wind_deg + 180) - az)  # ?need to confirm?
    return Gspeed


# add yaw


'''main function:
- calculate time of flight in each leg- 
    get the coordinates from DataFrame for a specific leg (leg_number). using our function we clc the distance, az, and high difference. using the get_weather function for wind information we clc the true speed of the aircraft (ground speed).
    we have 2 options- climbing takes more time then flying between the two points. in this case we will climb in place when getting to point b, and the time of flight in this leg will be the time of climbing. otherwise, the time will be determine by the time of flight between two coordinates.
- add all our calculations to path.csv'''


def clc_leg_FlightTime_FuelWeist(leg_number, wind_ref_point, aircraftType, current_fuel):  # aircraftType=weight
    distance = clc_dist_between_2points(df_path['lat_a'][leg_number], df_path['lon_a'][leg_number],
                                        df_path['lat_b'][leg_number], df_path['lon_b'][leg_number])
    high_diff = df_path['hight_b(m)'][leg_number] - df_path['hight_a(m)'][leg_number]
    az = clc_azimuth(df_path['lat_a'][leg_number], df_path['lon_a'][leg_number], df_path['lat_b'][leg_number],
                     df_path['lon_b'][leg_number])
    startTemp, endTemp = get_weather(df_path['lat_a'][leg_number], df_path['lon_a'][leg_number], "temp"), get_weather(
        df_path['lat_b'][leg_number], df_path['lon_b'][leg_number], "temp")

    if high_diff < 0
        flightPattern = "decsend"
    if high_diff > 0
        flightPattern = "climb"
    # weight_tot ???
    avgROC, avgFC = getFlightLegData(aircraftType, flightPattern, weight_tot, current_fuel, startTemp, endTemp,
                                     df_path['high_a(m)'][leg_number], df_path['high_b(m)'][leg_number])
    avgROC_lev, avgFC_lev = getFlightLegData(aircraftType, ["leveled flight"], weight_tot, current_fuel, startTemp,
                                             endTemp, df_path['high_a(m)'][leg_number],
                                             df_path['high_b(m)'][leg_number])

    if (wind_ref_point == 'start'):  # option for later
        wind_speed = get_weather(df_path['lat_a'][leg_number], df_path['lon_a'][leg_number], "wind_speed")
        wind_deg = get_weather(df_path['lat_a'][leg_number], df_path['lon_a'][leg_number], "wind_deg")
    else:
        wind_speed = get_weather(df_path['lat_b'][leg_number], df_path['lon_b'][leg_number], "wind_speed")
        wind_deg = get_weather(df_path['lat_b'][leg_number], df_path['lon_b'][leg_number], "wind_deg")
    Aspeed = get_Aspeed(aircraft_weight + start_fuel)
    Gspeed = clc_Gspeed(az, wind_speed, wind_deg, Aspeed)

    # calculate flight time from a to b
    time_dist = (distance / Gspeed) * 100 / 6  # 6min/100 -- time of flight from point a to b
    time_alt = high_diff / avgROC  # min -- time to climb or decsend from point 1 to point b
    time_of_leg = max(time_dist, time_alt)

    # Fuel consumption from a to b
    if time_of_leg == time_alt:
        fuel_decrease = avgFC * time_of_leg
    elif time_of_leg == time_dist:
        fuel_decrease = avgFC * time_alt
        fuel_decrease += avgFC_lev * (time_dist - time_alt)
    current_fuel = start_fuel - fuel_decrease
    # add data to csv
    df = pd.read_csv("path.csv")
    df[leg_number, "dist"] = distance
    df[leg_number, "high_diff"] = high_diff
    df[leg_number, "az"] = az
    df[leg_number, "Gspeed"] = Gspeed
    df[leg_number, "time_dist"] = time_dist
    df[leg_number, "time_climb"] = time_climb
    df[leg_number, "time_of_leg"] = time_of_leg
    df[leg_number, "current_fuel"] = current_fuel
    df.to_csv("path.csv", index=False)

    return time_of_leg, current_fuel


def clc_path_FlightTime_FuelWeist(start_fuel, aircraftType):
    num_legs = int(len(df_path['lat_a']))
    wind_ref_point = 'start'  ####
    start_fuel = 500  # ?start fuel?
    current_fuel = start_fuel
    aircraftType = "Airbus"  ####
    total = 0

    for i in range(num_legs):
        time_of_leg, current_fuel = clc_leg_FlightTime_FuelWeist(i, wind_ref_point, aircraftType, current_fuel)
        total += time_of_leg

    # add total time to csv at the last row of time_of_leg
    df = pd.read_csv("path.csv")
    df[num_legs + 1, "time_of_leg"] = total
    df.to_csv("path.csv", index=False)

    return total, (start_fuel - current_fuel)

# ---------------------------

# yaw (wind)
# start fuel, aircraftType,aircraft_weight - add a csv file
# verify units between all codes




