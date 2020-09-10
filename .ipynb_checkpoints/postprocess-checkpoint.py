import os, geojson, multiprocessing, datetime, time, geog, json, folium
from shapely.geometry import shape, Point, Polygon
from shapely.ops import cascaded_union
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt
import branca.colormap as cm
import concurrent.futures
from geojson import dump
import geopandas as gpd
import shapely.geometry
from tqdm import tqdm
import pandas as pd
import numpy as np

with open('preprocessed_data/us_counties_2010.json', encoding= "ISO-8859-1") as f:
    gj = geojson.load(f)
selected_states = ['CA','MN','TX'] #for the purposes of this model, only three states were considered.
selected_states_fips = ['06','27','48'] #corresponding state FIPS codes
selected_states_dict = {'06':'CA','27':'MN','48':'TX'}

visual_df = pd.read_csv('optimisation_data/visual_df.csv')
visual_df.drop(visual_df.columns[0], axis=1,inplace=True)

selected_states_pattern = '|'.join(selected_states)
selected_states_pattern

visual_df['County']=np.where(visual_df['County'].str.contains(selected_states_pattern) ,visual_df['County'].str.replace(" ", "_"), visual_df['County'] + '_' + visual_df['State'])

with open('preprocessed_data/us_counties_2010.json', encoding = "ISO-8859-1") as f:
    gj = geojson.load(f)
    
cookie = gpd.GeoDataFrame(gj['features'])
for i in tqdm(range(cookie.shape[0])):
    cookie['properties'][i]['NAME'] = cookie['properties'][i]['NAME'].replace('_',' ')
    cookie['properties'][i]['STATE'] = cookie['properties'][i]['STATE'].replace('06','CA')
    cookie['properties'][i]['STATE'] = cookie['properties'][i]['STATE'].replace('27','MN')
    cookie['properties'][i]['STATE'] = cookie['properties'][i]['STATE'].replace('48','TX')
    if cookie['properties'][i]['STATE'] in selected_states:
        cookie['properties'][i]['NAME'] = cookie['properties'][i]['NAME'] + '_' + cookie['properties'][i]['STATE']
        
visual_dict = visual_df.set_index('County').T.to_dict()

counties_list = list(visual_df['County'])
counter = []
for i,j in tqdm(enumerate(gj['features'])):
    if gj['features'][i]['properties']['NAME'] in counties_list:
        counter.append(1)
        gj['features'][i]['properties'].update(visual_dict[gj['features'][i]['properties']['NAME']])
        
print('10th quantile: {}'.format(visual_df.annual_ghg_emissions.quantile(0.1)))
print('20th quantile: {}'.format(visual_df.annual_ghg_emissions.quantile(0.2)))
print('30th quantile: {}'.format(visual_df.annual_ghg_emissions.quantile(0.3)))
print('40th quantile: {}'.format(visual_df.annual_ghg_emissions.quantile(0.4)))
print('50th quantile: {}'.format(visual_df.annual_ghg_emissions.quantile(0.5)))
print('60th quantile: {}'.format(visual_df.annual_ghg_emissions.quantile(0.6)))
print('70th quantile: {}'.format(visual_df.annual_ghg_emissions.quantile(0.7)))
print('80th quantile: {}'.format(visual_df.annual_ghg_emissions.quantile(0.8)))
print('90th quantile: {}'.format(visual_df.annual_ghg_emissions.quantile(0.9)))

visual_df.groupby('State').sum()

with open("state_output.js", 'w') as file:
    file.write('var statesData = ' +  str(gj))