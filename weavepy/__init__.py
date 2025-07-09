# Data
import numpy as np
import pandas as pd
import xarray as xr
#import geopandas as gpd

# Plots
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import seaborn as sns

# Interface
from tqdm import tqdm

# Specific functions
from .load import get_data, explore_database, load_vars
from .events import find_events, identify_events
from .plot import event_stripplot, nb_events_barplot, event_duration_histplot, event_seasonnality_histplot
from .utils import get_period_length, get_period_min_max

model_aliases = {
    "historical":"historical",
    "cmcc_cm2_sr5":"CMR5",
    "ec_earth3":"ECE3", 
    "mpi_esm1_2_hr":"MEHR", 
}