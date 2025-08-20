# Data
import numpy as np
import pandas as pd
import xarray as xr
import os
#import geopandas as gpd

# Plots
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import seaborn as sns

# Interface
from tqdm import tqdm

# Specific functions
from .load import get_data, load_vars
from .events import identify_pb_days, identify_events_whole_base
from .plot import scenario_colors, model_linestyles, nb_event_timeseries, event_duration_hist, event_seasonality_kde
from .utils import get_period_length, get_period_min_max

model_aliases = {
    "historical":"historical",
    "cmcc_cm2_sr5":"CMR5",
    "ec_earth3":"ECE3", 
    "mpi_esm1_2_hr":"MEHR", 
}

