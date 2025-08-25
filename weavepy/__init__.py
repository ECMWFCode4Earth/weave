# System
import os
import sys

# Data
import numpy as np
import pandas as pd
import xarray as xr

# Plots
import matplotlib.pyplot as plt
#import cartopy.crs as ccrs
import seaborn as sns

# Interface
from tqdm import tqdm

# Specific functions
from .load import get_data, load_vars
from .events import identify_pb_days, identify_events_whole_base, count_events
from .plot import scenario_colors, model_linestyles, nb_event_timeseries, event_duration_hist, event_seasonality_kde
from .utils import get_period_length, get_period_min_max

config_dir = os.path.abspath("../")
sys.path.append(config_dir)