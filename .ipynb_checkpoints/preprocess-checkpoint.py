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
import pickle

print(int(round(distance_KM)))

e85_pickles, efuels_pickles = [[] for i in range(2)]
for file in os.listdir("preprocessed_data/pickles"):
    if (file.endswith(".pkl")) & ('e85' in file): e85_pickles.append(file)
    elif (file.endswith(".pkl")) & ('efuels' in file): efuels_pickles.append(file)

#basic steps is that you want to check if pickle exists. if it does, load it to e85_vi.csv, 
e85_matched,efuels_matched = [0,0]
for i in e85_pickles: 
    if (('e85_vi_'+str(int(round(int(round(distance_KM))/1.609)))) in i): 
        selected_e85pickle = i
        
        with open('preprocessed_data/pickles/'+selected_e85pickle,'rb') as pf:
            var = pickle.load(pf)
        print(os.getcwd())
        print(selected_e85pickle)
        var.to_csv('e85_vi.csv')
        #import to e85_vi.csv
        e85_matched=1
        break
if (e85_matched == 0): 
    with open('preprocessed_data/us_counties_2010.json', encoding= "ISO-8859-1") as f:
        gj = geojson.load(f)
    selected_states = ['CA','MN','TX'] #for the purposes of this model, only three states were considered.
    selected_states_fips = ['06','27','48'] #corresponding state FIPS codes
    selected_states_dict = {'06':'CA','27':'MN','48':'TX'}
    repeated_list = ['Orange','Cass','Lake','Trinity','Houston','Polk','Brown','Clay','Jackson','Washington','Martin']

    e85 = pd.read_csv('preprocessed_data/e85_fuel_stations.csv')
    e85['Points'] = list(zip(e85['Longitude'], e85['Latitude']))
    e85 = e85[['Station Name','City','County', 'State','ZIP','Points']]
    e85.groupby('County').count().sort_values(by='City', ascending=False).head(5)
    e85_points = e85['Points']


    geo_df = pd.DataFrame()
    geo_df['points'] = e85_points
    geometry_string = []

    for i,j in tqdm(list(enumerate(e85_points))):
        p = Point(j)
        n_points = 20
        d = 10 * 1000 # meters --- distance in km
        angles = np.linspace(0, 360, n_points)
        polygon = geog.propagate(p, angles, d)
        geometry_string.append(shapely.geometry.Polygon(polygon))

    geo_df['coordinates'] = geometry_string
    geo_df['name'] = e85['County']
    desc = []
    for i in range(geo_df.shape[0]): desc.append('e85 station')
    geo_df['description'] = desc

    boundary = gpd.GeoSeries(cascaded_union(geometry_string))
    boundary.plot()
    boundary = boundary.to_frame()
    plt.figure(figsize=(40,20))
    # plt.show()

    type(boundary)
    boundary

    gdf = GeoDataFrame(geometry=boundary[0])
    gdf['name'] = 'e85_stations'
    gdf
    with open('e85.geojson', 'w') as f:
        dump(gdf, f)

    uscs = gpd.read_file('preprocessed_data/gz_2010_us_050_00_500k/gz_2010_us_050_00_500k.shp')
    # us_county_shapefile['STATEFP'].unique()
    # uscs[(uscs['STATE']=='06') | (uscs['STATE']=='27') | (uscs['STATE']=='48')]
    uscs = uscs[uscs['STATE'].isin(selected_states_fips)]
    #tester.loc[tester['County'].isin(repeated_list), 'County'] = tester['County'] + '_' + tester['State']
    uscs.reset_index(drop=True,inplace=True)
    uscs = uscs.replace({'STATE':selected_states_dict})
    uscs.loc[uscs['NAME'].isin(repeated_list), 'NAME'] = uscs['NAME'] + '_' + uscs['STATE']

    e85_vi = pd.DataFrame(columns = ['county','e85 station','e85_area'])

    geom_p1 = list(uscs['geometry'])
    geom_p8 = list(gdf['geometry'])

    #this is the part that takes ages to run
    for i,g1 in tqdm(enumerate(geom_p1)):
        for j, g8 in enumerate(geom_p8):
            if g1.intersects(g8):
                df1 = pd.DataFrame([[i,j,(g1.intersection(g8).area/g1.area)*100]],columns = ['county','e85 station','e85_area'])
                e85_vi = e85_vi.append(df1)

    inplaced = e85_vi.set_index('county')

    e85_vi = pd.merge(uscs,inplaced,how='outer',left_index=True,right_index=True).fillna(0)
    e85_vi.groupby('NAME').sum().sort_values(by='e85_area',ascending=False).head(10)
    # e85_vi.to_csv('e85_vi.csv')

    dirname = os.path.dirname('preprocess.py')
    filename = os.path.join(dirname, 'preprocessed_data/pickles')
    os.chdir(filename)
    with open('e85_vi_' + str(int(round(int(round(distance_KM))/1.609)))+ '.pkl','wb') as pf:
            pickle.dump(e85_vi,pf,protocol=pickle.HIGHEST_PROTOCOL)
    os.chdir('..')
    os.chdir('..')

for i in efuels_pickles: 
    if (str(int(round(int(round(distance_KM))/1.609))) in i): 
        selected_efuelspickle = i
        with open('preprocessed_data/pickles/'+selected_efuelspickle,'rb') as pf:
            var = pickle.load(pf)
        var.to_csv('efuels_vi.csv')
        efuels_matched=1
        break
if (efuels_matched == 0): 
    
    with open('preprocessed_data/us_counties_2010.json', encoding= "ISO-8859-1") as f:
        gj = geojson.load(f)
    selected_states = ['CA','MN','TX'] #for the purposes of this model, only three states were considered.
    selected_states_fips = ['06','27','48'] #corresponding state FIPS codes
    selected_states_dict = {'06':'CA','27':'MN','48':'TX'}
    repeated_list = ['Orange','Cass','Lake','Trinity','Houston','Polk','Brown','Clay','Jackson','Washington','Martin']

    efuel_stations = pd.read_csv('preprocessed_data/electric_fuel_stations.csv')
    efuel_stations['Points'] = list(zip(efuel_stations['Longitude'], efuel_stations['Latitude']))
    efuel_points = efuel_stations['Points']
    geo_df = pd.DataFrame()
    geo_df['points'] = efuel_points
    geometry_string = []

    for i,j in tqdm(list(enumerate(efuel_points))):
        p = Point(j)
        n_points = 20
        d = distance_KM * 1000 # meters --- 10km
        angles = np.linspace(0, 360, n_points)
        polygon = geog.propagate(p, angles, d)
        geometry_string.append(shapely.geometry.Polygon(polygon))

    geo_df['coordinates'] = geometry_string
    geo_df['name'] = efuel_stations['County']
    desc = []
    for i in range(geo_df.shape[0]): desc.append('efuel station')
    geo_df['description'] = desc
    
    
    boundary = gpd.GeoSeries(cascaded_union(geometry_string))
    boundary.plot()
    boundary = boundary.to_frame()
    
    from geopandas import GeoDataFrame
    gdf = GeoDataFrame(geometry=boundary[0])
    gdf['name'] = 'efuel_stations'
    gdf
    with open('efuels.geojson', 'w') as f:
        dump(gdf, f)
    
    uscs = gpd.read_file('preprocessed_data/gz_2010_us_050_00_500k/gz_2010_us_050_00_500k.shp')
    # us_county_shapefile['STATEFP'].unique()
    # uscs[(uscs['STATE']=='06') | (uscs['STATE']=='27') | (uscs['STATE']=='48')]
    uscs = uscs[uscs['STATE'].isin(selected_states_fips)]
    #tester.loc[tester['County'].isin(repeated_list), 'County'] = tester['County'] + '_' + tester['State']
    uscs.reset_index(drop=True,inplace=True)
    uscs = uscs.replace({'STATE':selected_states_dict})
    uscs.loc[uscs['NAME'].isin(repeated_list), 'NAME'] = uscs['NAME'] + '_' + uscs['STATE']
    
    geom_p1 = list(uscs['geometry'])
    geom_p8 = list(gdf['geometry'])
    
    efuels_vi = pd.DataFrame(columns = ['county','electric fuel station','efuels_area'])
    for i,g1 in tqdm(enumerate(geom_p1)):
        for j, g8 in enumerate(geom_p8):
            if g1.intersects(g8):
                df1 = pd.DataFrame([[i,j,(g1.intersection(g8).area/g1.area)*100]],columns = ['county','electric fuel station','efuels_area'])
                efuels_vi = efuels_vi.append(df1)
    inplaced = efuels_vi.set_index('county')
    
    efuels_vi = pd.merge(uscs,inplaced,how='outer',left_index=True,right_index=True).fillna(0)
    efuels_vi.groupby('NAME').sum().sort_values(by='efuels_area',ascending=False).head(10)
    
    dirname = os.path.dirname('preprocess.py')
    filename = os.path.join(dirname, 'preprocessed_data/pickles')
    os.chdir(filename)
    with open('efuels_vi_' + str(int(round(int(round(distance_KM))/1.609)))+ '.pkl','wb') as pf:
            pickle.dump(efuels_vi,pf,protocol=pickle.HIGHEST_PROTOCOL)
    os.chdir('..')
    os.chdir('..')