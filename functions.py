from geopy.geocoders import Nominatim
import streamlit as st
import datetime as dt  # Import datetime for working with dates and times
import pandas as pd  # Import pandas for data manipulation
import requests  # Import requests for making HTTP requests
import urllib  # Import module for working with URLs
import json  # Import module for working with JSON data

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
    if location == '':
        return ''
    else:
        return((location.latitude, location.longitude))