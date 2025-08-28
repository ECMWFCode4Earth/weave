import plotly.graph_objects as go
from .plot_utils import scenario_colors, model_linestyles
from .events import count_events

def nb_event_timeseries(events, rolling_window=21):
    """
    Plot number of events over time:
    - Individual model lines (faint, distinct dash)
    - Multi-model mean (thick, solid)
    - Legend shows only mean; clicking legend hides all traces for that scenario
    - Custom hover showing value, year range, scenario, and model
    """
    # Compute rolling counts
    N_events = count_events(events)
    Nroll = (
        N_events.groupby(["model", "scenario"])[["year","n_events"]]
        .rolling(rolling_window, center=True)
        .mean()
        .reset_index()
    )

    # Multi-model mean
    mm_mean = Nroll.groupby(["scenario","year"])["n_events"].mean().reset_index()

    fig = go.Figure()

    half_window = rolling_window // 2

    # 1. Add individual model lines
    for scenario in Nroll["scenario"].unique():
        scen_data = Nroll[Nroll["scenario"]==scenario]
        for model in scen_data["model"].unique():
            model_data = scen_data[scen_data["model"]==model]
            # Only keep rows without NaN in 'n_events' or 'year'
            model_data = model_data.dropna(subset=["year", "n_events"])
            fig.add_trace(go.Scatter(
                x=model_data["year"],
                y=model_data["n_events"],
                mode="lines",
                line=dict(color=scenario_colors[scenario], dash=model_linestyles[str(model[-4:])]),
                legendgroup=scenario,
                name=scenario,        # legendgroup key
                showlegend=False,     # hide from legend
                opacity=0.2,
                hovertemplate=(
                    "Scenario: %{customdata[0]}<br>"
                    "Model: %{customdata[1]}<br>"
                    "Value: %{y:.2f}<br>"
                    "Year range: %{customdata[2]}–%{customdata[3]}<extra></extra>"
                ),
                customdata=[
                    [scenario, model, int(y-half_window), int(y+half_window)]
                    for y in model_data["year"]
                ]
            ))

    # 2. Add multi-model mean
    for scenario in mm_mean["scenario"].unique():
        data = mm_mean[mm_mean["scenario"]==scenario].dropna(subset=["year","n_events"])
        fig.add_trace(go.Scatter(
            x=data["year"],
            y=data["n_events"],
            mode="lines",
            line=dict(color=scenario_colors[scenario], width=4, dash="solid"),
            name=scenario,
            legendgroup=scenario,
            showlegend=True,
            hovertemplate=(
                "Scenario: %{customdata[0]}<br>"
                "Value: %{y:.2f}<br>"
                "Year range: %{customdata[1]}–%{customdata[2]}<extra></extra>"
            ),
            customdata=[
                [scenario, int(y-half_window), int(y+half_window)]
                for y in data["year"]
            ]
        ))

    # Layout
    fig.update_layout(
        title="Number of Events Over Time",
        xaxis_title="Year",
        yaxis_title="Number of Events",
        legend=dict(
            groupclick="togglegroup",
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    return fig
