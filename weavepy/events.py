import pandas as pd
from tqdm import tqdm
import numpy as np

def identify_pb_days(var_daily, var_comparison, var_threshold):
    """ Reads user-defined conditions for problematic events and mask them. """
    # Climate condition
    if var_comparison == '<':
        return var_daily < var_threshold
    elif var_comparison == '<=':
        return var_daily <= var_threshold
    elif var_comparison == '>':
        return var_daily > var_threshold
    elif var_comparison == '>=':
        return var_daily >= var_threshold                                

def identify_events_one_series(T, series, model = "", scenario = "", country = ""):
    """ Identify continuous problematic events from one boolean series obtained with `identify_pb_days`. """
    events = []
    event_ongoing = False
    eventID = 0
    for d, pb in zip(T, series):
        if pb: # If the current step is a problematic day
            if not event_ongoing: # New event
                event_ongoing = True
                start = d
                end = d
            elif event_ongoing: # Event continuing
                end = d
        else: # If the current step is a problematic day
            if event_ongoing: # If there was an event going on, stop it
                event_ongoing = False
                events.append([model, scenario, country, eventID, start, end, d-start])
                eventID += 1
    return events

def identify_events_whole_base(pb_days):
    """ Recursively identify continuous problematic events for all the dimensions of the data being handled """
    events = []
    # Loop over scenarios and models
    for a, s in tqdm([(a, s) for a in pb_days.model.values for s in pb_days.scenario.values]):
        ds = pb_days.sel(model = a).sel(scenario = s)
        new_events = identify_events_one_series(ds.time.values, ds.squeeze().values, model = a, scenario = s)
        if len(new_events) > 0: 
            if len(events) > 0:
                events = np.concat([events, new_events])
            else:
                events = new_events.copy()
    events = pd.DataFrame(events, columns = ["model", "scenario", "country", "eventID", "start", "end", "duration"])
    if "start" in events.columns:
        events = events.assign(year = events.start.dt.year)
    return events