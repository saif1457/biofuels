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
st.write('Turning attention to answering the biofuels/EV complement on a county basis, particularly interesting counties within each state will be examined in turn. **All results contained below are conducted with the residential EVSE boost activated, a 6-mile charging station range, and 25% GHG reduction target**. This is reflective of the aims of the original manuscript.')
st.markdown('## California')
st.write('Of the 58 counties in California, every single one of them has a non-zero EV allocation, which provides adequate rationale for California to have the highest BEV allocation within this sample of states. In terms of the biofuels complement: there are no counties have a non-zero FFV allocation where BEV allocation is zero. There is despite 29 or 50% of California’s counties having a non-zero FFV allocation. Again, this provides support for the preference for BEV over FFV allocation due to lower emission factors whenever a free choice is available. Even within these 29 counties, average FFV allocation account for only 10.8% compared against 52.3% BEV and 36.9% SIDI.')
st.markdown('#### San Francisco County, CA')
st.write('A outlier is San Francisco, and this make sense given that across the analysed states, this is definitely the biggest city/county. San Francisco County (CA) is home to the city of San Francisco, which stands alongside New York and Chicago as the nation\'s three major urban hubs. Due to being on a peninsula with limited space (the entire county is only 47 square miles) and the centre of entreprenuerial life in the US, it make sense that San Francisco County (CA) has the highest population density in this sample. With the dense county included, the correlation between population density and \'efuels_area\' is 0.48, which is moderately positive.')

st.markdown('#### Los Angeles County, CA')
st.write('Los Angeles County has the highest population density in California, has the highest GHG emis- sions for the state. The opposite is also true: counties the lowest population densities also have the lowest GHG emissions. For instance, Modoc (CA) is a county with a low population density, and has one of the lowest GHG emissions in the state. This trend is visible despite the fact that Los Angeles (CA) has a (SIDI = 3.2%, BEV = 63%, FFV = 33.8%) split, compared with Modoc (CA) at a (SIDI = 94.7%, BEV = 5.3%, FFV = 0%) split.')

st.markdown('#### San Bernardino County, CA')
st.write('Despite being California’s largest county by census area, San Bernardino County only registers 9th in terms of GHG emissions. This is mostly due to the lower population density and lack of urban center means that it is classified as a suburban county. Despite having only 4.7% rural population and benefiting from the EVSE residential charging boost, it only has a 9.9% EV allocation, 4.3% FFV allocation and 85.9% SIDI allocation. This comes as a surprise, and appears to buck the suburban county trend to have significant (over 10%) EV allocation, but given expansive nature of the county, it also makes sense that lacking sufficient E85 fuel infrastructure means that gas- powered vehicles are more relevant to the possibly longer journeys.')

st.markdown('## Texas')
st.write('Of the 254 counties in Texas, 123 had a non-zero BEV allocation. There are 5 counties in Texas which have FFV allocations where BEV allocations are zero, alluding to the existence of E85 infrastructure where EV infrastructure does not exist. As mentioned previously, these counties have not had an EV coverage boost due to residential charging - which is given only to suburban and urban counties - which means that these counties are rural. Only 2 of these counties - Scurry County and Brown County - accounted for significant FFV allocations (allocations exceeding 10%), compared with 15 with Minnesota, and none in California in the same analysis. This hints to the relatively limited FFV infrastructure in areas without BEV infrastructure.')
st.markdown('#### Lubbock County, TX')
st.write('Despite being surrounded by many rural counties in north Texas, Lubbock (TX) boasts existing infrastructure for both EV and E85 fuels. Based on its population density, it is classified as a suburuban county, and contains the city of Lubbock. Here, FFV allocations account for almost 30% of total vehicles (29.40%), which is more than 10 times the Texas state average of just 3.41%. [More details about EV - talk about changes during the update] How much of TX mean comes from Lubbock Texas')

st.markdown('#### Bexar County, TX')
st.write('Bexar county stands out in terms of emissions, and is classed as an \'urban\' county, containing the city of San Antonio. It has excellent EV infrastructure, which sees 65.70% of the vehicle allocation assigned as electric. It benefitted significantly from residential enhancements, which took the estimated coverage of EV infrastructure from 65% coverage to 90.7%, which puts Bexar in the xx% percentile in Texas')

st.markdown('#### Dallas County, TX')
st.write('Dallas County leads Texas in terms of annual GHG emissions by a significant margin (it outputs over 35% more emissions than second-placed Tarrant County). This is coupled with being home to the City of Dallas, which makes Dallas County an urban county. It comes as a surprise, given this leaderboard, that Dallas County also enjoys one of the nation’s more prominent EV rebate programs, which may contribute to its entirely alternative fuel allocation (98.3% BEV, 1.7% FFV). There are no SIDI allocations in this county. It is possible that the excess of GHG emissions is representative of the population density, which is also the highest in Texas.')

st.markdown('#### Comal County, TX')
st.write('Comal County stands out as an anomaly in the Texas alternative fuel landscape, with over 46.1% of its population rural, it is classified as suburban overall. This leads to the residential EVSE charging boost, and a resultant 41.6% EV presence. However, the reason for its status as an anomaly is because Comal County is one of few counties across the entire sample to have a higher FFV allocation compared to the BEV allocation where both allocations comprise of high values: (BEV: 41.6% vs FFV 46.3%). It also had a 12.10% SIDI presence. This coupling gives support to the idea that biofuel complements can not only overlap areas that also have a EV infrastructure, but aid in decreasing the SIDI requirements.')

st.markdown('## Minnesota')
st.write('Of the 87 counties in Minnesota, 18 have no BEV infrastructure (and correspondingly no allocation). As a corollary, these counties are exclusively rural, since both urban and suburban counties have been given an EV boost to account for residential charging. Across these counties, their allocations average 27.4% FFV and 72.6% SIDI allocations. There are two counties - Waseca County and Cottonwood County - which boast over 60% FFV allocations. Of these 18 counties, 15 counties held significant FFV allocations, over 10%. Other notable counties include:')

st.markdown('#### Ramsey County, MN')
st.write('Ramsey County represents Minnesota’s smallest county by census area, but also contains the City of St. Paul, and overall is the second most populous county in Minnesota. Due to its high population density, it has been classified as an urban county, and it also boasts 100% EV vehicle allocation.')
st.markdown('#### Hennepin County, MN')
st.write('Hennepin County represents Minnesota’s most populous county, containing the City of Minneapo- lis. Due to its high population density, it has been classified as an urban county, and also features an entirely alternative fuel allocation with 91.6% being BEV, and 8.40% being FFV.')
st.markdown('#### St. Louis County, MN')
st.write('St. Louis County is Minnesota’s largest county by census area, and is also home to the City of Duluth along its south-eastern boundary. Despite encompassing this urban centre, the rest of the state is very rural, with a correspondingly low population density. Overall - and due in large part to Duluth - the model parameters classify the state as a suburban county. As a result, the +40% EV coverage boost used to emulate residential EVSEs means that the county now features an increased BEV presence when compared against the original model without this consideration. As a result, St. Louis has a 10.8% BEV presence. The statewide trend of having extensive biofuels / E85 infrastructure continues, with a 3.60% FFV vehicle allocation. The remaining 85.6% is SIDI, which makes sense given the rural nature of upstate St. Louis.')


tx_int = pd.concat([tx_vdf[tx_vdf['County'].isin(['Travis','Harris','Dallas','Bexar'])].T, c],axis=1)
tx_int = pd.concat([tx_vdf[tx_vdf['County'].isin(['Travis','Harris','Dallas','Bexar'])].T, c],axis=1)
tx_int.columns = ['Bexar','Harris','Dallas','Travis','TX_mean']
# tx_int['Travis_diff'] = tx_int.iloc[1:12,3].sub(tx_int['TX_mean'][1:12], axis = 0) 
tx_int
