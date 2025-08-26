import re
import numpy as np

scenario_colors = {
    "historical": "rgb(0,0,0)",
    "SP119": "rgb(0,173,207)",
    "SP126": "rgb(23,60,102)",
    "SP245": "rgb(247,148,32)",
    "SP370": "rgb(231,29,37)",
    "SP585": "rgb(149,27,30)",
}

model_linestyles = {
    "ERA5": "solid",
    "AWCM": "dash",
    "BCCS": "dashdot",
    "CMR5": "dot",
    "ECE3": "solid",     
    "MEHR": "longdashdot", 
    "MRM2": "longdash",
}

doy_first_day_month = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]

def _rgb_to_rgba(rgb_str, alpha=0.2):
    """Convert 'rgb(r,g,b)' string to 'rgba(r,g,b,a)' string."""
    nums = re.findall(r'\d+', rgb_str)   # extract numbers
    r, g, b = map(int, nums)
    return f'rgba({r},{g},{b},{alpha})'

def vonmises_kde(data, kappa, n_bins=100):
    from scipy.special import i0
    bins = np.linspace(-np.pi, np.pi, n_bins)
    x = np.linspace(-np.pi, np.pi, n_bins)
    # integrate vonmises kernels
    kde = np.exp(kappa*np.cos(x[:, None]-data[None, :])).sum(1)/(2*np.pi*i0(kappa))
    kde /= np.trapezoid(kde, x=bins)
    return bins, kde