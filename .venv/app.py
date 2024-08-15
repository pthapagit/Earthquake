import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

URL = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson'


# Get data from earthquake.usgs.gov
def get_data():
    response = requests.get(URL)
    geo_data = response.json()
    earthquake_features = geo_data['features']
    earthquake_data_list = []
    for item in earthquake_features:
        extract_data = {'Mag': item["properties"]["mag"],
                        "Location": item["properties"]["place"],
                        "longitude": item["geometry"]["coordinates"][0],
                        "latitude": item["geometry"]["coordinates"][1]}
        earthquake_data_list.append(extract_data)
    return earthquake_data_list


# Export to csv file
def generate_file(data):
    try:
        df = pd.DataFrame(data[:5])
        df.to_csv("Earthquake.csv", index=False)
    except FileNotFoundError as e:
        print("Error while exporting file", {e})
    return "File exported"


# Create a Pandas Dataframe
def create_DF(geo_earthquake_data):
    df = pd.DataFrame(geo_earthquake_data)
    return df


# Create a map centered around the average latitude and longitude
def create_map(earthquake_df):
    center_lat = earthquake_df['latitude'].mean()
    center_long = earthquake_df['longitude'].mean()

    m = folium.Map(location=[center_lat, center_long], zoom_start=3)

    # Add markers to the map
    for index, row in earthquake_df.iterrows():
        folium.Circle(
            location=[row['latitude'], row['longitude']],
            popup=f"Mag: {row['Mag']}<br>Location: {row['Location']}",
            radius=row['Mag'] * 20000.0,
            tooltip=f"Loc: {row['Location']}| Mag: {row['Mag']}",
            color='crimson',
            fill=True,
            fill_color='crimson'
        ).add_to(m)
    return m


st.title("Global Earthquake Map")

earthquake_data = get_data()

generate_file(earthquake_data)

earthquake_DF = create_DF(earthquake_data)
max_magnitude_data = max(earthquake_DF['Mag'])
max_mag = st.slider("Magnitude:", 0.0, max_magnitude_data, 0.5)
mag_filtered_df = earthquake_DF[earthquake_DF['Mag'] <= max_mag]
map_layout = create_map(mag_filtered_df)

# call to render Folium map in Streamlit
st_folium(map_layout, width=800)
