import math
import folium
from functions import *
import streamlit as st
from streamlit_folium import st_folium


st.set_page_config(page_title='Toronto Bike Share WebApp', page_icon=':bike:', layout='centered')

station_url = 'https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_status'
latlon_url = 'https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_information'

# Initialize Session State to store search results across reruns
if 'rent_geocode' not in st.session_state:
    st.session_state.rent_geocode = None
if 'return_geocode' not in st.session_state:
    st.session_state.return_geocode = None
if 'search_active' not in st.session_state:
    st.session_state.search_active = False

data_df = get_station_status(station_url)
latlon_df = get_station_latlon(latlon_url)
df = merge_df(data_df, latlon_df)

#df = df.drop(columns= ['status', 'traffic', 'is_installed', 'is_renting', 'is_returning', 'last_reported', 'num_bikes_available_types', 'name', 'physical_configuration', 'groups', 'obcn', 'short_name', 'nearby_distance', 'address', 'is_charging_station', 'rental_methods', '_ride_code_support', 'rental_uris', 'post_code', 'altitude', 'is_valet_station', 'cross_street'])

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

## Sidebar Setup
with st.sidebar:
    option_selection = st.segmented_control(label='Are you looking to rent or return a bike ?', options=['Rent', 'Return'], selection_mode='single', label_visibility='visible', width='stretch')
    if option_selection == 'Rent':
        reset_return()
        rent_bike_type = st.segmented_control(label='What kind of bikes are you looking to rent ?', options=['Mechanical', 'E-Bike', 'Both'], selection_mode='single', label_visibility='visible', width='stretch')
        rent_address = st.text_input(label='Where are you located ?', value='', type='default', label_visibility='visible', key='rent_address_input')
        rent_button = st.button(label='Find me a bike', type='primary')
        rent_reset_button = st.button(label='Reset address search', type='primary', on_click=reset_rent)

        if rent_button:
            if rent_bike_type == '' or rent_bike_type == None:
                reset_rent_geocode()
                reset_rent_search()
                st.error('Please choose a bike type')
            if rent_address == '':
                reset_rent_geocode()
                reset_rent_search()
                st.error('Please enter an address')
            else:
                res = geocode(rent_address + ' Toronto Canada')
                if res == '':
                    reset_rent_geocode()
                    st.error('Address not found')
                else:
                    st.session_state.rent_geocode = res
                    st.session_state.search_active = True
                    st.session_state.option = 'Rent'

    elif option_selection == 'Return':
        reset_rent()
        return_address = st.text_input(label='Where are you located ?', value='', type='default', label_visibility='visible', key='return_address_input')
        return_button = st.button(label='Find me a dock', type='primary')
        return_reset_button = st.button(label='Reset address search', type='primary', on_click=reset_return)

        if return_button:
            if return_address == '':
                reset_return_geocode()
                reset_return_search()
                st.error('Please enter an address')
            else:
                res = geocode(return_address + ' Toronto Canada')
                if res == '':
                    reset_return_geocode()
                    st.error('Address not found')
                else:
                    st.session_state.return_geocode = res
                    st.session_state.search_active = True
                    st.session_state.option = 'Return'

## Map Display 
if option_selection == 'Rent' and st.session_state.rent_geocode:
    chosen_station = get_bike_availability(st.session_state.rent_geocode, df, rent_bike_type)
    coordinates, distance, duration = osrm(chosen_station, st.session_state.rent_geocode)
    
    m = folium.Map(location=st.session_state.rent_geocode, zoom_start=15, tiles='Cartodb Positron')
    folium.Marker(location=st.session_state.rent_geocode, popup='You are here', icon=folium.Icon(color='blue', icon='person', prefix='fa')).add_to(m)
    folium.Marker(location=[chosen_station[1], chosen_station[2]], popup='Closest Bike', icon=folium.Icon(color='red', icon='bicycle', prefix='fa')).add_to(m)
    folium.PolyLine(locations=coordinates, color='blue', weight=5).add_to(m)

    st_folium(m, use_container_width=True, height=500, key="rent_map")

    with col3:
        st.metric(label=':green[Travel time (min)]', value=duration)
        if distance >= 1000:
            distance = round(distance / 1000, 1)
            st.metric(label=':green[Travel distance (km)]', value=distance)
        else:
            distance = math.ceil(distance/10) * 10
            st.metric(label=':green[Travel distance (m)]', value=distance)

elif option_selection == 'Return' and st.session_state.return_geocode:
    chosen_station = get_dock_availability(st.session_state.return_geocode, df)
    coordinates, distance, duration = osrm(chosen_station, st.session_state.return_geocode)
    duration = distance * 3600/4000
    
    m = folium.Map(location=st.session_state.return_geocode, zoom_start=15, tiles='Cartodb Positron')
    folium.Marker(location=st.session_state.return_geocode, popup='You are here', icon=folium.Icon(color='blue', icon='person', prefix='fa')).add_to(m)
    folium.Marker(location=[chosen_station[1], chosen_station[2]], popup='Closest Station', icon=folium.Icon(color='red', icon='bicycle', prefix='fa')).add_to(m)
    folium.PolyLine(locations=coordinates, color='blue', weight=5).add_to(m)
    
    st_folium(m, use_container_width=True, height=500, key="return_map")
    
    with col3:
        if distance >= 1000:
            distance = round(distance / 1000, 1)
            st.metric(label=':green[Travel distance (km)]', value=distance)
        else:
            distance = math.ceil(distance/10) * 10
            st.metric(label=':green[Travel distance (m)]', value=distance)

        st.metric(label=':green[Travel time (min)]', value=duration)

else:
    center = (43.65306613746548, -79.38815311015)  # Toronto's center coordinates
    m = folium.Map(location=center, zoom_start=12.5, tiles='Cartodb Positron')  # Create a map with a grey background

    for _, row in df.iterrows():
        count = row['num_bikes_available'] if option_selection == 'Rent' else row['num_docks_available']
        marker_color = get_marker_color(count)

        folium.Circle(
            location=[row['lat'], row['lon']], 
            radius=15, 
            color= marker_color, 
            fill=True, 
            fill_opacity=1, 
            opacity=1, 
            popup=folium.Popup(f"Station: {row['station_id']}<br>Bikes: {row['num_bikes_available']}<br>Docks: {row['num_docks_available']}")
        ).add_to(m)

    st_folium(m, use_container_width=True, height=500, key="main_map")
