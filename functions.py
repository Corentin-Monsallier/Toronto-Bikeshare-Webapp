from geopy.exc import GeocoderUnavailable, GeocoderTimedOut
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

@st.cache_resource
@st.cache_data 
def get_station_status(url):
    with urllib.request.urlopen(url) as data_url:  # Open the URL
        data = json.loads(data_url.read().decode())  # Read and decoded the JSON data
    
    df = pd.DataFrame(data['data']['stations'])  # Convert the json data into a dataframe
    df = df[df['is_renting'] == 1]  # Filter out the stations that are not renting
    df = df[df['is_returning'] == 1]  # Filter out the stations that are not returning
    df = df.drop_duplicates(['station_id', 'last_reported'])  # Remove duplicated records

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

def get_geolocator():
    return Nominatim(
        user_agent="Toronto-BikeShare-Webapp",
        timeout=10
    )
def geocode(address):
    geolocator = get_geolocator()
    try:
        location = geolocator.geocode(address)
        if location is None:
            return None
        return (location.latitude, location.longitude)
    except (GeocoderUnavailable, GeocoderTimedOut):
        return None


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

def reset_rent():
    reset_rent_address()
    reset_rent_geocode()
    reset_rent_search()

def reset_rent_address():
    st.session_state.rent_address_input = ''
def reset_rent_geocode():
    st.session_state.rent_geocode = None
def reset_rent_search():
    st.session_state.search_active = False

def reset_return():
    reset_return_address()
    reset_return_geocode()
    reset_return_geocode()

def reset_return_address():
    st.session_state.return_address_input = ''
def reset_return_geocode():
    st.session_state.return_geocode = None
def reset_return_search():
    st.session_state.search_active = False

def osrm(chosen_station, user_position):
    coord_start = f'{user_position[1]},{user_position[0]}'
    coord_end = f'{chosen_station[2]},{chosen_station[1]}'
    profile = 'walking'
    url = f'http://router.project-osrm.org/route/v1/{profile}/{coord_start};{coord_end}?geometries=geojson'

    r = requests.get(url)
    json_route = r.json()
    coord_path = json_route['routes'][0]['geometry']['coordinates']
    duration = round(json_route['routes'][0]['duration'] / 60, 1)
    distance = json_route['routes'][0]['distance']

    coordinates = []
    for i in range(len(coord_path)):
        coordinates.append([coord_path[i][1], coord_path[i][0]])
    
    return coordinates, distance, duration

def get_dock_availability(latlon, df):
    df_return = df
    df_return['distance'] = ''
    for i in range(len(df_return)):
        dist = geodesic(st.session_state.return_geocode, (df_return['lat'][i], df_return['lon'][i])).km
        df_return.loc[i, ['distance']] = dist
    chosen_station = choose_station(df_return)
    return chosen_station
