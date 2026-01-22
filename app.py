from functions import *
import streamlit as st

st.set_page_config(page_title='Toronto Bike Share WebApp', page_icon=':bike:')

station_url = 'https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_status'
latlon_url = 'https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_information'



data_df = get_station_status(station_url)
latlon_df = get_station_latlon(latlon_url)
df = merge_df(data_df, latlon_df)

df = df.drop(columns= ['status', 'traffic', 'is_installed', 'is_renting', 'is_returning', 'last_reported', 'num_bikes_available_types', 'name', 'physical_configuration', 'groups', 'obcn', 'short_name', 'nearby_distance', 'address', 'is_charging_station', 'rental_methods', '_ride_code_support', 'rental_uris', 'post_code', 'altitude', 'is_valet_station', 'cross_street'])

st.markdown('## Toronto Bike Share WebApp')
st.markdown('#### You can track in real time the availability of each Bike Share station in Toronto')
st.markdown('> Toronto\'s bikeshare guidelines say that an electric bike can be dropped at a non-charging station, so when returning an electric bike, the station doesn\'t need to be a charging station')

## General Data
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
                pass

    elif option_selection == 'Return':
        return_address = st.text_input(label='Where are you located ?', value='', type='default', label_visibility='visible')
        return_button = st.button(label='Find me a dock', type='primary')
        if return_button:
            if return_address == '':
                st.badge('Input address not valid', icon=':heavy_exclamation_mark:', color='red')
            else:
                pass

st.dataframe(df)

