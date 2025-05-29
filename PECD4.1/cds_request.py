import cdsapi
import numpy as np
import os
from pathlib import Path

variables = [
                "100m_wind_speed",
                "10m_wind_speed",
                "2m_temperature",
                "surface_solar_radiation_downwards",
                "total_precipitation",
                "solar_generation_capacity_factor",
            ]

models = [
            "cmcc_cm2_sr5",
            "ec_earth3",
            "mpi_esm1_2_hr"
        ]

for var in variables:
    # Create folder if does not already exist
    Path(var).mkdir(parents=True, exist_ok=True)
    
    # Download historical data
    Path(var+"/historical/").mkdir(parents=True, exist_ok=True)
    for yr in np.arange(1980,2021):
        fname=var+"/historical/"+var+'_'+str(yr)+'.zip'
        if not os.path.exists(fname):
            dataset = "sis-energy-pecd"
            request = {
                    "pecd_version": "pecd4_1",
                    "temporal_period": ["historical"],
                    "origin": ["era5_reanalysis"],
                    "variable": [var],
                    "spatial_resolution": ["nuts_0"],
                    "year": [str(yr)]
                    }
            client = cdsapi.Client()
            client.retrieve(dataset, request, fname)
    
    # Download future data
    Path(var+"/future/").mkdir(parents=True, exist_ok=True)
    for model in models:
        Path(var+"/future/"+model).mkdir(parents=True, exist_ok=True)
        for yr in np.arange(2015, 2066):
            fname = var+"/future/"+model+'/'+var+'_'+str(yr)+'_'+model+'.zip'
            if not os.path.exists(fname):
                dataset = "sis-energy-pecd"
                request = {
                            "pecd_version": "pecd4_1",
                            "temporal_period": ["future_projections"],
                            "origin": [model],
                            "emissions": ["ssp2_4_5"],
                            "variable": [var],
                            "spatial_resolution": ["nuts_0"],
                            "year": [str(yr)]
                        }
                client = cdsapi.Client()
                client.retrieve(dataset, request, fname)


# Metadata
# Retrieved manually

# Wind power data
# ONSHORE
var = "wind_power_onshore_capacity_factor"

# Create folder if does not already exist
Path(var).mkdir(parents=True, exist_ok=True)
# Download historical data
Path(var+"/historical/").mkdir(parents=True, exist_ok=True)
for yr in np.arange(1980,2021):
    fname=var+"/historical/"+var+'_'+str(yr)+'.zip'

    dataset = "sis-energy-pecd"
    request = {
        "pecd_version": "pecd4_1",
        "temporal_period": ["historical"],
        "origin": ["era5_reanalysis"],
        "year": [str(yr)],
        "variable": [var],
        "technology": [
            "30",
            "31",
            "32",
            "33",
            "34",
            "35",
            "36",
            "37",
            "38",
            "39"
        ],
        "spatial_resolution": ["peon"]
    }

    client = cdsapi.Client()
    client.retrieve(dataset, request, fname)
    
# Download future data
Path(var+"/future/").mkdir(parents=True, exist_ok=True)
for model in models:
    Path(var+"/future/"+model).mkdir(parents=True, exist_ok=True)
    for yr in np.arange(2015, 2066):
        fname = var+"/future/"+model+'/'+var+'_'+str(yr)+'_'+model+'.zip'

        dataset = "sis-energy-pecd"
        request = {
            "pecd_version": "pecd4_1",
            "temporal_period": ["future_projections"],
            "origin": [model],
            "emissions": ["ssp2_4_5"],
            "variable": [var],
            "technology": [
                "30",
                "31",
                "32",
                "33",
                "34",
                "35",
                "36",
                "37",
                "38",
                "39"
            ],
            "spatial_resolution": ["peon"],
            "year": [str(yr)]
        }
        
        client = cdsapi.Client()
        client.retrieve(dataset, request, fname)

# OFFSHORE
var = "wind_power_offshore_capacity_factor"

# Create folder if does not already exist
Path(var).mkdir(parents=True, exist_ok=True)
# Download historical data
Path(var+"/historical/").mkdir(parents=True, exist_ok=True)
for yr in np.arange(1980,2021):
    fname=var+"/historical/"+var+'_'+str(yr)+'.zip'

    dataset = "sis-energy-pecd"
    request = {
        "pecd_version": "pecd4_1",
        "temporal_period": ["historical"],
        "origin": ["era5_reanalysis"],
        "variable": [var],
        "technology": [
            "20",
            "21",
            "22"
        ],
        "spatial_resolution": ["peof"],
        "year": [str(yr)]
    }

    client = cdsapi.Client()
    client.retrieve(dataset, request, fname)

# Download future data
Path(var+"/future/").mkdir(parents=True, exist_ok=True)
for model in models:
    Path(var+"/future/"+model).mkdir(parents=True, exist_ok=True)
    for yr in np.arange(2015, 2066):
        fname = var+"/future/"+model+'/'+var+'_'+str(yr)+'_'+model+'.zip'
        
        dataset = "sis-energy-pecd"
        request = {
            "pecd_version": "pecd4_1",
            "temporal_period": ["future_projections"],
            "origin": [model],
            "emissions": ["ssp2_4_5"],
            "variable": [var],
            "technology": [
                "20",
                "21",
                "22"
            ],
            "spatial_resolution": ["peof"],
            "year": [str(yr)]
        }
        
        client = cdsapi.Client()
        client.retrieve(dataset, request, fname)
    