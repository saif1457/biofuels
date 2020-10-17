# import matplotlib.pyplot as plt
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
def _max_width_():
    max_width_str = f"max-width: 900px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )
_max_width_()

#SIDE BAR
st.sidebar.markdown('In order to use this tool, please select the parameters in the left hand sidebar. This will set the parameters for this optimisation run.')
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

st.sidebar.markdown('#### ')
st.sidebar.markdown('#### ')
st.sidebar.markdown('#### ')
st.sidebar.markdown('#### ')
st.sidebar.markdown('#### ')
st.sidebar.markdown('#### ')
st.sidebar.markdown('#### ')
st.sidebar.markdown('#### ')
st.sidebar.markdown('#### ')
st.sidebar.markdown('#### Credits')
st.sidebar.markdown('In order to fully understanding the relevant details behind the entire project, the reader is directed to the previous manuscript:')
link1 = '[IEMS 394 BioFuels Github](https://github.com/saif1457/biofuels)'
st.sidebar.markdown(link1,unsafe_allow_html=True)
st.sidebar.markdown('This repository includes the manuscript outlines motivations, considerations and assumptions, as well as clarifying nuance in future developments.')
link2 = '[IEMS 394 BioFuels Manuscript](https://github.com/saif1457/biofuels/blob/master/tex/biofuels.pdf)'
st.sidebar.markdown(link2, unsafe_allow_html=True)




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

# vdf = pd.read_csv('./optimisation_data/visual_df.csv')
# del vdf['Unnamed: 0']
# readFrame = pd.read_feather('./vdf', use_threads=True);
# vdf = vdf.merge(readFrame)
vdf = pd.read_feather('./analysed_vdf', use_threads=True);



ca_vdf = vdf[vdf['State']=='CA']
tx_vdf = vdf[vdf['State']=='TX']
mn_vdf = vdf[vdf['State']=='MN']


st.write('In adapting the optimisation model to include simulated increases for residential charging ability, it is apparent that overall EV allocation steeply increases. Before the optimisation was updated, the percentage split across all three allocations was **(BEV: 15.43, FFV: 8.88, SIDI: 75.68)**, and after the update, BEV almost tripled **(BEV: 48.3, FFV: 4.19, SIDI: 47.5)**. Consequently, FFV allocation decreased, which follows from the heavy intersection of areas where EV and FFV infrastructure has been simultaneously been developed and made available. Given the preference for EV over FFV when a free choice can be made, driven by lower emission factors, FFV allocations decline. As a collorary, SIDI allocations have been diminished by almost 30%, as previously untapped residential charging faciities are added to counties without public EV station infrastructure.')
st.write('In this version of the model, FFV has become much less significant element in fuel allocation compared to regular gasoline (SIDI allocation) and electicity. There are specific cases where it makes sense - in rural counties where `travel distance per trip`  may be higher, and critical mass for BEV infrastucture is lacking. In these cases, FFV allocations make sense, since they combine the useful elements of regular gasoline - namely the ease and speed of refueling, and relatively long ranger, with a lower emission factor.')

st.markdown('## State Analysis')
st.markdown('### Comparing the mean values across the states')
st.write('Turning attention to answering the biofuels/EV complement on a county basis, particularly interesting counties within each state will be examined in turn. **All results contained below are conducted with the residential EVSE boost activated, a 6-mile charging station range, and 25% GHG reduction target**. This is reflective of the aims of the original manuscript.')

a = pd.Series(vdf[['annual_ghg_emissions','annual_operating_cost','total_annual_cost','vehicle_pc_BEV','vehicle_pc_FFV','vehicle_pc_SIDI','census_totpop','pct_rural','pop_density']].mean(), name='overall_mean')
b = pd.Series(ca_vdf[['annual_ghg_emissions','annual_operating_cost','total_annual_cost','vehicle_pc_BEV','vehicle_pc_FFV','vehicle_pc_SIDI','census_totpop','pct_rural','pop_density']].mean(), name='mn_mean')
c = pd.Series(tx_vdf[['annual_ghg_emissions','annual_operating_cost','total_annual_cost','vehicle_pc_BEV','vehicle_pc_FFV','vehicle_pc_SIDI','census_totpop','pct_rural','pop_density']].mean(), name='tx_mean')
d = pd.Series(mn_vdf[['annual_ghg_emissions','annual_operating_cost','total_annual_cost','vehicle_pc_BEV','vehicle_pc_FFV','vehicle_pc_SIDI','census_totpop','pct_rural','pop_density']].mean(), name='ca_mean')
pd.DataFrame([a,b,c,d]).T

st.markdown('#### Overall Results')
st.write(vdf[['State','vehicle_pc_BEV','vehicle_pc_FFV','vehicle_pc_SIDI','efuels_area']].groupby(by='State').mean())



choose_state = st.radio("Choose a state to analyse",('California', 'Minnesota', 'Texas'))
if choose_state == 'California':
    st.markdown('## California')
    # sns.regplot(ca_vdf['annual_ghg_emissions'],ca_vdf['total_vehicle_count']).set_title("CA Annual GHG emissions vs Total Vehicles")
    st.pyplot(sns.regplot(ca_vdf['annual_ghg_emissions'],ca_vdf['total_vehicle_count']).set_title("CA Annual GHG emissions vs Total Vehicles"))

    st.write('Of the 58 counties in California, every single one of them has a non-zero EV allocation, which provides adequate rationale for California to have the highest BEV allocation within this sample of states. In terms of the biofuels complement: there are no counties have a non-zero FFV allocation where BEV allocation is zero. There make sense given that there are only 4 or 6% of California\'s counties that have a non-zero FFV allocation. Again, this provides support for the preference for BEV over FFV allocation due to lower emission factors whenever a free choice is available. Even within these 21 counties, average FFV allocation account for only 2.5% compared against 89.67% BEV and 7.85% SIDI.')

    st.markdown('#### San Francisco County, CA')
    st.write('A outlier is San Francisco, and this make sense given that across the analysed states, this is definitely the biggest city/county. San Francisco County (CA) is home to the city of San Francisco, which stands alongside New York and Chicago as the nation\'s three major urban hubs. Due to being on a peninsula with limited space (the entire county is only 47 square miles) and the centre of entreprenuerial life in the US, it make sense that San Francisco County (CA) has the highest population density in this sample. With the dense county included, the correlation between population density and \'efuels_area\' is 0.48, which is moderately positive.')

    st.markdown('#### Los Angeles County, CA')
    st.write('Los Angeles County has the highest population density in California, has the highest GHG emis- sions for the state. The opposite is also true: counties the lowest population densities also have the lowest GHG emissions. For instance, Modoc (CA) is a county with a low population density, and has one of the lowest GHG emissions in the state. This trend is visible despite the fact that Los Angeles (CA) has a (SIDI = 0%, BEV = 100%, FFV = 0%) split, compared with Modoc (CA) at a (SIDI = 94.7%, BEV = 5.3%, FFV = 0%) split.')

    st.markdown('#### San Bernardino County, CA')
    st.write('Despite being California\'s largest county by census area, San Bernardino County registers 4th in terms of GHG emissions. This is mostly due to the lower population density and lack of urban center means that it is classified as a suburban county. Having only 4.7% rural population and benefiting from the EVSE residential charging boost, it has a 89.9% EV allocation, 4.3% FFV allocation and 5.9% SIDI allocation. This comes as a surprise, and appears to buck the suburban county trend to have a significant EV allocation, but given expansive nature of the county, it also makes sense that lacking sufficient E85 fuel infrastructure means that gas- powered vehicles are more relevant to the possibly longer journeys.')

elif choose_state == 'Minnesota':
    st.markdown('## Minnesota')
    sns.regplot(mn_vdf['annual_ghg_emissions'],mn_vdf['total_vehicle_count']).set_title("MN Annual GHG emissions vs Total Vehicles")
    st.pyplot()
    st.write('Of the 87 counties in Minnesota, 42 have FFV allocations that *exceed* their corresponding BEV allocation. The prototypical description of such a county is suburban,  with an average FFV allocation of 31.5%, 60.9% SIDI and just 7.5% BEV. This result aligns with expectations within the context of Minnesota being a core market for biofuels and infrastructure within the US and within this sample.')
    
    st.write('Across Minnesota, 25 counties have no BEV infrastructure (and correspondingly no allocation). As a corollary, these counties are exclusively rural, since both urban and suburban counties have been given an EV boost to account for residential charging. Across these counties, their allocations average 20.51% FFV and 79.5% SIDI allocations. There are two counties - Waseca County and Cottonwood County - which boast over 60% FFV allocations. Of these 25 counties, 16 counties held significant FFV allocations, over 10%. Some notable counties include:')
    st.markdown('#### Waseca County, MN')
    st.write('Despite being surrounded by many rural counties, Waseca (TX) boasts existing infrastructure for both EV and E85 fuels. Based on its population density, it is classified as a rural county. Here, FFV allocations account for almost 70% of total vehicles (68.1%), which is more than 4 times the Minnesota state average of 16.4%. There is no EV component to the allocation, with the remaining 31.9% coming from SIDI vehicles. The FFV allocation stands out significantly, but further examinations lead to the understand that Waseca is outside the top 50% counties by `annual_ghg_emissions` in Minnesota (46th of 87) and is ranked 175th across the sample.')

    st.markdown('#### Ramsey County, MN')
    st.write('Ramsey County represents Minnesota\'s smallest county by census area, but also contains the City of St. Paul, and overall is the second most populous county in Minnesota. Due to its high population density, it has been classified as an urban county, and it also boasts 100% EV vehicle allocation.')
    st.markdown('#### Hennepin County, MN')
    st.write('Hennepin County represents Minnesota\'s most populous county, containing the City of Minneapolis. Due to its high population density, it has been classified as an urban county, and also features an entirely EV allocation with 100.0% being BEV.')
    st.markdown('#### St. Louis County, MN')
    st.write('St. Louis County is Minnesota\'s largest county by census area, and is also home to the City of Duluth along its south-eastern boundary. Despite encompassing this urban centre, the rest of the state is very rural, with a correspondingly low population density. Overall - and due in large part to Duluth - the model parameters classify the state as a suburban county. As a result, the +40% EV coverage boost used to emulate residential EVSEs means that the county now features an increased BEV presence when compared against the original model without this consideration. As a result, St. Louis has a 2.90% BEV presence. The statewide trend of having extensive biofuels / E85 infrastructure continues, with a 3.60% FFV vehicle allocation. The remaining 93.5% is SIDI, which makes sense given the rural nature of upstate St. Louis.')

elif choose_state == 'Texas': 
    st.markdown('## Texas')
    sns.regplot(tx_vdf['annual_ghg_emissions'],tx_vdf['total_vehicle_count']).set_title("TX Annual GHG emissions vs Total Vehicles")
    st.pyplot()
    st.write('Of the 254 counties in Texas, 123 had a non-zero BEV allocation. There are 3 counties in Texas which have FFV allocations where BEV allocations are zero, alluding to the existence of E85 infrastructure where EV infrastructure does not exist. As mentioned previously, these counties have not had an EV coverage boost due to residential charging - which is given only to suburban and urban counties - which means that these counties are rural. Only 2 of these counties - Atascosa County and Polk County - accounted for significant FFV allocations, compared with 16 with Minnesota, and none in California in the same analysis. This hints to the relatively limited FFV infrastructure in areas without BEV infrastructure.')


    # st.markdown('#### Bexar County, TX')
    # st.write('Bexar county stands out in terms of emissions, and is classed as an \'urban\' county, containing the city of San Antonio. It has excellent EV infrastructure, which sees 65.70% of the vehicle allocation assigned as electric. It benefitted significantly from residential enhancements, which took the estimated coverage of EV infrastructure from 65% coverage to 90.7%.')

    st.markdown('#### Dallas County, TX')
    st.write('Dallas County leads Texas in terms of annual GHG emissions by a significant margin (it outputs over 35% more emissions than second-placed Tarrant County). This is coupled with being home to the City of Dallas, which makes Dallas County an urban county. It comes as a surprise, given this leaderboard, that Dallas County also enjoys one of the nation\'s more prominent EV rebate programs, which may contribute to its entirely alternative fuel allocation (100% BEV, 0% FFV). There are no SIDI allocations in this county. It is possible that the excess of GHG emissions is representative of the population density, which is also the highest in Texas.')

    st.markdown('#### Comal County, TX')
    st.write('Comal County stands out as an anomaly in the Texas alternative fuel landscape, with over 46.1% of its population rural, it is classified as suburban overall. This leads to the residential EVSE charging boost, and a resultant 41.6% EV presence. However, the reason for its status as an anomaly is because Comal County is one of few counties across the entire sample to have a higher FFV allocation compared to the BEV allocation where both allocations comprise of high values: (BEV: 41.6% vs FFV 46.3%). It also had a 12.10% SIDI presence. This coupling gives support to the idea that biofuel complements can not only overlap areas that also have a EV infrastructure, but aid in decreasing the SIDI requirements.')

state_dict = {'Minnesota':'MN','California':'CA','Texas':'TX'}
choose_state = choose_state.replace('Minnesota','MN')
choose_state = choose_state.replace('California','CA')
choose_state = choose_state.replace('Texas','TX')

if choose_state == 'CA':
    default_selection = ['San Francisco','Los Angeles','San Bernardino']
elif choose_state == 'TX':
    default_selection = ['Bexar','Dallas','Comal','Austin','Travis']
elif choose_state == 'MN':
    default_selection = ['Ramsey','Hennepin','St. Louis','Waseca']

st.success('#### New Feature: Ranking Engine')
st.write('Using a ranking system makes it easier for viewers to make comparisons between relative datasets. First `globalrank` gives the county\'s relative position within the entire sample, providing critical context. This is accompanied by `staterank`, which summarises the county\'s position within its own state.')

# possible_counties = list(vdf[vdf['State']==choose_state]['County'])
county_selection = st.multiselect('Select counties within '+choose_state+':', list(vdf[vdf['State']==choose_state]['County']),default_selection)


# vdf.style.set_properties(**{'background-color': 'red'}, subset=['vehicle_pc_BEV'])
show_multi = vdf[vdf['County'].isin(county_selection)][['County','State','ghg_globalrank','ghg_staterank','popden_globalrank','popden_staterank','censusarea_globalrank','censusarea_staterank','vehicle_pc_BEV','vehicle_pc_FFV','vehicle_pc_SIDI']]
show_multi.set_index('County',inplace=True)
show_multi

# def highlight_first(value):
#     color = "yellow" if value == 0 else "white"
#     return "background-color: %s" % color


# grid = np.arange(0, 100, 1).reshape(10, 10)
# df = pd.DataFrame(grid)
# st.dataframe(df.style.applymap(highlight_first))

analysis_multi = st.multiselect('Select analysis:',['Rank by GHG output','Rank by Census Area','Rank by Pop Density'])
if 'Rank by GHG output' in analysis_multi:
    st.markdown('##### Rank by GHG output')
    st.write(vdf[['County','State','ghg_globalrank','ghg_staterank','vehicle_pc_BEV','vehicle_pc_FFV','vehicle_pc_SIDI']].sort_values(by=['ghg_staterank','ghg_globalrank'],ascending=True).head(15))
if 'Rank by Census Area' in analysis_multi:
    st.markdown('##### Rank by Census Area')
    st.write(vdf[['County','State','censusarea_globalrank','censusarea_staterank','vehicle_pc_BEV','vehicle_pc_FFV','vehicle_pc_SIDI']].sort_values(by=['censusarea_staterank','censusarea_globalrank'],ascending=True).head(15))
if 'Rank by Pop Density' in analysis_multi:
    st.markdown('##### Rank by Pop Density')
    st.write(vdf[['County','State','popden_globalrank','popden_staterank','vehicle_pc_BEV','vehicle_pc_FFV','vehicle_pc_SIDI']].sort_values(by=['popden_staterank','popden_globalrank'],ascending=True).head(15))