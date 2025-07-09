import numpy as np

def get_period_length(model, data):
    years = data.sel(model = model).where(~np.isnan(data.sel(model = model)), drop = True).Date.dt.year
    return (years.max() - years.min() + 1).values

def get_period_min_max(model, data):
    years = data.sel(model = model).where(~np.isnan(data.sel(model = model)), drop = True).Date.dt.year
    return years.min().values, years.max().values