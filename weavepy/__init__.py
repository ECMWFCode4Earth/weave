# System
import os
import sys

# Data
import numpy as np
import pandas as pd
import xarray as xr

# Plots
import matplotlib.pyplot as plt
import seaborn as sns

# Interface
from tqdm import tqdm

# Specific functions
from .load import get_data, load_vars
from .events import identify_pb_days, identify_events_whole_base, count_events
from .plot_wrappers import nb_event_timeseries_multi, event_count_barplot_multi, event_duration_hist_multi, event_seasonality_kde_multi
from .utils import get_period_length, get_period_min_max

# BDD parameters
from .bdd_parameters import *

config_dir = os.path.abspath("../")
sys.path.append(config_dir)
from config import BDD_VERSION