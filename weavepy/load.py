import os
import sys
import pandas as pd
import dask.dataframe as dd
from tqdm import tqdm
import xarray as xr

config_dir = os.path.abspath("../")
sys.path.append(config_dir)

from config import BDD_PATH

def load_vars(vars: list, bdd_version: float = 4.2,
              countries: list = ["FR"], technos: list = ["NA", "60"], models: list = [], scenarios: list = [], # Filters
              aggregation_frequency: str = "D", aggregation_function: str = "mean",
              verbose:bool=False):
    
    # TODO : Implement aliases?
    # models_aliases = {}
    
    data = {}
    for var in tqdm(vars):
        if verbose: print(var)
        data[var] = get_data(variable=var, bdd_version=bdd_version, 
                             countries=countries, technos=technos, models=models, scenarios=scenarios,
                             aggregation_frequency=aggregation_frequency, aggregation_function=aggregation_function,
                             verbose=verbose)
    return xr.merge(data.values())

#PECD4.1
#PECD4.1/2m_temperature/future/cmcc_cm2_sr5
#P_CMI6_CMCC_CMR5_TA-_0002m_Pecd_NUT0_S201501010000_E201512312300_INS_TIM_01h_NA-_cdf_org_NA_SP245_NA---_NA---_PECD4.1_fv1.csv (len22)

#PECD4.2
#PECD4.2/NUTS0/PROJ/ENER/ECE3/SP126/SPV/NUT0
#P_CMI6_ECEC_ECE3_SPV_0000m_Pecd_NUT0_S201501010000_E201512312300_CFR_TIM_01h_NA-_noc_org_60_SP126_NA---_PhM03_PECD4.2_fv1.csv (len22)

def get_data(variable: str, bdd_version: float = 4.2, 
             countries: list = ["FR"], technos: list = ["NA", "60"], models: list = [], scenarios: list = [], # Filters
             aggregation_frequency: str = "D", aggregation_function: str = "mean", # Aggregation
             verbose: bool = False) -> xr.Dataset:
    '''
    It seems to be compatible with both PECD4.1 and PECD4.2. but no complete testing has been done yet.
    This function saturates the memmory, it needs to be re-writen or the workflow must be changed to load less data at a time.
    '''
    data_path= BDD_PATH.joinpath(f'PECD{str(bdd_version)}')
    if verbose: print(data_path)
    
    # List all files available for the given variable
    all_files = [f for f in data_path.rglob('*.csv') if (variable in str(f))&('ReGrA' not in str (f))] 
    if verbose : print(len(all_files))
        
    if not all_files:
        raise FileNotFoundError("No matching CSV files found.")

    # Metadata dataframe : Contains the list of available files with the corresponding model, techno and scenario.
    ## Create the dataframe
    meta = pd.DataFrame({
        'path': all_files,
        'basename': [os.path.basename(f) for f in all_files]
    })

    ## Extract metadata (adjust indices as needed based on filename structure)
    meta[['model', 'institute']] = meta['basename'].str.split('_', expand=True)[[2, 3]]
    meta['model'] = meta[['model', 'institute']].agg('_'.join, axis=1).replace({"ECMW_T639":"ERA5"})
    meta['tech'] = meta['basename'].str.split('_').str[16]
    meta['scenario'] = meta['basename'].str.split('_').str[17].replace({"NA---":"historical"})


    ## Filter
    if len(technos) > 0:
        meta = meta[meta.tech.isin(technos)]
    if len(models) > 0:
        meta = meta[meta.model.isin(models)]
    if len(scenarios) > 0:
        meta = meta[meta.scenario.isin(scenarios)]
    
    if verbose : print(len(meta))

    #Loading
    #NB: This is long
    records = []
    for _, row in tqdm(meta.iterrows()):
        df = pd.read_csv(row['path'], sep=',', comment='#',
                         usecols = lambda col: col == "Date" or any(col.startswith(country) for country in countries))
        df['Date'] = dd.to_datetime(df['Date'])
        # - Aggregation step -
        df = df.resample(aggregation_frequency, on = "Date").agg(aggregation_function).reset_index()
        # - Format -
        df_long = df.melt(id_vars='Date', var_name='country', value_name=variable)
        df_long['model'] = row['model']
        df_long['scenario'] = row['scenario']
        df_long['tech'] = row['tech']
        records.append(df_long)
    df_all = pd.concat(records, ignore_index=True)
    
    #Transform
    if verbose : print("Starting pivot_table")
    ## NB: This is memory intensive. It is also quite long.
    df_pivot = df_all.pivot_table(index=['Date', 'country', 'scenario', 'model', 'tech'], values=variable)
    
    if verbose : print("Converting to xr...")
    ds = df_pivot.to_xarray().rename({'Date': 'time'})

    return ds