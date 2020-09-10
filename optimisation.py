#!pip install pulp
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from itertools import product
from tqdm import tqdm
import pandas as pd
from pulp import *
import numpy as np

#import files from github
V = pd.read_csv('https://raw.githubusercontent.com/saif1457/biofuels/master/optimisation_data/V.csv') #vehicle types
F = pd.read_csv('https://raw.githubusercontent.com/saif1457/biofuels/master/optimisation_data/F.csv') #fuel types
E = pd.read_csv('https://raw.githubusercontent.com/saif1457/biofuels/master/optimisation_data/E.csv') #driving env
R = pd.read_csv('https://raw.githubusercontent.com/saif1457/biofuels/master/optimisation_data/R.csv') #counties
M = pd.read_csv('https://raw.githubusercontent.com/saif1457/biofuels/master/optimisation_data/M.csv') #charging stations
S = pd.read_csv('https://raw.githubusercontent.com/saif1457/biofuels/master/optimisation_data/S.csv') #states

F['fuel_type'] = F['fuel_type'].apply(lambda x: x.replace('electricity','Electricity'))

VEHICLE_TYPES = list(V['vehicle_type'])
FUEL_TYPES = list(F['fuel_type'])
DRIVING_ENV = list(E['driving_environment'])
COUNTIES = list(R['county'])
CHARGING_STATIONS = list(M['filling_stations'])
STATES = list(S['state'])

EF = pd.read_csv('https://raw.githubusercontent.com/saif1457/biofuels/master/optimisation_data/EF(f%2Cs).csv')
EF['fuel_type'] = EF['fuel_type'].apply(lambda x: x.replace('electricity','Electricity'))
FE = pd.read_csv('https://raw.githubusercontent.com/saif1457/biofuels/master/optimisation_data/FE(v%2Cf).csv')
FE['fuel_type'] = FE['fuel_type'].apply(lambda x: x.replace('electricity','Electricity'))
C = pd.read_csv('https://raw.githubusercontent.com/saif1457/biofuels/master/optimisation_data/C(F).csv')
CC = pd.read_csv('https://raw.githubusercontent.com/saif1457/biofuels/master/optimisation_data/CC(v%2Cs).csv') 
CC['yearly_cost']=np.where(CC['vehicle_type']=='BEV', CC['cost_minus_rebate']/8.5, CC['cost_minus_rebate']/5.5)
CG = pd.read_csv('https://raw.githubusercontent.com/saif1457/biofuels/master/optimisation_data/CG(F).csv')
CG['fuel_type'] = CG['fuel_type'].apply(lambda x: x.replace('electricity','Electricity'))
# D = 0.25
TM = pd.read_csv('https://raw.githubusercontent.com/saif1457/biofuels/master/optimisation_data/TM(f%2Cs).csv')
N = pd.read_csv('https://raw.githubusercontent.com/saif1457/biofuels/master/optimisation_data/N(r).csv')
B = pd.read_csv('https://raw.githubusercontent.com/saif1457/biofuels/master/optimisation_data/B(r).csv')
CF = FE
CF['fuel_consumption'] = (1 / CF['fuel_economy'])
T = pd.read_csv('https://raw.githubusercontent.com/saif1457/biofuels/master/optimisation_data/T(r).csv')
T['total_vehicles_registered'] = T['total_vehicles_registered'].apply(lambda x: x.replace(',',''))
T['total_vehicles_registered'] = T['total_vehicles_registered'].apply(pd.to_numeric)
W_param = pd.read_csv('https://raw.githubusercontent.com/saif1457/biofuels/master/optimisation_data/W_county_param.csv')
e85_vi = pd.read_csv('e85_vi.csv')
efuels_vi = pd.read_csv('efuels_vi.csv')
e85_vi = e85_vi[['STATE','NAME','CENSUSAREA','e85_area']]
e85_vi = e85_vi.rename(columns={'STATE': 'state', 'NAME': 'county','CENSUSAREA':'census_area'})
efuels_vi = efuels_vi[['STATE','NAME','CENSUSAREA','efuels_area']]
efuels_vi = efuels_vi.rename(columns={'STATE': 'state', 'NAME': 'county','CENSUSAREA':'census_area'})

import feather
readFrame = pd.read_feather('./vdf', use_threads=True)
readFrame.sort_values(by=['State','County'],ascending=True,inplace=True)
efuels_vi.sort_values(by=['state','county'],ascending=True,inplace=True)
efuels_vi.reset_index(inplace=True)

e85_vi['e85_area'] = e85_vi['e85_area'] / 100
efuels_vi['efuels_area'] = efuels_vi['efuels_area'] / 100
efuels_vi['efuels_area_new'] = readFrame['efuels_area']/100


e85vi_param = e85_vi.groupby('county')['e85_area'].apply(list).to_dict()
efuelsvi_param = efuels_vi.groupby('county')['efuels_area'].apply(list).to_dict()

v = V['vehicle_type']
f = F['fuel_type']
r = R['county']

def variable_n():
    '''
    n(r,v,f) total optimal count of vehicle v using fuel type f in county r
    '''
    n = pd.DataFrame(list(product(r,v,f)), columns=['county', 'vehicle_type','fuel_type'])
    n['count'] = 0
    
    bev_elec = n[(n['vehicle_type']== 'BEV') & (n['fuel_type']== 'Electricity')]
    gas_e10 = n[(n['vehicle_type']== 'SIDI_ICE') & (n['fuel_type']== 'E10')]
    ffv_e85 = n[(n['vehicle_type']== 'FFV') & (n['fuel_type']== 'E85')]

    result = pd.concat([bev_elec,gas_e10,ffv_e85])
    result.sort_values(by=['county','vehicle_type'],inplace=True)
    result.reset_index(drop=True, inplace=True)
    return result

def variable_fc():
    '''
    fc(r,v,f) Total fuel consumption by vehicle v using fuel type f in county r
    '''
    fc = pd.DataFrame(list(product(r,v,f)), columns=['county','vehicle_type','fuel_type'])
    fc['fuel_consumption'] = 0
    
    bev_elec = fc[(fc['vehicle_type']== 'BEV') & (fc['fuel_type']== 'Electricity')]
    gas_e10 = fc[(fc['vehicle_type']== 'SIDI_ICE') & (fc['fuel_type']== 'E10')]
    ffv_e85 = fc[(fc['vehicle_type']== 'FFV') & (fc['fuel_type']== 'E85')]

    result = pd.concat([bev_elec,gas_e10,ffv_e85])
    result.sort_values(by=['county'],inplace=True)
    result.reset_index(drop=True, inplace=True)
    return result

def variable_oc():
    '''
    oc(r,v,f) Annual operating cost for vehicle v using fuel type f in county r 
    '''
    oc = pd.DataFrame(list(product(r,v,f)), columns=['county', 'vehicle_type','fuel_type'])
    oc['operating_cost'] = 0
    
    bev_elec = oc[(oc['vehicle_type']== 'BEV') & (oc['fuel_type']== 'Electricity')]
    gas_e10 = oc[(oc['vehicle_type']== 'SIDI_ICE') & (oc['fuel_type']== 'E10')]
    ffv_e85 = oc[(oc['vehicle_type']== 'FFV') & (oc['fuel_type']== 'E85')]

    result = pd.concat([bev_elec,gas_e10,ffv_e85])
    result.sort_values(by=['county'],inplace=True)
    result.reset_index(drop=True, inplace=True)
    return result 

def variable_tac():
    '''
    tac(r,v,f) Total annual cost of vehicle v using fuel type f in county r 
    '''
    tac = pd.DataFrame(list(product(r,v,f)), columns=['county', 'vehicle_type','fuel_type'])
    tac['total_annual_vehicle_cost'] = 0
    
    bev_elec = tac[(tac['vehicle_type']== 'BEV') & (tac['fuel_type']== 'Electricity')]
    gas_e10 = tac[(tac['vehicle_type']== 'SIDI_ICE') & (tac['fuel_type']== 'E10')]
    ffv_e85 = tac[(tac['vehicle_type']== 'FFV') & (tac['fuel_type']== 'E85')]

    result = pd.concat([bev_elec,gas_e10,ffv_e85])
    result.sort_values(by=['county'],inplace=True)
    result.reset_index(drop=True, inplace=True)
    return result

def variable_ce():
    '''
    ce(r,v,f)  GHG emission per year of vehicle v using fuel type f in county r 
    '''
    ce = pd.DataFrame(list(product(r,v,f)), columns=['county', 'vehicle_type','fuel_type'])
    ce['emission_per_year'] = 0
    
    bev_elec = ce[(ce['vehicle_type']== 'BEV') & (ce['fuel_type']== 'Electricity')]
    gas_e10 = ce[(ce['vehicle_type']== 'SIDI_ICE') & (ce['fuel_type']== 'E10')]
    ffv_e85 = ce[(ce['vehicle_type']== 'FFV') & (ce['fuel_type']== 'E85')]

    result = pd.concat([bev_elec,gas_e10,ffv_e85])
    result.sort_values(by=['county'],inplace=True)
    result.reset_index(drop=True, inplace=True)
    return result

n = variable_n()
fc = variable_fc()
tac = variable_tac()
oc = variable_oc()
ce = variable_ce()

n1 = n.merge(B)
n2 = n1.merge(CG)
n3 = n2.merge(oc)
n4 = n3.merge(ce)
n5 = n4.merge(fc)
n6 = n5.merge(tac)
n6 = n6.sort_values(by=['county','vehicle_type'], ascending=True)
n6.reset_index(drop=True, inplace=True)

N_B = B.merge(N)
number_one = N_B.merge(TM, left_on=['household_income_ID','state'],right_on=['household_income_ID','state'])
number_one.drop(['household_income','household_income_ID'],axis=1,inplace=True)
n6 = n6.merge(number_one)
total_miles_df = n6[['county','vehicle_type','annual_miles_driven']]

EF_param = {k: f.groupby('fuel_type')['emission_factor'].apply(list).to_dict()
     for k, f in EF.groupby('state')}

FE_param = {k: f.groupby('fuel_type')['fuel_economy'].apply(list).to_dict()
     for k, f in FE.groupby('vehicle_type')}

C_param = {k: f.groupby('fuel_type')['fuel_cost_per_mile'].apply(list).to_dict()
     for k, f in C.groupby('state')}
# CC_param = {k: f.groupby('vehicle_type')['cost_minus_rebate'].apply(list).to_dict()
#      for k, f in CC.groupby('state')}
improve = CC.merge(B)
CC_param = {k: f.groupby('vehicle_type')['yearly_cost'].apply(list).to_dict()
     for k, f in improve.groupby('county')}
CC_param

CG_param = {k: f.groupby('fuel_type')['fuel_cost_per_gal'].apply(list).to_dict()
     for k, f in CG.groupby('state')}
TM_param = {k: f.groupby('vehicle_type')['annual_miles_driven'].apply(list).to_dict()
     for k, f in total_miles_df.groupby('county')}
CFnew = CF.merge(n6,left_on="vehicle_type",right_on="vehicle_type")
CFnew.sort_values(by=['county'],inplace=True)
CFnew.reset_index(drop=True, inplace=True)
CFnew = CFnew[['county','vehicle_type','fuel_consumption_x']]
CFnew_param = {k: f.groupby('vehicle_type')['fuel_consumption_x'].apply(list).to_dict()
     for k, f in CFnew.groupby('county')}

CGnew_param = n6[['county','vehicle_type','fuel_cost_per_gal']]
CGnew_param = {k: f.groupby('vehicle_type')['fuel_cost_per_gal'].apply(list).to_dict()
     for k, f in CGnew_param.groupby('county')}
     

T_param = T.groupby('county')['total_vehicles_registered'].apply(list).to_dict()
W_param = W_param.groupby('county')['emissions_per_county'].apply(list).to_dict()


n = LpVariable.dicts("vehicle_count", (COUNTIES, VEHICLE_TYPES), 0)
fc = LpVariable.dicts("total_fuel_use", (COUNTIES, VEHICLE_TYPES), 0)
oc = LpVariable.dicts("annual_operating_cost", (COUNTIES, VEHICLE_TYPES), 0)
tac = LpVariable.dicts("total_annual_cost", (COUNTIES, VEHICLE_TYPES), 0)
ce = LpVariable.dicts("GHG_emissions_new", (COUNTIES, VEHICLE_TYPES), 0)

#SET PROBLEM VARIABLE
prob = LpProblem('Biofuels',LpMinimize)
#OBJECTIVE FUNCTION: minimise cost, determine car allocation (mixed integer)
prob += lpSum(((CFnew_param[r][f][0] * CGnew_param[r][f][0] * TM_param[r][f][0]) + CC_param[r][f][0]) * n[r][f] for f in VEHICLE_TYPES for r in COUNTIES)

v = V['vehicle_type']
f = F['fuel_type']
r = R['county']
CE = variable_ce()
ce_update = CE.merge(B)


#Constraint 0: Non-negative vehicles assigned to each county r 
for r in COUNTIES:
    for f in VEHICLE_TYPES:
        prob += n[r][f] >= 0
        
Nnew = N.merge(B)
EFnew = pd.merge(TM, Nnew,  how='left', left_on=['state','household_income_ID'], right_on = ['state','household_income_ID']).dropna()
EFnew = EFnew.merge(EF).merge(FE)
EFnew.sort_values(by=['county'],inplace=True)
EFnew.reset_index(drop=True, inplace=True)
EFnew['TotalEmission'] = EFnew['annual_miles_driven']*EFnew['emission_factor']
EFnew
EFnew_param = {k: f.groupby('county')['TotalEmission'].apply(list).to_dict()
      for k, f in EFnew.groupby('county')}

#Constraint 1: Annual emission by total of vehicle v in county f with a given fuel ce(r,f) equals emission per mile * total miles driven 

for r in COUNTIES:
    j = 0
    for f in VEHICLE_TYPES:
        prob += ce[r][f] == EFnew_param[r][r][j]*n[r][f]
        j += 1

# #Constraint 2: Decrease total emissions by D(s) for each state 
prob += lpSum(ce[r][f] for f in VEHICLE_TYPES for r in COUNTIES) <= ((1-D) * lpSum(W_param[r][0] for r in COUNTIES))

#Constraints 3: E85 Viability index
for r in COUNTIES:
    prob += lpSum(n[r]['FFV']) <= (e85vi_param[r][0] * T_param[r][0]) 
    
#Constraint 4: EV Viability index
for r in COUNTIES:
    prob += lpSum(n[r]['BEV']) <= (efuelsvi_param[r][0] * T_param[r][0]) 
    
#Constraint 5: Total annual fuel consumption per county equals fuel consumption of each vehicle in that county
for r in COUNTIES:
    for f in VEHICLE_TYPES:
        prob += fc[r][f]  - (CFnew_param[r][f][0] * n[r][f]* TM_param[r][f][0]) == 0
        
#Constraint 6: Operating cost= cost of fuel * sum of fuel consumption
for r in COUNTIES:
    for f in VEHICLE_TYPES:
        prob += oc[r][f] - (CGnew_param[r][f][0] * fc[r][f]) == 0
        
# Constraint 7: Total number of all vehicle types v should be equal to the total number of vehicles in county r 
for r in COUNTIES:
    prob += lpSum(n[r][f] for f in VEHICLE_TYPES) == T_param[r][0]

# Constraint 8: Total annual cost of vehicle v in county r = operating cost + capital cost
for r in COUNTIES: 
    for f in VEHICLE_TYPES:
        prob += tac[r][f] == oc[r][f] + (CC_param[r][f][0] * n[r][f])

LpSolverDefault.msg=1
prob.solve()

print("The Min Value = $",value(prob.objective))

keys, values = [[] for i in range(2)]
for v in prob.variables():
    keys.append(v.name)
    values.append(v.varValue)
results = dict(zip(keys, values))

census_area = efuels_vi[['census_area','county']]
temp_county_list = list(census_area['county'])

for i in temp_county_list:
    temp_county_list[temp_county_list.index(i)] = i.replace(' ','_')
census_area['county'] = temp_county_list
census_area.rename(columns={'county':'County'},inplace=True)
census_area[census_area['County']=='San_Francisco']

for i in COUNTIES:
    COUNTIES[COUNTIES.index(i)] = i.replace(" ", "_")
    
ghg_vis, oc_vis, tac_vis, tfu_vis, vc_vis, vc_vis_BEV, vc_vis_FFV, vc_vis_SIDI = [[] for i in range(8)]

for r in COUNTIES:
    a_subset = {key: value for key, value in results.items() if r in key}
    ghg_vis.append(a_subset['GHG_emissions_new_' + r + '_BEV'] + a_subset['GHG_emissions_new_' + r + '_FFV'] + a_subset['GHG_emissions_new_' + r + '_SIDI_ICE'])
    oc_vis.append(a_subset['annual_operating_cost_' + r + '_BEV'] + a_subset['annual_operating_cost_' + r + '_FFV'] + a_subset['annual_operating_cost_' + r + '_SIDI_ICE'])
    tac_vis.append(a_subset['total_annual_cost_' + r + '_BEV'] + a_subset['total_annual_cost_' + r + '_FFV'] + a_subset['total_annual_cost_' + r + '_SIDI_ICE'])
    tfu_vis.append(a_subset['total_fuel_use_' + r + '_BEV'] + a_subset['total_fuel_use_' + r + '_FFV'] + a_subset['total_fuel_use_' + r + '_SIDI_ICE'])
    vc_vis.append(a_subset['vehicle_count_' + r + '_BEV'] + a_subset['vehicle_count_' + r + '_FFV'] + a_subset['vehicle_count_' + r + '_SIDI_ICE'])
    vc_vis_BEV.append(a_subset['vehicle_count_' + r + '_BEV'])
    vc_vis_FFV.append(a_subset['vehicle_count_' + r + '_FFV'])
    vc_vis_SIDI.append(a_subset['vehicle_count_' + r + '_SIDI_ICE'])

Visual = pd.DataFrame(zip(COUNTIES, ghg_vis, oc_vis, tac_vis, tfu_vis, vc_vis, vc_vis_BEV, vc_vis_FFV, vc_vis_SIDI),
              columns=['County','ghg_vis','oc_vis', 'tac_vis','tfu_vis','vc_vis','vc_vis_BEV','vc_vis_FFV','vc_vis_SIDI'])

column_names = ["County", "annual_ghg_emissions", "annual_operating_cost","total_annual_cost","annual_fuel_use", "total_vehicle_count",'vehicle_split_BEV','vehicle_split_FFV','vehicle_split_SIDI']
Visual.columns = column_names
Visual['vehicle_pc_BEV'] = (Visual['vehicle_split_BEV']/Visual['total_vehicle_count']*100).round(1)
Visual['vehicle_pc_FFV'] = (Visual['vehicle_split_FFV']/Visual['total_vehicle_count']*100).round(1)
Visual['vehicle_pc_SIDI'] = (Visual['vehicle_split_SIDI']/Visual['total_vehicle_count']*100).round(1)

county_renaming_engine = pd.read_csv('https://raw.githubusercontent.com/saif1457/biofuels/master/optimisation_data/county_renaming_engine.csv')
Visual = Visual.merge(county_renaming_engine)
Visual['County'] = Visual['County'].str.replace('_',' ')
Visual.to_csv('optimisation_data/visual_df.csv')