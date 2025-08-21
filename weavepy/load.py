import os
import pandas as pd
import dask.dataframe as dd
from tqdm import tqdm
import xarray as xr

from config import BDD_PATH, CACHE_DATA_PATH, ENER_VARS_DICT

def define_cache_path(bdd_version, var, techno, aggregation_frequency, aggregation_function, country):
    return CACHE_DATA_PATH.joinpath(f"PECD{str(bdd_version)}/{var}_{techno}_{aggregation_frequency}-{aggregation_function}_{country}_PECD{str(bdd_version)}.nc")
    
def load_vars(vars: list, bdd_version: float = 4.2,
              countries: list = ["FR"], technos: list = ["NA", "60"], models: list = [], scenarios: list = [], # Filters
              aggregation_frequency: str = "D", aggregation_function: str = "mean",
              verbose:bool=False):
    """ 
    Function to load PECD4.2 data with specific time aggregation. This function uses a cache system, where if the file is not already cached, it will be, and if it is, the cached file will be loaded. The cache path is to be set in the config.py file. 
    """
    
    data = {}

    # Check that input is correct
    if len(countries) == 0:
        raise ValueError("At least one country must be specified.")
    if len(vars) == 0:
        raise ValueError("At least one variable must be specified.")

    # Load the data for each country, variable, techno
    for i,country in enumerate(countries):
        if verbose: print(f'Loading country n°{i+1}/{len(countries)} ({country})')

        data_per_variable = {}
        for j,var in enumerate(vars):
            if verbose: print(f'|_Variable n°{j+1}/{len(vars)} ({var})')

            data_per_techno = {}
            subset_technos = [t for t in technos if (var in ENER_VARS_DICT)&(t!='NA')] or ['NA']
            for k,techno in enumerate(subset_technos):
                if verbose: print(f'|__Techno n°{k+1}/{len(subset_technos)} ({techno})')

                # Define Cache NetCDF file name
                nc_file_path = define_cache_path(bdd_version, var, techno, aggregation_frequency, aggregation_function, country)

                # Check if cached file exists
                if nc_file_path.exists():
                    # If it does, load from cache
                    if verbose: print(f"|__ > File already exists, loading from cache: {nc_file_path}")
                    data_per_techno[techno] = xr.open_dataset(nc_file_path)

                else:
                    # If it does not, load the data
                    if verbose: print(f"|__ > File not found, loading from source. Estimated processing time = 1 minute.")
                    
                    data_per_techno[techno] = get_data(variable=var, bdd_version=bdd_version, countries=[country], technos=[techno], models=models, scenarios=scenarios, aggregation_frequency=aggregation_frequency, aggregation_function=aggregation_function, verbose=verbose)

                    # Save the new file to cache
                    os.makedirs(nc_file_path.parent, exist_ok=True)
                    data_per_techno[techno].to_netcdf(nc_file_path)

           # Combine all data for this variable into one object
            data_per_variable[var]=xr.merge(data_per_techno.values()).squeeze()

        # Combine all variable for one country into one object
        data[country] = xr.merge(data_per_variable.values(), compat='override')

    # combine everything together
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

    """ Read data for one variable from the database as specified in the config file. 
    """

    data_path= BDD_PATH.joinpath(f'PECD{str(bdd_version)}')
    #if verbose: print(data_path)
    
    # List all files available for the given variable
    all_files = [f for f in data_path.rglob('*.csv') if (variable in str(f))&('ReGrA' not in str (f))] 
    #if verbose : print(len(all_files))
        
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

    if verbose : print(len(meta), meta.tech.unique(), meta.model.unique(), meta.scenario.unique())
        
    ## Filter
    if len(technos) > 0:
        meta = meta[meta.tech.isin(technos)]
        if verbose : print("After filtering technos", len(meta))
    if len(models) > 0:
        meta = meta[meta.model.isin(models)]
        if verbose : print("After filtering models", len(meta))
    if len(scenarios) > 0:
        meta = meta[meta.scenario.isin(scenarios)]
        if verbose : print("After filtering scenarios", len(meta))
    
    #if verbose : print(len(meta))

    #Loading
    #NB: This is long
    records = []
    for _, row in tqdm(meta.iterrows()):
        df = pd.read_csv(row['path'], sep=',', comment='#',
                         usecols = None if len(countries)==0 else lambda col: col == "Date" or any(col.startswith(country) for country in countries))
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
    if verbose : print("|__ > Data loaded. Starting pivot_table")
    ## NB: This is memory intensive. It is also quite long.
    df_pivot = df_all.pivot_table(index=['Date', 'country', 'scenario', 'model', 'tech'], values=variable)
    
    if verbose : print("|__ > Converting to Xarray Dataset")
    ds = df_pivot.to_xarray().rename({'Date': 'time'})

    return ds