import pandas as pd

def find_events(series):
    events = []
    event_ongoing = False
    for line in pd.DataFrame(series.rename("problem")).itertuples():
        if (line.problem == True) :
            if not event_ongoing:
                events.append([line.Index]) # Create new event
                event_ongoing = True
            elif event_ongoing:
                events[-1].append(line.Index) # Continue previous event
        else:
            event_ongoing = False
    return events