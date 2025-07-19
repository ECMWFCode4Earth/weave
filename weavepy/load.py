import os
import sys
import pandas as pd
import dask.dataframe as dd
from tqdm import tqdm
import xarray as xr

config_dir = os.path.abspath("../")
sys.path.append(config_dir)

from config import BDD_PATH

def load_vars(vars, historical = True, future = True, future_models = [], country = 'FR',): # TODO : Implement aliases?
    # Load data
    data = {}
    for var in tqdm(vars):
        print(var)
        data[var] = {}
        if historical:
            data[var]["historical"] = get_data(variable=var, period="historical", verbose = False)[country
                ].to_xarray().rename(var).to_dataset().assign(model = "ERA5")
        if future & (len(future_models) > 0):
            for model in future_models :
                data[var][model] = get_data(variable=var, period="future", model = model, verbose = False)[country
                    ].to_xarray().rename(var).to_dataset().assign(model = model)
        data[var] = xr.concat(data[var].values(), dim = "model")
    return xr.merge(data.values())

#PECD4.1
#PECD4.1/2m_temperature/future/cmcc_cm2_sr5
#P_CMI6_CMCC_CMR5_TA-_0002m_Pecd_NUT0_S201501010000_E201512312300_INS_TIM_01h_NA-_cdf_org_NA_SP245_NA---_NA---_PECD4.1_fv1.csv (len22)

#PECD4.2
#PECD4.2/NUTS0/PROJ/ENER/ECE3/SP126/SPV/NUT0
#P_CMI6_ECEC_ECE3_SPV_0000m_Pecd_NUT0_S201501010000_E201512312300_CFR_TIM_01h_NA-_noc_org_60_SP126_NA---_PhM03_PECD4.2_fv1.csv (len22)

def get_data(variable: str, bdd_version: float = 4.2) -> xr.Dataset:
    '''
    It seems to be compatible with both PECD4.1 and PECD4.2. but no complete testing has been done yet.
    This function saturates the memmory, it needs to be re-writen or the workflow must be changed to load less data at a time.
    '''
    data_path= BDD_PATH.joinpath(f'PECD{str(bdd_version)}')
    #########################################################################################################################################
    ##################### I voluntarily add conditions on the variable, tech and model here for testing purposes.############################
    ################## If not, the memory saturates and the program crashes (with 32Go of RAM and 34Go of swap memory). #####################
    variable = 'SPV'
    all_files = [f for f in data_path.rglob('*.csv') if (variable in str(f))&('ReGrA' not in str (f))&('_60_' in str(f))&('MRI-' in str(f))]
    #########################################################################################################################################

    #all_files = [f for f in data_path.rglob('*.csv') if (variable in str(f))&('ReGrA' not in str (f))]

    if not all_files:
        raise FileNotFoundError("No matching CSV files found.")

    # Create a metadata dataframe
    meta = pd.DataFrame({
        'path': all_files,
        'basename': [os.path.basename(f) for f in all_files]
    })

    # Extract metadata (adjust indices as needed based on filename structure)
    meta[['source', 'model', 'institute']] = meta['basename'].str.split('_', expand=True)[[1, 2, 3]]
    meta['model'] = meta[['source', 'model', 'institute']].agg('_'.join, axis=1)
    meta['tech'] = meta['basename'].str.split('_').str[16]
    meta['scenario'] = meta['basename'].str.split('_').str[17]

    records = []
    for _, row in meta.iterrows():
        ddf = dd.read_csv(row['path'], sep=',', comment='#')
        ddf['Date'] = dd.to_datetime(ddf['Date'])
        ddf_long = ddf.melt(id_vars='Date', var_name='country', value_name=variable)
        ddf_long['model'] = row['model']
        ddf_long['scenario'] = row['scenario']
        ddf_long['tech'] = row['tech']
        records.append(ddf_long)

    ddf_all = dd.concat(records, ignore_index=True)
    
    #At this stage it loads all the data, making no difference with not using dask. I kinda think it also takes longer than without dask.
    df_all = ddf_all.compute()  #We seem to be forced to compute here because dask does not support pivot_table directly and xarray cannot create a Dataset from a dask DataFrame

    #This is the memory intensive part. It is also quite long.
    df_pivot = df_all.pivot_table(index=['Date', 'country', 'scenario', 'model', 'tech'], values=variable)
    
    ds = df_pivot.to_xarray().rename({'Date': 'time'})

    return ds