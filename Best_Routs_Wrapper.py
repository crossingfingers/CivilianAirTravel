import pandas as pd
# A class to represent a waypoint in a route:


class Waypoint:
    def __init__(self, name, latitude, longitude, altitude):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude

# TODO:suggest changing the flight data in Tagel's code to a similar class, and also add there code for descent

# A class to represent all the data required for Tagel's calculations (except for the waypoints themselves):


class FlightData:
    def __init__(self, wind_reference_point, average_roc, average_fuel_consumption_during_climb,
                 average_fuel_consumption_during_levelled_flight, average_fuel_consumption_during_descent,
                 initial_fuel_amount):
        self.wind_reference_point = wind_reference_point
        self.average_ROC = average_roc
        self.average_fuel_consumption_during_climb = average_fuel_consumption_during_climb
        self.average_fuel_consumption_during_levelled_flight = average_fuel_consumption_during_levelled_flight
        self.average_fuel_consumption_during_descent = average_fuel_consumption_during_descent
        self.initial_fuel_amount = initial_fuel_amount

################################################################################################
# TODO: remove pseudo-code from this point (copy of Tagel's function)
#  after understanding how to import the function from jupiter notebook


def clc_leg_FlightTime_FuelWeist(lat1, lon1, lat2, lon2, h1, h2, wind_ref_point, avgROC, av_feul_climb, av_feul_str,
                                 start_fuel):
    time_of_leg = 1
    current_fuel = 100
    return time_of_leg, current_fuel
# Todo: remove pseudo-code until this point.
################################################################################################
# Input:
###############
# "origin","destination": way-points,containing 4 fields: name,lat,long,alt
# flight_data: containing wind_ref_point, average_ROC, average_fuel_in_climb, average_fuel_in_leveled, initial_fuel
# wanted_routs_number: user defined number of how many routes he wants to receive (optional, default=5)
# csv file with flight routes named "routes.csv". expected format is (each w.p contains 4 fields: name,lat,long,alt):
# route_name | route_priority | 1st w.p | 2nd w.p | 3rd w.p|...| last w.p|
# for priority: The lower the number, the higher the priority ("1" is prior to "2")
##############
# Output:
##############
# print & returns "wanted_routs_number" of routes, sorted primarily by "route_priority" (ascending),
# and secondly by "flight_time" (ascending).
################################################################################################


def get_flight_time_for_route(route: list[Waypoint], flight_data: FlightData):
    time_in_route = 0
    for current_wp, next_wp in zip(route, route[1:]):
        # getting the flight time in the leg, "__" is for ignoring fuel return value:
        time_in_leg, __ = clc_leg_FlightTime_FuelWeist(current_wp.latitude, current_wp.longitude, next_wp.latitude,
                                                       next_wp.longitude, current_wp.altitude, next_wp.altitude,
                                                       flight_data.wind_reference_point, flight_data.average_ROC,
                                                       flight_data.average_fuel_consumption_during_climb,
                                                       flight_data.average_fuel_consumption_during_levelled_flight,
                                                       flight_data.initial_fuel_amount)
        time_in_route += time_in_leg
    return time_in_route


def get_best_routes(origin: Waypoint, destination: Waypoint, flight_data: FlightData, wanted_routs_number=5):
    # import the routes from the csv file
    routes = pd.read_csv('routes.csv')

    # iterating over the routes, summing up the time from "origin" to the beginning of the route,
    # time in route, and time from end of route to "destination":
    for index, route in routes.iterrows():
        # getting a list of only the waypoints of the route, and also first and last w.p:
        waypoint_list = route.drop('route_name', 'route_priority').values.flatten().tolist()
        first_wp_in_route = waypoint_list[0]
        last_wp_in_route = waypoint_list[-1]
        # calculating flight time for the first leg - from origin to 1st w.p in the route:
        # ("__" is for ignoring fuel return value)
        time_from_origin_to_route_start, __ = clc_leg_FlightTime_FuelWeist(origin.latitude, origin.longitude,
                                                                           first_wp_in_route.latitude,
                                                                           first_wp_in_route.longitude,
                                                                           origin.altitude, first_wp_in_route.altitude,
                                                                           flight_data.wind_reference_point,
                                                                           flight_data.average_ROC,
                                                                           flight_data.average_fuel_consumption_during_climb,
                                                                           flight_data.average_fuel_consumption_during_levelled_flight,
                                                                           flight_data.initial_fuel_amount)
        # calculating flight time for the last leg - from last w.p in the route to the destination:
        # ("__" is for ignoring fuel return value)
        time_from_route_end_to_destination, __ = clc_leg_FlightTime_FuelWeist(last_wp_in_route.latitude,
                                                                              last_wp_in_route.longitude,
                                                                              destination.latitude,
                                                                              destination.longitude,
                                                                              last_wp_in_route.altitude,
                                                                              destination.altitude,
                                                                              flight_data.wind_reference_point,
                                                                              flight_data.average_ROC,
                                                                              flight_data.average_fuel_consumption_during_climb,
                                                                              flight_data.average_fuel_consumption_during_levelled_flight,
                                                                              flight_data.initial_fuel_amount)
        # calculating flight time in the route itself:
        time_in_route = get_flight_time_for_route(waypoint_list, flight_data)
        # fill in the flight time that was calculated to the current route:
        routes.at[index, 'flight_time'] = time_from_origin_to_route_start + time_in_route + time_from_route_end_to_destination

    # sorting the routes' datatframe so at the top we have the optimal routes:
    routes.sort_values(by=['priority', 'flight_time'], ascending=[True, True], inplace=True)

    # finished our calculations - printing & returning the optimal routes:
    print(f'To get from {origin} to {destination} the best { wanted_routs_number} routes are:\n {routes.head(wanted_routs_number)}')
    return routes.head(wanted_routs_number)
