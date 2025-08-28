from plotly.subplots import make_subplots
import plotly.graph_objects as go
from .plot_time_series import nb_event_timeseries
from .plot_hists import event_count_barplot, event_duration_hist, event_seasonality_kde
import numpy as np
from .plot_utils import *


def nb_event_timeseries_multi(dfs, rolling_window=21, titles=["Climate events", "Energy events", "Compound events"]):
    """
    Multi-panel wrapper for nb_event_timeseries.
    Subplots vertically, shared x-axis, only one legend per scenario.
    Panels closer together.
    """

    # Manage input
    n = len(dfs)
    assert (titles is None) | (len(titles) == n), "titles must be None or have the same length as dfs"
    if titles is None:
        titles = [f"Dataset {i+1}" for i in range(n)]

    # Create vertical subplots, reduce vertical spacing
    fig = make_subplots(
        rows=n, cols=1,
        subplot_titles=titles,
        shared_xaxes=True,
        vertical_spacing=0.05  # smaller spacing between panels
    )

    for i, df in enumerate(dfs):
        subfig = nb_event_timeseries(df, rolling_window=rolling_window)
        for trace in subfig.data:
            # Only show legend in first panel
            trace.showlegend = (i==0 and trace.showlegend)
            fig.add_trace(trace, row=i+1, col=1)

    # Layout
    fig.update_layout(
        height=300*n,
        legend=dict(
            groupclick="togglegroup",
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
        title=dict(
            text=(
                "Evolution of the number of events (running mean over "+str(rolling_window)+" years)<br><sup>Faint lines represent individual models, thick lines the multi-model mean.</sup>"
            ),
        )
    )
    
    # X-axis label only for bottom subplot
    fig.update_xaxes(title_text="Year", row=n, col=1)
    
    # Y-axis label for all subplots
    fig.update_yaxes(title_text="Number of Events")

    return go.FigureWidget(fig)

    
def event_count_barplot_multi(dfs, historical_period, future_period, titles=["Climate events", "Energy events", "Compound events"]):
    """
    Create horizontal subplots of event count barplots for multiple datasets.
    
    Parameters
    ----------
    dfs : list of pandas.DataFrame
        Each DataFrame must contain columns [model, scenario, year, eventID].
    titles : list of str, optional
        Titles for each subplot (default: Dataset 1, Dataset 2, ...).
    """

    # Manage input
    n = len(dfs)
    assert (titles is None) | (len(titles) == n), "titles must be None or have the same length as dfs"
    if titles is None:
        titles = [f"Dataset {i+1}" for i in range(n)]

    # Filter period 
    if (len(historical_period)) > 0 & (len(future_period) > 0):
        for df in dfs:
            df = df[df.year.between(*historical_period) | df.year.between(*future_period)]
        
    n = len(dfs)
    if titles is None:
        titles = [f"Dataset {i+1}" for i in range(n)]

    # Create horizontal subplots
    fig = make_subplots(
        rows=1, cols=n,
        subplot_titles=titles,
        shared_yaxes=True
    )

    for i, df in enumerate(dfs):
        subfig = event_count_barplot(df)
        for trace in subfig.data:
            # Keep scenario grouping consistent across panels
            trace.legendgroup = trace.legendgroup
            # Show legend only for first subplot (avoid duplicates)
            trace.showlegend = (i == 0 and trace.showlegend)
            fig.add_trace(trace, row=1, col=i+1)
    
    # Set common y-axis title
    fig.update_yaxes(title_text="Number of events per year", row=1, col=1)
    
    # Update layout
    fig.update_layout(
        height=500,
        width=300*n,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            traceorder="normal",
            itemsizing="constant",
            groupclick="togglegroup"
        ),
        title_text="Event Counts<br><sup>Dots represent the different models and the bars show the multi-model mean for each scenario.</sup>"
    )

    return go.FigureWidget(fig)
    
def event_duration_hist_multi(dfs, historical_period, future_period, titles=None):
    """
    Create a vertical multi-panel histogram figure across multiple dfs.
    Each panel shows duration histograms for scenarios with mean lines.
    """

    # Filter period 
    if (len(historical_period)) > 0 & (len(future_period) > 0):
        for df in dfs:
            df = df[df.year.between(*historical_period) | df.year.between(*future_period)]
    
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
        subfig = event_duration_hist(df)
        for trace in subfig.data:
            # Link legend items across panels
            trace.legendgroup = trace.name.split()[0]  # base scenario name
            trace.showlegend = (i == 0) and ("mean" not in trace.name)  
            # ^ only show the histogram traces in the first panel's legend
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
        title_text="Event Duration",
        xaxis_title="Duration (days)",
        yaxis_title="Proportion"
    )

    return go.FigureWidget(fig)


def event_seasonality_kde_multi(dfs, historical_period, future_period, titles=None):
    """
    Multi-panel polar KDE plots for event seasonality.

    Parameters
    ----------
    dfs : list
        List of xarray dfs [climate_days, energy_days, compound_days].
    titles : list of str, optional
        Titles for each subplot. Defaults to ["Climate events", "Energy events", "Compound events"].
    """

    # Filter period 
    if (len(historical_period)) > 0 & (len(future_period) > 0):
        for df in dfs:
            df["year"] = df.time.dt.year
            cond1 = (df.year >= historical_period[0]) & (df.year <= historical_period[1])
            cond2 = (df.year >= future_period[0]) & (df.year <= future_period[1])
            df = df.where(cond1 | cond2, drop = True)
    
    n = len(dfs)
    if titles is None:
        titles = ["Climate events", "Energy events", "Compound events"][:n]

    # Create subplot grid: one row, n polar plots
    fig = make_subplots(
        rows=1, cols=n,
        subplot_titles=titles,
        specs=[[{"type": "polar"}] * n]
    )

    for i, d in enumerate(dfs):
        d["doy"] = d.time.dt.dayofyear

        # TODO : Call the individual function here!!
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
