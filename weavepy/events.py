import pandas as pd

def identify_problematic_events(climate_daily, energy_daily, climate_variable_comparison = '<', climate_variable_threshold = 0,
                                energy_variable_comparison = '<', energy_variable_threshold = 0.5, ):
    # Climate condition
    if climate_variable_comparison == '<':
        condition1 = climate_daily < climate_variable_threshold
    elif climate_variable_comparison == '<=':
        condition1 = climate_daily <= climate_variable_threshold
    elif climate_variable_comparison == '>':
        condition1 = climate_daily > climate_variable_threshold
    elif climate_variable_comparison == '>=':
        condition1 = climate_daily >= climate_variable_threshold

    # Energy condition
    if energy_variable_comparison == '<':
        condition2 = energy_daily < energy_variable_threshold
    elif energy_variable_comparison == '<=':
        condition2 = energy_daily <= energy_variable_threshold
    elif energy_variable_comparison == '>':
        condition2 = energy_daily > energy_variable_threshold
    elif energy_variable_comparison == '>=':
        condition2 = energy_daily >= energy_variable_threshold
    return condition1 & condition2
                                

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
