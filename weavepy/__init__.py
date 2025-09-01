# System
import os
import sys

# Specific functions
from .load import get_data, load_vars
from .events import identify_pb_days, identify_events_whole_base, count_events
from .plot_wrappers import (
    nb_event_timeseries_multi,
    event_count_barplot_multi,
    event_duration_hist_multi,
    event_seasonality_kde_multi,
)
from .utils import get_period_length, get_period_min_max

# BDD parameters
from .bdd_parameters import (
    CLIM_VARS,
    ENER_VARS,
    CLIM_VARS_DICT,
    ENER_VARS_DICT,
    ENER_VARS_TECHNOS,
    FREQUENCIES_DICT,
    MODEL_NAMES,
    SCENARIOS,
    COUNTRIES_LIST,
    COUNTRIES_DICT,
)

# Robust config import from parent directory
config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if config_dir not in sys.path:
    sys.path.insert(0, config_dir)
from config import BDD_VERSION

__all__ = [
    "get_data", "load_vars", "identify_pb_days", "identify_events_whole_base",
    "count_events", "nb_event_timeseries_multi", "event_count_barplot_multi",
    "event_duration_hist_multi", "event_seasonality_kde_multi",
    "get_period_length", "get_period_min_max",
    "CLIM_VARS", "ENER_VARS", "CLIM_VARS_DICT", "ENER_VARS_DICT", "ENER_VARS_TECHNOS",
    "FREQUENCIES_DICT", "MODEL_NAMES", "SCENARIOS", "COUNTRIES_LIST", "COUNTRIES_DICT",
    "BDD_VERSION",
]