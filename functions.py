from geopy.geocoders import Nominatim
import streamlit as st
import datetime as dt  # Import datetime for working with dates and times
import pandas as pd  # Import pandas for data manipulation
import requests  # Import requests for making HTTP requests
import urllib  # Import module for working with URLs
import json  # Import module for working with JSON data
import time

from geopy.distance import geodesic  # Import geodesic for calculating distances
from geopy.geocoders import Nominatim  # Import Nominatim for geocoding

@st.cache_data 

def get_station_status(url):
    with urllib.request.urlopen(url) as data_url:  # Open the URL
        data = json.loads(data_url.read().decode())  # Read and decoded the JSON data
    
    df = pd.DataFrame(data['data']['stations'])  # Convert the json data into a dataframe
    df = df[df['is_renting'] == 1]  # Filter out the stations that are not renting
    df = df[df['is_returning'] == 1]  # Filter out the stations that are not returning
    df.drop_duplicates(['station_id', 'last_reported'])  # Remove duplicated records

    df['last_reported'] = pd.to_datetime(df['last_reported'], unit='s', utc=True)  # Convert the timestamps in date and time
    df['current_time'] = data['last_updated']  # Store the API's last updated timestamp
    df['current_time'] = pd.to_datetime(df['last_reported'], unit='s', utc=True)  # Convert the timestamp to a timezone-aware UTC datetime

    df = df.set_index('current_time')  # Use the update time as the DataFrame index

    df = pd.concat([df, df['num_bikes_available_types'].apply(pd.Series)], axis=1)  # Expand the dict of bike types into separate columns and append them to df

    return df  # Return the DataFrame

def get_station_latlon(url):
    with urllib.request.urlopen(url) as latlon_url:  # Open the URL
        data = json.loads(latlon_url.read().decode())  # Read and decoded the JSON data

    df = pd.DataFrame(data['data']['stations'])  # Convert the json data into a dataframe

    return df

def merge_df(df1, df2):
    df = df1.merge(df2, how='left', on='station_id')  # Merge the DataFrames on station_id

    return df

def get_marker_color(available):
    if available > 3:
        return 'green'
    elif 0 < available <= 3:
        return 'orange'
    else:
        return 'red'

def geocode(address):
    geolocator = Nominatim(user_agent='Toronto-BikeShare-Webapp')
    location = geolocator.geocode(address)
    if location == '' or location == None:
        return ''
    else:
        return((location.latitude, location.longitude))

def choose_station(df):
    chosen_station = []
    mask = df['distance'] == df['distance'].min()

    chosen_station.append(df.loc[mask, 'station_id'].iloc[0])
    chosen_station.append(df.loc[mask, 'lat'].iloc[0])
    chosen_station.append(df.loc[mask, 'lon'].iloc[0])

    return chosen_station

def get_bike_availability(latlon, df, input_bike_modes):
    df_rent = df
    df_rent['distance'] = ''
    for i in range(len(df_rent)):
        dist = geodesic(latlon, (df_rent['lat'][i], df_rent['lon'][i])).km
        df_rent.loc[i, ['distance']] = dist

    if input_bike_modes == 'Mechanical':
        df_rent = df_rent[df_rent['mechanical'] > 0]
        chosen_station = choose_station(df_rent)
    if input_bike_modes == 'E-Bike':
        df_rent = df_rent[df_rent['ebike'] > 0]
        chosen_station = choose_station(df_rent)
    elif input_bike_modes == 'Both':
        chosen_station = choose_station(df_rent)

    return chosen_station





def run_osrm(chosen_station, iamhere):
    start = "{},{}".format(iamhere[1], iamhere[0])  # Format the start coordinates
    end = "{},{}".format(chosen_station[2], chosen_station[1])  # Format the end coordinates
    url = 'http://router.project-osrm.org/route/v1/driving/{};{}?geometries=geojson'.format(start, end)  # Create the OSRM API URL

    headers = {'Content-type': 'application/json'}
    r = requests.get(url, headers=headers)  # Make the API request
    print("Calling API ...:", r.status_code)  # Print the status code

    routejson = r.json()  # Parse the JSON response
    coordinates = []
    i = 0
    lst = routejson['routes'][0]['geometry']['coordinates']
    while i < len(lst):
        coordinates.append([lst[i][1], lst[i][0]])  # Extract coordinates
        i = i + 1
    duration = round(routejson['routes'][0]['duration'] / 60, 1)  # Convert duration to minutes

    return coordinates, duration  # Return the coordinates and duration