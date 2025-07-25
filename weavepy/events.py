import pandas as pd
from tqdm import tqdm
import numpy as np

def identify_pb_days(var_daily, var_comparison, var_threshold):
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
    events = []
    event_ongoing = False
    eventID = 0
    for d, pb in zip(T, series):
        #d = pd.to_datetime(d)
        if pb:
            if not event_ongoing: # New event
                event_ongoing = True
                start = d
                end = d
            elif event_ongoing: # Event in continuing
                end = d
        else:
            if event_ongoing:
                event_ongoing = False
                events.append([model, scenario, country, eventID, start, end, d-start])
                eventID += 1
    #events = pd.DataFrame(events, columns = ["eventID", "start", "end", "duration"]
    #            ).assign(model = model, scenario = scenario, country = country)
    #if "start" in events.columns:
    #    events = events.assign(year = events.start.dt.year)
    return events

def identify_events_whole_base(pb_days):
    events = []
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