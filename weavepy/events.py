import pandas as pd
from tqdm import tqdm
import numpy as np

def identify_pb_days(var_daily, var_comparison, var_threshold):
    """
    Mask days based on a user-defined climate condition and threshold.
    Returns a boolean array indicating problematic days.
    """
    comparison_ops = {
        '<': np.less,
        '<=': np.less_equal,
        '>': np.greater,
        '>=': np.greater_equal,
    }
    if var_comparison not in comparison_ops:
        raise ValueError(f"Invalid comparison: {var_comparison}. Use one of {list(comparison_ops.keys())}")
    return comparison_ops[var_comparison](var_daily, var_threshold)                             

def identify_events_one_series(T, series, model="", scenario="", country=""):
    """
    Identify continuous problematic events from a boolean array.
    Returns a list of event records.
    """
    events = []
    event_ongoing = False
    eventID = 0
    start = end = None
    for d, pb in zip(T, series):
        if pb:
            if not event_ongoing:
                event_ongoing = True
                start = d
                end = d
            else:
                end = d
        else:
            if event_ongoing:
                event_ongoing = False
                duration = (end - start) if isinstance(end, (np.datetime64, pd.Timestamp)) else (end-start)
                events.append([model, scenario, country, eventID, start, end, duration])
                eventID += 1
                start = end = None
    # Handle event that goes until last day
    if event_ongoing and start is not None and end is not None:
        duration = (end - start) if isinstance(end, (np.datetime64, pd.Timestamp)) else (end-start)
        events.append([model, scenario, country, eventID, start, end, duration])
    return events

def identify_events_whole_base(pb_days):
    """
    Identify continuous problematic events across all models and scenarios.
    Returns a DataFrame of all events.
    """
    events = []
    # Loop over scenarios and models
    for a in pb_days.model.values:
        for s in pb_days.scenario.values:
            ds = pb_days.sel(model=a, scenario=s)
            country = ds.country.values.item() if "country" in ds.dims and ds.country.size == 1 else ""
            new_events = identify_events_one_series(ds.time.values, ds.squeeze().values, model=a, scenario=s, country=country)
            events.extend(new_events)
    events_df = pd.DataFrame(events, columns=["model", "scenario", "country", "eventID", "start", "end", "duration"])
    if "start" in events_df.columns and pd.api.types.is_datetime64_any_dtype(events_df["start"]):
        events_df = events_df.assign(year=events_df.start.dt.year)
    else:
        events_df = events_df.assign(year=None)
    # Categorical scenario sorting
    sc = events_df["scenario"].unique()
    sc_order = ["historical"] + sorted([str(sp) for sp in sc if str(sp).startswith("SP")])
    events_df["scenario"] = pd.Categorical(events_df["scenario"], sc_order)
    return events_df

def count_events(events):
    """
    Count events per model/scenario/year, filling in missing years with 0.
    Returns a DataFrame with counts per year.
    """
    # Step 1: count events
    counts = events.groupby(["model", "scenario", "year"], observed=False).size()
    # Step 2: build full index per (model, scenario)
    full_index = []
    for (model, scenario), group in events.groupby(["model", "scenario"], observed=False):
        if group["year"].notna().any():
            years = range(int(group["year"].min()), int(group["year"].max()) + 1)
            full_index.extend([(model, scenario, y) for y in years])
    full_index = pd.MultiIndex.from_tuples(full_index, names=["model", "scenario", "year"])
    # Step 3: reindex counts to full index (missing years → 0)
    N_events = counts.reindex(full_index, fill_value=0).reset_index(name="n_events")
    return N_events