import folium
from functions import *
import streamlit as st
from streamlit_folium import st_folium


st.set_page_config(page_title='Toronto Bike Share WebApp', page_icon=':bike:', layout='centered')

station_url = 'https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_status'
latlon_url = 'https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_information'



data_df = get_station_status(station_url)
latlon_df = get_station_latlon(latlon_url)
df = merge_df(data_df, latlon_df)

df = df.drop(columns= ['status', 'traffic', 'is_installed', 'is_renting', 'is_returning', 'last_reported', 'num_bikes_available_types', 'name', 'physical_configuration', 'groups', 'obcn', 'short_name', 'nearby_distance', 'address', 'is_charging_station', 'rental_methods', '_ride_code_support', 'rental_uris', 'post_code', 'altitude', 'is_valet_station', 'cross_street'])

st.markdown('## Toronto Bike Share WebApp')
st.markdown('#### You can track in real time the availability of each Bike Share station in Toronto')
st.markdown('> Toronto\'s bikeshare guidelines say that an electric bike can be dropped at a non-charging station, so when returning an electric bike, the station doesn\'t need to be a charging station')

## General Data Display
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label='Currently available bikes', value=sum(df['num_bikes_available']))
    st.metric(label='Currently available mechanical bikes', value=sum(df['mechanical']))
    st.metric(label='Currently available e-bikes', value=sum(df['ebike']))
with col2:
    st.metric(label='Available docks in the city', value=sum(df['num_docks_disabled']))
    st.metric(label='Stations with empty docks', value=sum(df['num_docks_disabled'] > 0))
    st.metric(label='Average bike utilization', value=f"{((df['num_bikes_available'] / df['capacity']).mean()) * 100:.1f}%")
with col3:
    st.metric(label='Total number of stations', value=len(df['num_docks_available']))
    st.metric(label='Full stations', value=sum(df['num_docks_available'] < 1))

## Sidebar Setup
with st.sidebar:
    option_selection = st.segmented_control(label='Are you looking to rent or return a bike ?', options=['Rent', 'Return'], selection_mode='single', default='Rent', label_visibility='visible', width='stretch')
    if option_selection == 'Rent':
        rent_bike_type = st.segmented_control(label='What kind of bikes are you looking to rent ?', options=['Mechanical', 'E-Bike', 'Both'], selection_mode='single', label_visibility='visible', width='stretch')
        rent_address = st.text_input(label='Where are you located ?', value='', type='default', label_visibility='visible')
        rent_button = st.button(label='Find me a bike', type='primary')
        if rent_button:
            if rent_address == '':
                st.badge('Input address not valid', icon='❌', color='red')
            else:
                rent_geocode = geocode(rent_address + ' Toronto Canada')
                if rent_geocode == '':
                    st.badge('Input address not valid', icon='❌', color='red')
                else:
                    st.badge('Input address valid', icon='✔️', color='green')

    elif option_selection == 'Return':
        return_address = st.text_input(label='Where are you located ?', value='', type='default', label_visibility='visible')
        return_button = st.button(label='Find me a dock', type='primary')
        if return_button:
            if return_address == '':
                st.badge('Input address not valid', icon='❌', color='red')
            else:
                return_geocode = geocode(return_address + ' Toronto Canada')
                if return_geocode == '':
                    st.badge('Input address not valid', icon='❌', color='red')
                else:
                    st.badge('Input address valid', icon='✔️', color='green')

## Map Display Before Address
if option_selection == 'Rent' and not rent_button:
    center = (43.65306613746548, -79.38815311015)  # Toronto's center coordinates
    m = folium.Map(location=center, zoom_start=12.5, tiles='Cartodb Positron', height=500)  # Create a map with a grey background

    for _, row in df.iterrows():
        marker_color = get_marker_color(row['num_bikes_available'])
        folium.Circle(location=[row['lat'], row['lon']], radius=2, color=marker_color, popup=folium.Popup(f"Station ID : {row['station_id']}<br>"
                                                                                            f"Total Bikes Available: {row['num_bikes_available']}<br>"
                                                                                            f"Mechanical Bike Available: {row['mechanical']}<br>"
                                                                                            f"eBike Available: {row['ebike']}", max_width=300)).add_to(m)
    st_folium(m, use_container_width=True, height=500)

if option_selection == 'Return' and not return_button:
    center = (43.65306613746548, -79.38815311015)  # Toronto's center coordinates
    m = folium.Map(location=center, zoom_start=12.5, tiles='Cartodb Positron', height=500)  # Create a map with a grey background

    for _, row in df.iterrows():
        marker_color = get_marker_color(row['num_docks_available'])
        folium.Circle(location=[row['lat'], row['lon']], radius=2, color=marker_color, popup=folium.Popup(f"Station ID : {row['station_id']}<br>"
                                                                                            f"Total Bikes Available: {row['num_bikes_available']}<br>"
                                                                                            f"Mechanical Bike Available: {row['mechanical']}<br>"
                                                                                            f"eBike Available: {row['ebike']}", max_width=300)).add_to(m)
    st_folium(m, use_container_width=True, height=500)

## Map Display After Address
if rent_button:
    if rent_address != '':
        if rent_geocode != '':
            # fonction qui cherche le plus proche
            rent_center = rent_geocode
            rent_m = folium.Map(location=rent_center, zoom_start=12.5, tiles='Cartodb Positron', height=500)

            for _, row in df.iterrows():
                marker_color = get_marker_color(row['num_bikes_available'])
                folium.Circle(location=[row['lat'], row['lon']], radius=2, color=marker_color, popup=folium.Popup(f"Station ID : {row['station_id']}<br>"
                                                                                                    f"Total Bikes Available: {row['num_bikes_available']}<br>"
                                                                                                    f"Mechanical Bike Available: {row['mechanical']}<br>"
                                                                                                    f"eBike Available: {row['ebike']}", max_width=300)).add_to(rent_m)
            folium.Marker(location=rent_geocode, popup='You are here', icon=folium.Icon(color='blue', icon='person', prefix='fa'))
            st_folium(rent_m, use_container_width=True, height=500)