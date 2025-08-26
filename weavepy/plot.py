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
    "historical":'k',
    "SP119": np.array([0,173,207])/256,
    "SP126": np.array([23,60,102])/256,
    "SP245": np.array([247,148,32])/256,
    "SP370": np.array([231,29,37])/256,
    "SP585": np.array([149,27,30])/256,
}

scenario_colors_plotly = {
    "historical": "rgb(0,0,0)",
    "SP119": "rgb(0,173,207)",
    "SP126": "rgb(23,60,102)",
    "SP245": "rgb(247,148,32)",
    "SP370": "rgb(231,29,37)",
    "SP585": "rgb(149,27,30)",
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

model_linestyles_plotly = {
    "ERA5": "solid",
    "AWCM": "dash",
    "BCCS": "dashdot",
    "CMR5": "dot",
    "ECE3": "solid",     
    "MEHR": "longdashdot", 
    "MRM2": "longdash",
}

def nb_event_timeseries(N_climate_events, N_energy_events, N_compound_events):
    fig, axs = plt.subplots(3, figsize = [12, 8], sharex = True) 
    Nrolls = {}
    for i, N in enumerate([N_climate_events, N_energy_events, N_compound_events]):
        for scenario in N_climate_events.scenario.unique():
            Nrolls[str(scenario)] = {}
            for model in N_climate_events.model.unique():
                N2plot = N[(N.scenario == scenario) & (N.model == model)].set_index("year")
                #Running mean
                Nroll = N2plot.eventID.rolling(20, center = True).mean()
                Nrolls[str(scenario)][str(model)] = Nroll
                Nroll.plot(ax = axs[i], 
                           c = scenario_colors[scenario], 
                           linestyle = model_linestyles[model], 
                          alpha = 0.5)
            mm_mean = pd.concat(list(Nrolls[scenario].values())).rename(scenario).reset_index().groupby("year").mean()
            mm_mean.plot(ax = axs[i], linewidth = 5, color = scenario_colors[scenario],)
        axs[i].set_ylabel("#events")
    axs[0].set_title("Climate events")
    axs[1].set_title("Energy events")
    axs[2].set_title("Compound events")
    plt.suptitle("Evolution of the number of events")
    plt.tight_layout()

def nb_event_timeseries_plotly(N_events, rolling_window = 21):
    Nroll = N_events.groupby(["model", "scenario"])[
    ["year", "n_events"]].rolling(rolling_window, center = True).mean().reset_index()

    # Base figure with all models (faint lines)
    fig = px.line(
        Nroll,
        x="year", y="n_events",
        color="scenario",
        line_dash="model",
        color_discrete_map=scenario_colors_plotly,
        line_dash_map=model_linestyles_plotly,
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
        color_discrete_map=scenario_colors_plotly
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

def nb_event_timeseries_plotly_multi(dfs, rolling_window=21, titles=None):
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
        subfig = nb_event_timeseries_plotly(df, rolling_window=rolling_window)
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


def event_duration_hist(climate_events, energy_events, compound_events, historical_period = (), future_period = ()):
    fig, axs = plt.subplots(3, figsize = [10, 10], sharex = True) # TODO: Rolling mean
    for i, e in enumerate([climate_events, energy_events, compound_events]):
        e["duration_days"] = e["duration"].astype(int) * 1e-9 / 3600 / 24

        # Filter period
        if (len(historical_period)) > 0 & (len(future_period) > 0):
            e = e[e.year.between(*historical_period) | e.year.between(*future_period)]
            
        # Scenarios
        for scenario in e.scenario.unique():
            e2plot = e[(e.scenario == scenario)].set_index("year")
            sns.histplot(data = e2plot, x = "duration_days", ax = axs[i], 
            color = scenario_colors[scenario], element = "step", alpha = 0.1,
            bins = np.arange(0.5,30,1), stat = "proportion", linewidth = 2,
            )
            mean = e2plot.duration_days.mean()
            axs[i].axvline(x = mean, color = scenario_colors[scenario], label = scenario)
    axs[0].set_title("Climate events")
    axs[1].set_title("Energy events")
    axs[2].set_title("Compound events")
    plt.suptitle("Duration of the events")
    plt.legend()
    plt.xlim(0,10)
    plt.tight_layout()

def rgb_to_rgba(rgb_str, alpha=0.2):
    """Convert 'rgb(r,g,b)' string to 'rgba(r,g,b,a)' string."""
    nums = re.findall(r'\d+', rgb_str)   # extract numbers
    r, g, b = map(int, nums)
    return f'rgba({r},{g},{b},{alpha})'
    
def event_duration_hist_plotly(e, historical_period, future_period):
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
    
        base_color = scenario_colors_plotly[scenario]
        fill_color = rgb_to_rgba(base_color, 0.15)
    
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

from plotly.subplots import make_subplots
import plotly.graph_objects as go

def event_duration_hist_plotly_multi(dfs, historical_period, future_period, titles=None):
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
        subfig = event_duration_hist_plotly(df, historical_period, future_period)
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

def event_seasonality_kde_plotly(d): 
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
                line_color = scenario_colors_plotly[scenario], 
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

def event_seasonality_kde_plotly_multi(datasets, titles=None):
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
                    line_color=scenario_colors_plotly[scenario],
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
    
def event_seasonality_kde(climate_days, energy_days, compound_days, historical_period = (), future_period = ()):
    fig, axs = plt.subplots(1, 3, subplot_kw = dict(projection = "polar"), figsize = (15,5))
    for i, e in enumerate([climate_days, energy_days, compound_days]):
        e["doy"] = e["time"].dt.dayofyear
        e["year"] = e["time"].dt.year

        # Filter period
        if (len(historical_period)) > 0 & (len(future_period) > 0):
            cond1 = (e.year >= historical_period[0]) & (e.year <= historical_period[1])
            cond2 = (e.year >= future_period[0]) & (e.year <= future_period[1])
            e = e.where(cond1 | cond2, drop = True)
            
        for scenario in np.unique(e.scenario):
            days_scenario = e.sel(scenario = scenario)#.set_index("year")
            doys2plot = days_scenario.doy.where(days_scenario).values.flatten()
            x, kde = vonmises_kde(doys2plot[~np.isnan(doys2plot)] * 2 * np.pi / 365, 180)
            axs[i].plot(x, kde, color = scenario_colors[scenario], label = scenario)
        axs[i].set_xticks(np.array(doy_first_day_month) * 2 * np.pi / 365, 'JFMAMJJASOND')
        axs[i].set_yticks([])
    axs[0].set_title("Climate events")
    axs[1].set_title("Energy events")
    axs[2].set_title("Compound events")
    axs[2].legend(fontsize = "small", loc = "lower left")
    plt.suptitle("Seasonality of the events")
    
    plt.tight_layout()

def event_stripplot(var_days, ax, index= "date", title = '', color = None, fill_between_kws = dict()):
    """
    bool_series (pd.Series): Boolean series where the days when the condition is met are True, and the others are false
    ax (matplotlib.axes._axes.Axes): axis object on which to draw
    title (str): title for the time series
    color (str): color for the time series
    """

    ax.fill_between(var_days[index], np.where(var_days, 1, 0), color = color, **fill_between_kws)
    ax.set_ylim(0.1,0.9)
    ax.set_yticks([])
    ax.set_title(title)

def nb_events_barplot(events_dict, period_len_dict, ax, palette = dict()):
    """
    events_dict (dict): dictionary containing the events as output of find_events
    period_len_dict (dict): dictionary containing the duration of the period for each dataset in events_dict
    ax (matplotlib.axes._axes.Axes): axis object on which to draw
    palette (dict): dictionary containing the color for the events_dict keys
    """
    for i, a in enumerate(events_dict):
        if a in palette.keys():
            ax.bar([i], [len(events_dict[a]) / period_len_dict[a]], label = a, color = palette[a],)
        else:
            ax.bar([i], [len(events_dict[a]) / period_len_dict[a]], label = a,)
    ax.set_xticks(np.arange(len(events_dict)), events_dict.keys(), rotation = 90)
    sns.despine(ax=ax)

def event_duration_histplot(events_dict, ax, palette = dict(), legend = True):
    """
    events_dict (dict): dictionary containing the events as output of find_events
    ax (matplotlib.axes._axes.Axes): axis object on which to draw
    palette (dict): dictionary containing the color for the events_dict keys
    legend (bool): whether to display the legend or not
    """
    
    for a in events_dict:
        duration = [len(event) for event in events_dict[a]]
        if a in palette.keys():
            sns.histplot(duration, label = a, ax = ax, kde = True, bins = np.arange(-0.5,max(duration) + 1), fill = False, element = "step", alpha = 0.5, color = palette[a])
        else:
            sns.histplot(duration, label = a, ax = ax, kde = True, bins = np.arange(-0.5,max(duration) + 1), fill = False, element = "step", alpha = 0.5,)
    ax.set_xlim(0.5)
    if legend: ax.legend()
    sns.despine(ax=ax)

doy_first_day_month = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
def event_seasonnality_histplot(doys, ax, palette = dict(), legend = True):
    """
    events_dict (dict): dictionary containing the events as output of find_events
    ax (matplotlib.axes._axes.Axes): axis object on which to draw
    palette (dict): dictionary containing the color for the events_dict keys
    legend (bool): whether to display the legend or not
    """
    
    for a in events_dict:
        doys = [event[0].dayofyear for event in events_dict[a]]
        H = np.histogram(doys, bins = np.arange(0.5,366+1,6))
        H_theta = H[1] * 2 * np.pi / 366
        theta_mid = (H_theta[:-1] + H_theta[1:]) / 2
        width = H_theta[1] - H_theta[0]
        if a in palette.keys():
            ax.bar(theta_mid, H[0], width = width, bottom = 0, alpha = 0.5, color = palette[a], label = a)
        else:
            ax.bar(theta_mid, H[0], width = width, bottom = 0, alpha = 0.5, label = a)
    ax.set_xticks(np.array(doy_first_day_month) * 2 * np.pi / 366, 'JFMAMJJASOND')
    if legend: ax.legend()
# TODO : circular kde (Use : https://stackoverflow.com/questions/28839246/scipy-gaussian-kde-and-circular-data ?)
