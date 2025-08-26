#import matplotlib.pyplot as plt
#import cartopy.crs as ccrs
#import seaborn as sns
#import numpy as np
#import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

from .plot_utils import scenario_colors, model_linestyles

def nb_event_timeseries(N_events, rolling_window = 21):
    ## 0. Computations
    # Compute rolling mean of number of events
    Nroll = N_events.groupby(["model", "scenario"])[
    ["year", "n_events"]].rolling(rolling_window, center = True).mean().reset_index()

    # Compute multi-model mean for each scenario
    mm_mean = (
        Nroll.groupby(["scenario", "year"])["n_events"]
        .mean()
        .reset_index()
    )
    
    ## 1. Base figure with all models 
    fig = px.line(
        Nroll,
        x="year", y="n_events",
        color="scenario",
        line_dash="model",
        color_discrete_map=scenario_colors,
        line_dash_map=model_linestyles,
    )
    
    # Make all individual lines faint 
    fig.update_traces(opacity=0.2)

    # 2. Multi-model means
    fig_means = px.line(
        mm_mean,
        x="year", y="n_events",
        color="scenario",
        color_discrete_map=scenario_colors
    )

    # Style and rename each mean trace
    for trace in fig_means.data:
        trace.line.width = 4
        trace.line.dash = "solid"
        trace.opacity = 1.0
        trace.name = f"{trace.name} mean"

    # Merge into the main figure
    for trace in fig_means.data:
        fig.add_trace(trace)

    return fig