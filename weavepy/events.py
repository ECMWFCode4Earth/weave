import pandas as pd

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

def identify_events(series, model = "", scenario = "", country = ""):
    events = pd.DataFrame()
    columns = ["model", "scenario", "country", "eventID", "start", "end", "duration"]
    event_ongoing = False
    eventID = 0
    for d in series.time.values:
        pb = (series.sel(time = d) == True)
        d = pd.to_datetime(d)
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
                event = pd.DataFrame([[model, scenario, country, eventID, start, end, d-start]], columns = columns)
                events = pd.concat([events, event])
                eventID += 1
    if "start" in events.columns:
        events = events.assign(year = events.start.dt.year)
    return events