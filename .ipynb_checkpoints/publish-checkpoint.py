import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
import pandas as pd
import numpy as np
import webbrowser
import feather
import time 
import os

pd.set_option('display.float_format', '{:.2f}'.format)
pd.options.mode.chained_assignment = None
selected_states = ['CA','TX','MN']

st.markdown('## *How can BioFuels Complement Fleet Electrification?*')
st.markdown('### A Study of Transport Emissions in the United States')


st.markdown('In order to fully understanding the relevant details behind the entire project, the reader is directed to the previous manuscript:')
link1 = '[IEMS 394 BioFuels Github](https://github.com/saif1457/biofuels)'
st.markdown(link1,unsafe_allow_html=True)
st.markdown('This repository includes the manuscript outlines motivations, considerations and assumptions, as well as clarifying nuance in future developments.')
link2 = '[IEMS 394 BioFuels Manuscript](https://github.com/saif1457/biofuels/blob/master/tex/biofuels.pdf)'
st.markdown(link2, unsafe_allow_html=True)
st.markdown('In order to use this tool, please select the parameters in the left hand sidebar. This will set the parameters for this optimisation run.')

#SIDE BAR
ghg_reductions = st.sidebar.slider(
    'Select a GHG emission reduction target:',
    0.0, 100.0, 25.0, 0.5
)
dist = st.sidebar.slider(
    'Select a driving distance from E85/EV fuel stations (miles):',
    0.0, 20.0, 6.0, 0.5
)
D = (ghg_reductions/100)
distance_KM = dist*1.609

if st.button('Run Optimisation'):
    with st.spinner("All engines running"):
        
        try: 
            st.markdown('Pre-processing starting...')
            exec(open('preprocess.py').read())
            st.markdown('Pre-processing completed! **(1/3)**')
        except:
            st.write('There was an error with Preprocess.py. Speak to your friendly devs.')

        try:
            st.markdown('Optimisation starting...')
            exec(open('optimisation.py').read())
            st.markdown('Optimisation completed! **(2/3)**')
        except:
            st.write('There was an error with preprocess.py. Yikes - who you gonna call? That\'s right, your friend devs.')

        try:
            st.markdown('Post-processing starting...')
            exec(open('postprocess.py').read())
            st.markdown('Post-processing completed! **(3/3)**')
        except:
            st.write('There was an error with preprocess.py. Reach out to your friendly devs.')
        
        st.success('All systems running operationally')
filename = '[JS BioFuels Visualisation](file:///'+os.getcwd()+'/biofuels.html)'
st.markdown(filename, unsafe_allow_html=True)    

vdf = pd.read_csv('./optimisation_data/visual_df.csv')
del vdf['Unnamed: 0']
readFrame = pd.read_feather('./vdf', use_threads=True);
vdf = vdf.merge(readFrame)


ca_vdf = vdf[vdf['State']=='CA']
tx_vdf = vdf[vdf['State']=='TX']
mn_vdf = vdf[vdf['State']=='MN']

# # Add a placeholder
# latest_iteration = st.empty()
# bar = st.progress(0)

# for i in range(100):
#   # Update the progress bar with each iteration.
#   latest_iteration.text(f'Iteration {i+1}')
#   bar.progress(i + 1)
#   time.sleep(0.1)
st.write('In adapting the optimisation model to include simulated increases for residential charging ability, it is apparent that overall EV allocation steeply increases. Before the optimisation was updated, the percentage split across all three allocations was (BEV: 15.43, FFV: 8.88, SIDI: 75.68), and after the update, BEV almost doubled (BEV: 33.51, FFV: 6.79, SIDI: 59.68). Consequently, FFV allocation decreased, which follows from the heavy intersection of areas where EV and FFV infrastructure has been simultaneously been developed and made available. Given the preference for EV over FFV when a free choice can be made, driven by lower emission factors, FFV allocations decline. As a collorary, SIDI allocations have been diminished by over 15%, as previously untapped residential charging faciities are added to counties without public EV station infrastructure.')
st.markdown('## State Analysis')

#plot various graphs
sns.regplot(ca_vdf['annual_ghg_emissions'],ca_vdf['total_vehicle_count']).set_title("CA Annual GHG emissions vs Total Vehicles")
st.pyplot()

sns.regplot(mn_vdf['annual_ghg_emissions'],mn_vdf['total_vehicle_count']).set_title("MN Annual GHG emissions vs Total Vehicles")
st.pyplot()

sns.regplot(tx_vdf['annual_ghg_emissions'],tx_vdf['total_vehicle_count']).set_title("TX Annual GHG emissions vs Total Vehicles")
st.pyplot()



st.write('Turning attention to answering the biofuels/EV complement on a county basis, particularly interesting counties within each state will be examined in turn.')

# ru = pd.read_csv('preprocessed_data/rural_urban.csv')
# del ru['Note']
# ru = ru[ru.State.isin(selected_states)]
# ru.rename(columns = {'2015 Geography Name':'County','2010 Census \nPercent Rural' : 'pct_rural',
#                     '2010 Census Total Population':'census_totpop', '2010 Census Rural Population':'census_rurpop',
#                     '2010 Census Urban Population':'census_urbpop'},inplace=True)

# ru.County = ru.County.str.replace(' County, Texas','')
# ru.County = ru.County.str.replace(' County, California','')
# ru.County = ru.County.str.replace(' County, Minnesota','')

# #cleaning up the document here to ensure that we have the right names
# repeated_list = ['Orange','Cass','Lake','Trinity','Houston','Polk','Brown','Clay','Jackson','Washington','Martin']
# ru.loc[ru['County'].isin(repeated_list), 'County'] = ru['County'] + ' ' + ru['State']

# #checking if the sets are the same
# misfits = set(ru.County).symmetric_difference(set(vdf.County))
# len(misfits)
# vdf = vdf.merge(ru)
# vdf['census_totpop'] = vdf['census_totpop'].apply(lambda x: x.replace(',','')).astype(int)
# vdf['census_urbpop'] = vdf['census_urbpop'].apply(lambda x: x.replace(',','')).astype(int)
# vdf['census_rurpop'] = vdf['census_rurpop'].apply(lambda x: x.replace(',','')).astype(int)

# evi = pd.read_csv('efuels_vi.csv')
# del evi['Unnamed: 0']
# evi.NAME = evi.NAME.str.replace('_',' ')
# evi = evi[['NAME','efuels_area']]
# vdf = vdf.merge(evi, left_on='County',right_on='NAME')
# vdf.drop('NAME', axis=1,inplace=True)
# vdf['pop_density'] =vdf['census_totpop']/vdf['census_area']

st.markdown('### Comparing the mean values across the states')
a = pd.Series(vdf.mean(), name='overall_mean')
b = pd.Series(ca_vdf.mean(), name='mn_mean')
c = pd.Series(tx_vdf.mean(), name='tx_mean')
d = pd.Series(mn_vdf.mean(), name='ca_mean')
pd.DataFrame([a,b,c,d]).T



# vdf['pop_density'].corr(vdf['efuels_area'])
# vdf['pop_density'].corr(vdf['pct_rural'])
# st.write('Running a linear regression between the population density and coverage of EV charging infrastructure, both public and residential, there is a slight positive correlation (r=0.48)')
# from sklearn.linear_model import LinearRegression
# X = vdf['efuels_area'].values.reshape(-1, 1)  # values converts it into a numpy array
# y = vdf['pop_density'].values.reshape(-1, 1)  # -1 means that calculate the dimension of rows, but have 1 column

# linear_regressor = LinearRegression()  # create object for the class
# linear_regressor.fit(X, y)  # perform linear regression
# y_pred = linear_regressor.predict(X)  # make predictions
# plt.scatter(X, y)
# plt.plot(X, y_pred, color='red')
# st.pyplot()

st.markdown('#### San Francisco, CA')
st.write('The above outlier is San Francisco, and this make sense given that across the analysed states, this is definitely the biggest city/county. San Francisco County (CA) is home to the city of San Francisco, which stands alongside New York and Chicago as the nation\'s three major urban hubs. Due to being on a peninsula with limited space (the entire county is only 47 square miles) and the centre of entreprenuerial life in the US, it make sense that San Francisco County (CA) has the highest population density in this sample. With the dense county included, the correlation between population density and \'efuels_area\' is 0.48, which is moderately positive.')

st.markdown('#### Lubbock, TX')
st.write('Despite being surrounded by many rural counties in north Texas, Lubbock (TX) boasts existing infrastructure for both EV and E85 fuels. Based on its population density, it is classified as a suburuban county, and contains the city of Lubbock. Here, FFV allocations account for almost 30% of total vehicles (29.40%), which is more than 10 times the Texas state average of just 3.41%. [More details about EV - talk about changes during the update] How much of TX mean comes from Lubbock Texas')

st.markdown('#### Bexar, TX')
st.write('Bexar county stands out in terms of emissions, and is classed as an \'urban\' county, containing the city of San Antonio. It has excellent EV infrastructure, which sees 65.70% of the vehicle allocation assigned as electric. It benefitted significantly from residential enhancements, which took the estimated coverage of EV infrastructure from 65% coverage to 90.7%, which puts Bexar in the xx% percentile in Texas')

tx_int = pd.concat([tx_vdf[tx_vdf['County'].isin(['Travis','Harris','Dallas','Bexar'])].T, c],axis=1)
tx_int = pd.concat([tx_vdf[tx_vdf['County'].isin(['Travis','Harris','Dallas','Bexar'])].T, c],axis=1)
tx_int.columns = ['Bexar','Harris','Dallas','Travis','TX_mean']
# tx_int['Travis_diff'] = tx_int.iloc[1:12,3].sub(tx_int['TX_mean'][1:12], axis = 0) 
tx_int


st.markdown('#### Fresno')
st.markdown('#### Los Angeles')
st.markdown('#### San Mateo')
st.markdown('#### San Bernadino')
st.markdown('#### San Joaquin')

