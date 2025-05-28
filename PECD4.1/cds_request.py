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
                "latitude_weights",
                "nuts_0_regions_mask",
                "nuts_2_regions_mask",
                "peof_regions_mask",
                "peon_regions_mask",
                "population_density_mask",
                "power_law_coefficients",
                "solar_pv_mask",
                "szof_regions_mask",
                "szon_regions_mask",
                "wind_power_regions_mask"
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
