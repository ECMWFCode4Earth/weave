import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import seaborn as sns
import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re

scenario_colors = {
    "historical": "rgb(0,0,0)",
    "SP119": "rgb(0,173,207)",
    "SP126": "rgb(23,60,102)",
    "SP245": "rgb(247,148,32)",
    "SP370": "rgb(231,29,37)",
    "SP585": "rgb(149,27,30)",
}

model_linestyles = {
    "ERA5": "solid",
    "AWCM": "dash",
    "BCCS": "dashdot",
    "CMR5": "dot",
    "ECE3": "solid",     
    "MEHR": "longdashdot", 
    "MRM2": "longdash",
}

def nb_event_timeseries(N_events, rolling_window = 21):
    Nroll = N_events.groupby(["model", "scenario"])[
    ["year", "n_events"]].rolling(rolling_window, center = True).mean().reset_index()

    # Base figure with all models (faint lines)
    fig = px.line(
        Nroll,
        x="year", y="n_events",
        color="scenario",
        line_dash="model",
        color_discrete_map=scenario_colors,
        line_dash_map=model_linestyles,
    )
    
    # Make all individual lines faint (works across Plotly versions)
    fig.update_traces(opacity=0.2)

    
    # Compute multi-model mean for each scenario
    mm_mean = (
        Nroll.groupby(["scenario", "year"])["n_events"]
        .mean()
        .reset_index()
    )
    
    # Add all mean traces in one go
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

    fig_widget = go.FigureWidget(fig)
    return fig_widget

def nb_event_timeseries_multi(dfs, rolling_window=21, titles=None):
    n = len(dfs)
    if titles is None:
        titles = [f"Dataset {i+1}" for i in range(n)]

    # Create vertical subplots
    fig = make_subplots(
        rows=n, cols=1,
        subplot_titles=titles,
        shared_xaxes=True
    )

    for i, df in enumerate(dfs):
        subfig = nb_event_timeseries(df, rolling_window=rolling_window)
        for trace in subfig.data:
            # Link traces across panels by scenario/model
            trace.legendgroup = trace.name
            trace.showlegend = (i == 0)  # only show legend in first panel
            fig.add_trace(trace, row=i+1, col=1)

    # Update layout: bottom legend, horizontal, one column per scenario
    fig.update_layout(
        height=350*n + 100,  # extra space for legend
        showlegend=True,
        legend=dict(
            orientation="h",       # horizontal legend
            yanchor="bottom",
            y=-0.15,               # position below plot
            xanchor="center",
            x=0.5,
            traceorder="normal",
            itemsizing="constant"
        ),
        title_text="Climate Events Across Multiple Datasets"
    )

    fig_widget = go.FigureWidget(fig)
    return fig_widget

def _rgb_to_rgba(rgb_str, alpha=0.2):
    """Convert 'rgb(r,g,b)' string to 'rgba(r,g,b,a)' string."""
    nums = re.findall(r'\d+', rgb_str)   # extract numbers
    r, g, b = map(int, nums)
    return f'rgba({r},{g},{b},{alpha})'
    
def event_duration_hist(e, historical_period, future_period):
    e["duration_days"] = e["duration"].astype(int) * 1e-9 / 3600 / 24

    # Filter period
    if (len(historical_period)) > 0 & (len(future_period) > 0):
        e = e[e.year.between(*historical_period) | e.year.between(*future_period)]

    fig = go.Figure()
    bins = np.arange(0.5, 30, 1)  

    for scenario in e.scenario.unique():
        dur = e.loc[e.scenario == scenario, "duration_days"].dropna().values
        counts, edges = np.histogram(dur, bins=bins)
        if counts.sum() == 0:
            continue
        counts_prop = counts / counts.sum()
        x_step = np.repeat(edges, 2)[1:-1]
        y_step = np.repeat(counts_prop, 2)
    
        base_color = scenario_colors[scenario]
        fill_color = _rgb_to_rgba(base_color, 0.15)
    
        # Histogram step + fill
        fig.add_trace(go.Scatter(
            x=x_step,
            y=y_step,
            mode="lines",
            line=dict(color=base_color, width=3),
            fill="tozeroy",
            fillcolor=fill_color,
            name=scenario,
            legendgroup=scenario,       # group with mean line
            showlegend=True,            # only this one shows in legend
            hovertemplate="%{x}<br>proportion: %{y:.3f}<extra></extra>"
        ))
    
        # Mean vertical line
        mean_val = dur.mean()
        fig.add_trace(go.Scatter(
            x=[mean_val, mean_val],
            y=[0, max(y_step)],
            mode="lines",
            line=dict(color=base_color, width=2, dash="dash"),
            legendgroup=scenario,       # same group as histogram
            showlegend=True,            # hidden from legend
            name = scenario + " mean"
        ))
    
    fig.update_layout(
        #template = "simple_white",
        xaxis_title = "Duration (days)",
        yaxis_title = "Proportion"
    )

    return fig

def event_duration_hist_multi(dfs, historical_period, future_period, titles=None):
    """
    Create a vertical multi-panel histogram figure across multiple datasets.
    Each panel shows duration histograms for scenarios with mean lines.
    """
    n = len(dfs)
    if titles is None:
        titles = [f"Dataset {i+1}" for i in range(n)]

    # Create subplots
    fig = make_subplots(
        rows=n, cols=1,
        subplot_titles=titles,
        shared_xaxes=True
    )

    for i, df in enumerate(dfs):
        subfig = event_duration_hist(df, historical_period, future_period)
        for trace in subfig.data:
            # Link legend items across panels
            trace.legendgroup = trace.name.split()[0]  # base scenario name
            trace.showlegend = (i == 0) and ("mean" not in trace.name)  
            # 👆 only show the histogram traces in the first panel's legend
            fig.add_trace(trace, row=i+1, col=1)

    # Update layout: single horizontal legend below all panels
    fig.update_layout(
        height=350*n + 100,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            traceorder="normal",
            itemsizing="constant"
        ),
        title_text="Event Duration Histograms Across Multiple Datasets",
        xaxis_title="Duration (days)",
        yaxis_title="Proportion"
    )

    return go.FigureWidget(fig)
    
def vonmises_kde(data, kappa, n_bins=100):
    from scipy.special import i0
    bins = np.linspace(-np.pi, np.pi, n_bins)
    x = np.linspace(-np.pi, np.pi, n_bins)
    # integrate vonmises kernels
    kde = np.exp(kappa*np.cos(x[:, None]-data[None, :])).sum(1)/(2*np.pi*i0(kappa))
    kde /= np.trapezoid(kde, x=bins)
    return bins, kde

doy_first_day_month = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]

def event_seasonality_kde(d): 
    d["doy"] = d.time.dt.dayofyear
    
    fig = go.Figure()
    
    for scenario in np.unique(d.scenario):
        d_scenario = d.sel(scenario = scenario)
        # Multi-model mean kde for this scenario
        L = []
        for m in np.unique(d_scenario.model):
            d_m = d_scenario.sel(model = m)
            doys4kde = d_m.doy.where(d_m, drop = True).values
            if len(doys4kde) > 0:
                L.append(vonmises_kde(doys4kde * 2 * np.pi / 365, 180))
        theta, r = L[0][0]* 180/np.pi, np.array(L)[:,1].mean(axis = 0)
        theta_doy = (theta / 360) * 365
        fig.add_trace(
            go.Scatterpolar(
                r = r,
                theta = theta,
                mode = 'lines',
                name = scenario,
                line_color = scenario_colors[scenario], 
                hovertemplate="DOY: %{customdata:.0f}<br>Density: %{r:.3f}<extra></extra>",
                customdata=theta_doy   # attaches DOY values to each point

        ))

    month_starts = np.array(doy_first_day_month) * 360 / 365  # convert DOY → degrees
    month_labels = list("JFMAMJJASOND")
    fig.update_layout(
        title = 'Climate events',
        showlegend = True, 
        polar=dict(
            angularaxis=dict(
                tickmode="array",
                tickvals=month_starts,
                ticktext=month_labels,
                #direction="clockwise",    # optional: match your matplotlib convention
                #rotation=90               # optional: set where "Jan" starts
            )
        )
    )
    
    return fig

def event_seasonality_kde_multi(datasets, titles=None):
    """
    Multi-panel polar KDE plots for event seasonality.

    Parameters
    ----------
    datasets : list
        List of xarray datasets [climate_days, energy_days, compound_days].
    titles : list of str, optional
        Titles for each subplot. Defaults to ["Climate events", "Energy events", "Compound events"].
    """

    n = len(datasets)
    if titles is None:
        titles = ["Climate events", "Energy events", "Compound events"][:n]

    # Create subplot grid: one row, n polar plots
    fig = make_subplots(
        rows=1, cols=n,
        subplot_titles=titles,
        specs=[[{"type": "polar"}] * n]
    )

    for i, d in enumerate(datasets):
        d["doy"] = d.time.dt.dayofyear

        for scenario in np.unique(d.scenario):
            d_scenario = d.sel(scenario=scenario)
            # Multi-model mean KDE
            L = []
            for m in np.unique(d_scenario.model):
                d_m = d_scenario.sel(model=m)
                doys4kde = d_m.doy.where(d_m, drop=True).values
                if len(doys4kde) > 0:
                    L.append(vonmises_kde(doys4kde * 2 * np.pi / 365, 180))
            if not L:
                continue
            theta_deg = L[0][0] * 180/np.pi
            r = np.array(L)[:,1].mean(axis=0)
            theta_doy = (theta_deg / 360) * 365  # for hover

            fig.add_trace(
                go.Scatterpolar(
                    r=r,
                    theta=theta_deg,
                    mode="lines",
                    name=scenario,
                    line_color=scenario_colors[scenario],
                    legendgroup=scenario,
                    showlegend=(i == 0),  # legend only in first subplot
                    hovertemplate="DOY: %{customdata:.0f}<br>Density: %{r:.3f}<extra></extra>",
                    customdata=theta_doy
                ),
                row=1, col=i+1
            )

        # Month labels as xticks
        fig.update_polars(
            angularaxis=dict(
                tickmode="array",
                tickvals=(np.array(doy_first_day_month) * 360/365).tolist(),
                ticktext=list("JFMAMJJASOND")
            ),
            radialaxis=dict(showticklabels=False, ticks="")
        )

    # Layout adjustments
    fig.update_layout(
        title_text="Seasonality of the events",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        height=500,
        width=750
    )

    return go.FigureWidget(fig)
    
