from .plot_utils import scenario_colors, model_linestyles, vonmises_kde, _rgb_to_rgba
from .events import count_events
import plotly.graph_objects as go

import numpy as np

def event_count_barplot(df):
    """
    Plot number of events per scenario with multi-model mean (bar)
    and individual model values (dots with distinct markers).
    """
    # Count events per year, then aggregate
    df_counts = count_events(df)
    grouped = df_counts.groupby(["scenario", "model"])["n_events"].mean().reset_index()
    scenario_means = grouped.groupby("scenario")["n_events"].mean().reset_index()

    fig = go.Figure()

    # Define marker symbols for models
    models = grouped["model"].unique()
    marker_symbols = [
        "circle", "square", "diamond", "cross", "x", "triangle-up",
        "triangle-down", "star", "hexagon"
    ]
    symbol_map = {m: marker_symbols[i % len(marker_symbols)] for i, m in enumerate(models)}

    for scenario in df.scenario.cat.categories: # grouped["scenario"].unique():
        scen_data = grouped[grouped["scenario"] == scenario]
        mean_val = scenario_means.loc[scenario_means["scenario"] == scenario, "n_events"].values[0]

        if scenario == "historical":
            hover_template = f"{scenario} (ERA5): " + "%{y:.2f}<extra></extra>"
        else:
            hover_template = f"{scenario} (multi-model mean): " + "%{y:.2f}<extra></extra>"
        # Add bar (multi-model mean) with transparency
        fig.add_trace(go.Bar(
            x=[scenario],
            y=[mean_val],
            name=scenario,
            marker_color=scenario_colors[scenario],
            opacity=0.5,  # semi-transparent so dots are visible
            legendgroup=scenario,
            showlegend=True,   # only this shows in legend
            hovertemplate=hover_template
        ))

        # Add scatter (dots for individual models with black border)
        for _, row in scen_data.iterrows():
            fig.add_trace(go.Scatter(
                x=[scenario],
                y=[row["n_events"]],
                mode="markers",
                name=row["model"],
                legendgroup=scenario,
                showlegend=False,  # hide individual markers from legend
                marker=dict(
                    color=scenario_colors[scenario],
                    symbol=symbol_map[row["model"]],
                    size=10,
                    line=dict(color="black", width=1)  # black border
                ),
                hovertemplate=(
                    f"Model: {row['model']}<br>"
                    f"Scenario: {scenario}<br>"
                    f"Events: {row['n_events']:.2f}<extra></extra>"
                )
            ))

    fig.update_layout(
        barmode="overlay",
        xaxis_title="Scenario",
        yaxis_title="Number of Events",
        title="Number of Events per Scenario",
        legend=dict(
            groupclick="togglegroup"
        )
    )
    return fig

def event_duration_hist(e):
    
    ## 0. Computations
    # Convert durations to days
    e["duration_days"] = e["duration"].astype(int) * 1e-9 / 3600 / 24
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
    
        # 1. Histogram step + fill
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
    
        # 2. Mean vertical line
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

    # 3. Layout
    fig.update_layout(
        #template = "simple_white",
        xaxis_title = "Duration (days)",
        yaxis_title = "Proportion"
    )

    return fig

def event_seasonality_kde(d): 

    ## 0. Computations
    # Compute days of year
    d["doy"] = d.time.dt.dayofyear
    
    fig = go.Figure()
    
    for scenario in np.unique(d.scenario):
        d_scenario = d.sel(scenario = scenario)
        # Compute multi-model mean kde for this scenario
        L = []
        for m in np.unique(d_scenario.model):
            d_m = d_scenario.sel(model = m)
            doys4kde = d_m.doy.where(d_m, drop = True).values
            if len(doys4kde) > 0:
                L.append(vonmises_kde(doys4kde * 2 * np.pi / 365, 180))
        theta, r = L[0][0]* 180/np.pi, np.array(L)[:,1].mean(axis = 0)

        # 1. Plot multi-model mean kde
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

    ## Layout
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

    # TODO : Mettre les mois dans le sens anti-trigo
    
    return fig
