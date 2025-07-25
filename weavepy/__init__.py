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
from .plot import event_stripplot, nb_events_barplot, event_duration_histplot, event_seasonnality_histplot
from .utils import get_period_length, get_period_min_max

model_aliases = {
    "historical":"historical",
    "cmcc_cm2_sr5":"CMR5",
    "ec_earth3":"ECE3", 
    "mpi_esm1_2_hr":"MEHR", 
}

scenario_colors = {
    "historical":'k',
    "SP119": np.array([0,173,207])/256,
    "SP126": np.array([23,60,102])/256,
    "SP245": np.array([247,148,32])/256,
    "SP370": np.array([231,29,37])/256,
    "SP585": np.array([149,27,30])/256,
}

model_linestyles = {
    "ERA5":'-',
    "AWCM":'--',
    "BCCS":'-.',
    "CMR5":':',
    "ECE3":(0, (3, 1, 1, 1, 1, 1)),
    "MEHR":(0,(1,5)), # Densely dotted
    "MRM2":(5,(10,3)), # long dashes
    'AWI-_AWCM':'--',
    'BCC-_BCCS':'-.',
    "CMCC_CMR5":':',
    "ECEC_ECE3":(0, (3, 1, 1, 1, 1, 1)), #densely dashdotdotted
    'MPI-_MEHR':(0,(1,5)), # Densely dotted
    'MRI-_MRM2':(5,(10,3)), # long dashes
}