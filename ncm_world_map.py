#!/Users/CN/Documents/Conferences/NCM21/ncm_highlights_article/ncm_highlights/venv python
# ------------------------------------------------------------------------------
# Script name:  ncm_world_map.py
#
# Description:
#               Script to create world map from NCM attendence data
#
# Author:       Caroline Nettekoven, 2020
#
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# Create the environment with virtualenv --system-site-packages . Then, activate the virtualenv and when you want things installed in the virtualenv rather than the system python, use pip install --ignore-installed or pip install -I . That way pip will install what you've requested locally even though a system-wide version exists. Your python interpreter will look first in the virtualenv's package directory, so those packages should shadow the global ones.
# python -m venv --system-site-packages /Users/CN/Documents/Conferences/NCM21/ncm_highlights_article/ncm_highlights/venv
# conda activate geo_env # (Geopandas does not like pip, so had to create a seperate conda environment for geopandas. Fun times!)
#
# Install globally
# pip install pandas
#
# Install only in venv
# pip install -I pycountry_convert
# pip install -I geopy
# pip install -I folium

# ------------------------------------------------------------------------------
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2, country_name_to_country_alpha3
from geopy.geocoders import Nominatim
import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
from PIL import Image
import os
import time
from selenium import webdriver
# ------------------------------ Define helper functions --------------------------------
# function to convert to alpah2 country codes and continents


def get_continent(col):
    try:
        cn_a2_code = country_name_to_country_alpha2(col)
    except:
        cn_a2_code = 'Unknown'
    try:
        cn_continent = country_alpha2_to_continent_code(cn_a2_code)
    except:
        cn_continent = 'Unknown'
    return (cn_a2_code, cn_continent)


def get_alpha3(col):
    try:
        cn_a3_code = country_name_to_country_alpha3(col)
    except:
        cn_a3_code = 'Unknown'
    return (cn_a3_code)


# function to get longitude and latitude data from country name
geolocator = Nominatim(user_agent='ncm_highlights')


def geolocate(country_code, country_name):
    try:
        # Geolocate the center of the country
        loc = geolocator.geocode(country_code)
        # And return latitude and longitude
        return (loc.latitude, loc.longitude)
    except:
        try:
            loc = geolocator.geocode(country_name)
        except:
            # Return missing value
            return np.nan


# ------------------------------------------------------------------------------
# --------------------------------- Get Data -----------------------
file = '/Users/CN/Documents/Conferences/NCM21/ncm_highlights_article/NCMAnonymizedDelegateRegistration.csv'
data = pd.read_csv(file, delimiter=';')
d = {'CountryName': data.COUNTRY.value_counts(
).index, 'Members': data.COUNTRY.value_counts().values, 'Percentage': data.COUNTRY.value_counts().values * 100 / len(data)}
df = pd.DataFrame(data=d)

# Replace Chinas name
df.at[df['CountryName'] == "China, People's Republic of", 'CountryName'] = "China"


# ------------------------------ Get Country and Continent ------------------------------------

df['Country'] = None
df['Continent'] = None
for i in range(len(df)):
    country = get_continent(df.CountryName[i])[0]
    continent = get_continent(df.CountryName[i])[1]
    country_code_alpha3 = get_alpha3(df.CountryName[i])
    df.at[i, 'Country'] = country
    df.at[i, 'Continent'] = continent
    df.at[i, 'Country_A3'] = country_code_alpha3

# ------------------------------ Get Coordinates (Latitude and Longitude) ------------------------------------
df['Latitude'] = None
df['Longitude'] = None
for i in range(len(df)):
    coordinates = geolocate(df.CountryName[i], df.Country[i])
    Latitude = coordinates[0]
    Longitude = coordinates[1]
    df.at[i, 'Latitude'] = Latitude
    df.at[i, 'Longitude'] = Longitude


# ------------------------------ Draw world map ------------------------------------

# Create a world map to show distributions of users
# empty map
world_map = folium.Map(tiles="cartodbpositron")
marker_cluster = MarkerCluster().add_to(world_map)


# for each coordinate, create circlemarker of user percent
for i in range(len(df)):
    lat = df.at[i, 'Latitude']
    long = df.at[i, 'Longitude']
    radius = 5
    popup_text = """Country : {}<br>
                    Members : {}<br>"""
    popup_text = popup_text.format(df.at[i, 'Country'],
                                   df.at[i, 'Members']
                                   )
    folium.CircleMarker(location=[
        lat, long], radius=radius, popup=popup_text, fill=True).add_to(marker_cluster)

# show the map
world_map


# ------------------------------ Draw NEW world map WITHOUT nonmember states ------------------------------------

# ------------------------------ Remove all countries that have no members ----------
# We import the geoJSON file.
world_geo = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json'


# We read the file and print it.
geoJSON_df = gpd.read_file(world_geo)
geoJSON_df.head()

# Next we grab the states and put them in a list and check the length.
geoJSON_states = list(geoJSON_df.id.values)
len(geoJSON_states)

# Let's check which states are missing.
missing_states = np.setdiff1d(geoJSON_states, df.Country_A3.values
                              )
missing_states

# keep_states = [g for g, G in enumerate(
#     geoJSON_states) if G not in missing_states]

# geoJSON_df_clean = geoJSON_df.loc[keep_states]


# ------------------------------ Set non-member states to zero ------------------------------------
# intialise data of lists.
additional_entries = {'CountryName': None,
                      'Members': np.nan,
                      'Percentage': np.nan,
                      'Country': None,
                      'Continent': None,
                      'Country_A3': missing_states,
                      'Latitude': None,
                      'Longitude': None}

# Create DataFrame
df2 = pd.DataFrame(additional_entries)

df = df.append(df2, ignore_index=True)


# ------------------------------ Plot with bins ------------------------------------

m = folium.Map()
_, threshold_scale = pd.qcut(df["Members"], q=3, retbins=True)
threshold_scale = list(threshold_scale)
threshold_scale = [1.0, 20, 40, 60, 80, 100, 400.0]
folium.Choropleth(
    geo_data=world_geo,
    name="choropleth",
    data=df,
    columns=["Country_A3", "Members"],
    key_on="feature.id",
    fill_color="YlGn",
    # fill_color="GnBu",
    fill_opacity=0.7,
    line_opacity=0.1,
    legend_name="Members",
    nan_fill_color='white',
    nan_fill_opacity=0.3,
    # bins=6,
    # threshold_scale=[1, 53, 105, 157, 208, 260, 312],
    threshold_scale=threshold_scale,
    # threshold_scale=100
).add_to(m)

folium.LayerControl().add_to(m)


# m

m.save('/Users/CN/Documents/Conferences/NCM21/ncm_highlights_article/ncm_members_map_bins.html')


# ------------------------------ Plot with log10 ------------------------------------

df["Members_log10"] = np.log10(df["Members"])

m = folium.Map()
folium.Choropleth(
    geo_data=world_geo,
    name="choropleth",
    data=df,
    columns=["Country_A3", "Members_log10"],
    key_on="feature.id",
    fill_color="YlGn",
    # fill_color="GnBu",
    fill_opacity=0.7,
    line_opacity=0.1,
    legend_name="Members (log10)",
    nan_fill_color='white',
    nan_fill_opacity=0.3,
    # threshold_scale=100
).add_to(m)
m.save('/Users/CN/Documents/Conferences/NCM21/ncm_highlights_article/ncm_members_map_log10.html')


# ------------------------------ Plot with log10 and member numbers ------------------------------------

# location = [41.8772, -87.6102], tiles = 'CartoDB positron', zoom_start = 15
m = folium.Map()

folium.Choropleth(
    geo_data=world_geo,
    name="choropleth",
    data=df,
    columns=["Country_A3", "Members_log10"],
    key_on="feature.id",
    fill_color="YlGn",
    # fill_color="GnBu",
    fill_opacity=0.7,
    line_opacity=0.1,
    legend_name="Members (log10)",
    nan_fill_color='white',
    nan_fill_opacity=0.3,
    # threshold_scale=100
).add_to(m)

# folium.LayerControl().add_to(m)

# marker_cluster = MarkerCluster().add_to(m)
# for each coordinate, create circlemarker of user percent
for i in range(len(df.dropna())):
    lat = df.at[i, 'Latitude']
    long = df.at[i, 'Longitude']
    # radius = 5
    # popup_text = """{}<br>
    #                 {}<br>"""
    # popup_text = popup_text.format(df.at[i, 'Country'],
    #                                round(df.at[i, 'Members'])
    #                                )
    popup_text = """{}"""
    popup_text = popup_text.format(round(df.at[i, 'Members'])
                                   )
    # folium.CircleMarker(location=[
    #     lat, long], radius=radius, popup=popup_text, fill=True).add_to(marker_cluster)
    # folium.Marker(location=[
    #     lat, long], radius=radius, popup=popup_text, fill=True).add_to(marker_cluster)
    # folium.Marker(location=[lat, long],
    #               icon=folium.DivIcon(
    #               html='''{}'''.format(popup_text))
    #               ).add_to(m)
    folium.Marker(location=[lat, long],
                  icon=folium.DivIcon(
        #   icon_size=(100, 100),
        html='''<div style="
                  font-size: 12pt;
                  font-family: serif;
                  color: black; 
                  text-align: center;">
                  {}
                  </div>'''.format(popup_text))
    ).add_to(m)


# m

m.save('/Users/CN/Documents/Conferences/NCM21/ncm_highlights_article/ncm_members_map_log10_with_numbers.html')


# ------------------------------ Plot with log10 and member numbers as pop-up ------------------------------------


m = folium.Map()

folium.Choropleth(
    geo_data=world_geo,
    name="choropleth",
    data=df,
    columns=["Country_A3", "Members_log10"],
    key_on="feature.id",
    fill_color="YlGn",
    # fill_color="GnBu",
    fill_opacity=0.7,
    line_opacity=0.1,
    legend_name="Members (log10)",
    nan_fill_color='white',
    nan_fill_opacity=0.3,
    # threshold_scale=100
).add_to(m)

# folium.LayerControl().add_to(m)

marker_cluster = MarkerCluster().add_to(m)
# for each coordinate, create circlemarker of user percent
for i in range(len(df.dropna())):
    lat = df.at[i, 'Latitude']
    long = df.at[i, 'Longitude']
    # radius = 5
    # popup_text = """{}<br>
    #                 {}<br>"""
    # popup_text = popup_text.format(df.at[i, 'Country'],
    #                                round(df.at[i, 'Members'])
    #                                )
    popup_text = """{}"""
    popup_text = popup_text.format(round(df.at[i, 'Members'])
                                   )
    folium.CircleMarker(location=[
        lat, long], radius=radius, popup=popup_text, fill=True).add_to(marker_cluster)
    # folium.Marker(location=[
    #     lat, long], radius=radius, popup=popup_text, fill=True).add_to(marker_cluster)
    # folium.Marker(location=[lat, long],
    #               icon=folium.DivIcon(icon_size=(100, 100),
    #                                   html='''{}'''.format(popup_text))
    #               ).add_to(m)

# m

m.save('/Users/CN/Documents/Conferences/NCM21/ncm_highlights_article/ncm_members_map_log10_interactive.html')
