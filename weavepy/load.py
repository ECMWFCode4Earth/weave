"""
Module for loading functions
"""

import os
import pandas as pd
import dask.dataframe as dd
from tqdm import tqdm
import xarray as xr

from config import BDD_PATH, CACHE_DATA_PATH
from .bdd_parameters import ENER_VARS_TECHNOS

def define_cache_path(bdd_version, var, techno, aggregation_frequency, aggregation_function, country):
    """
    Construct the cache file path for NetCDF data.
    """
    bdd_version_str = str(bdd_version)
    return CACHE_DATA_PATH.joinpath(
        f"PECD{bdd_version_str}/{var}_{techno}_{aggregation_frequency}-{aggregation_function}_{country}_PECD{bdd_version_str}.nc"
    )
    
def load_vars(vars: list, bdd_version: float = 4.2,
              countries: list = None, technos: list = None, models: list = None, scenarios: list = None,
              aggregation_frequency: str = "D", aggregation_function: str = "mean",
              verbose: bool = False) -> xr.Dataset:
    """
    Load PECD4.2 data for specified variables, countries, technos, models, and scenarios,
    using time aggregation and a cache system. If the cached file does not exist, it is generated.
    """
    countries = countries if countries is not None else ["FR"]
    technos = technos if technos is not None else ["NA", "60"]
    models = models if models is not None else []
    scenarios = scenarios if scenarios is not None else []
    
    if not countries:
        raise ValueError("At least one country must be specified.")
    if not vars:
        raise ValueError("At least one variable must be specified.")

    data = {}

    for i, country in enumerate(countries):
        if verbose:
            print(f'Loading country {i+1}/{len(countries)} ({country})')

        data_per_variable = {}
        for j, var in enumerate(vars):
            if verbose:
                print(f'|_Variable {j+1}/{len(vars)} ({var})')

            data_per_techno = {}
            subset_technos = [t for t in technos if var in ENER_VARS_TECHNOS and t in ENER_VARS_TECHNOS[var]] \
                             if var in ENER_VARS_TECHNOS else ['NA']
            for k, techno in enumerate(subset_technos):
                if verbose:
                    print(f'|__Techno {k+1}/{len(subset_technos)} ({techno})')

                nc_file_path = define_cache_path(bdd_version, var, techno, aggregation_frequency, aggregation_function, country)

                # Ensure parent directory exists before writing
                if not nc_file_path.parent.exists():
                    nc_file_path.parent.mkdir(parents=True, exist_ok=True)

                # Load from cache if available
                if nc_file_path.exists():
                    if verbose:
                        print(f"|__ > File exists, loading from cache: {nc_file_path}")
                    data_per_techno[techno] = xr.open_dataset(nc_file_path)
                else:
                    if verbose:
                        print(f"|__ > File not found, loading from source. Estimated processing time = 1 minute.")
                    data_per_techno[techno] = get_data(
                        variable=var, bdd_version=bdd_version, countries=[country], technos=[techno],
                        models=models, scenarios=scenarios, aggregation_frequency=aggregation_frequency,
                        aggregation_function=aggregation_function, verbose=verbose
                    )
                    data_per_techno[techno].to_netcdf(nc_file_path)

            # Merge technos for variable
            data_per_variable[var] = xr.merge(list(data_per_techno.values())).squeeze()

        # Merge variables for country
        data[country] = xr.merge(list(data_per_variable.values()), compat='override')

    # Merge all countries
    return xr.merge(list(data.values()))
    
def get_data(variable: str, bdd_version: float = 4.2,
             countries: list = None, technos: list = None, models: list = None, scenarios: list = None,
             aggregation_frequency: str = "D", aggregation_function: str = "mean",
             verbose: bool = False) -> xr.Dataset:
    """
    Read data for one variable from the database and process according to filters.
    """
    countries = countries if countries is not None else ["FR"]
    technos = technos if technos is not None else ["NA", "60"]
    models = models if models is not None else []
    scenarios = scenarios if scenarios is not None else []

    bdd_version_str = str(bdd_version)
    data_path = BDD_PATH.joinpath(f'PECD{bdd_version_str}')

    # List all files for the variable
    all_files = [f for f in data_path.rglob('*.csv') if variable in str(f) and 'ReGrA' not in str(f)]
    if not all_files:
        raise FileNotFoundError(f"No matching CSV files found for variable '{variable}' in {data_path}")

    meta = pd.DataFrame({
        'path': all_files,
        'basename': [os.path.basename(f) for f in all_files],
    })

    # Extract metadata safely
    meta_split = meta['basename'].str.split('_', expand=True)
    meta['model'] = meta_split[2] + "_" + meta_split[3]
    meta['model'] = meta['model'].replace({"ECMW_T639": "ERA5"})
    meta['tech'] = meta_split[16]
    meta['scenario'] = meta_split[17].replace({"NA---": "historical"})

    if verbose:
        print(f"Found {len(meta)} files. Techs: {meta.tech.unique()}, Models: {meta.model.unique()}, Scenarios: {meta.scenario.unique()}")

    # Filtering
    if technos:
        meta = meta[meta.tech.isin(technos)]
        if verbose:
            print(f"After filtering technos: {len(meta)}")
    if models:
        meta = meta[meta.model.isin(models)]
        if verbose:
            print(f"After filtering models: {len(meta)}")
    if scenarios:
        meta = meta[meta.scenario.isin(scenarios)]
        if verbose:
            print(f"After filtering scenarios: {len(meta)}")

    records = []
    for _, row in tqdm(meta.iterrows(), total=len(meta), desc="Loading CSVs"):
        try:
            df = pd.read_csv(row['path'], sep=',', comment='#',
                             usecols=None if not countries else
                             lambda col: col == "Date" or any(col.startswith(c) for c in countries))
        except Exception as e:
            print(f"Error reading {row['path']}: {e}")
            continue
        df['Date'] = dd.to_datetime(df['Date'])
        df = df.resample(aggregation_frequency, on="Date").agg(aggregation_function).reset_index()
        df_long = df.melt(id_vars='Date', var_name='country', value_name=variable)
        df_long['model'] = row['model']
        df_long['scenario'] = row['scenario']
        df_long['tech'] = row['tech']
        records.append(df_long)

    if not records:
        raise ValueError("No data loaded; please check your filters and files.")

    df_all = pd.concat(records, ignore_index=True)
    if verbose:
        print("|__ > Data loaded. Starting pivot_table")
    df_pivot = df_all.pivot_table(index=['Date', 'country', 'scenario', 'model', 'tech'], values=variable)

    if verbose:
        print("|__ > Converting to Xarray Dataset")
    ds = df_pivot.to_xarray().rename({'Date': 'time'})

    return ds