import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import seaborn as sns
import numpy as np
import pandas as pd

scenario_colors = {
    "historical":'k',
    "SP119": np.array([0,173,207])/256,
    "SP126": np.array([23,60,102])/256,
    "SP245": np.array([247,148,32])/256,
    "SP370": np.array([231,29,37])/256,
    "SP585": np.array([149,27,30])/256,
}

scenario_colors_plotly = {
    "historical": "black",
    "SP119": "rgb(0,173,207)",
    "SP126": "rgb(23,60,102)",
    "SP245": "rgb(247,148,32)",
    "SP370": "rgb(231,29,37)",
    "SP585": "rgb(149,27,30)",
}

model_linestyles = {
    "ERA5":'-',
    "AWCM":'--',
    "BCCS":'-.',
    "CMR5":':',
    "ECE3":(0, (3, 1, 1, 1, 1, 1)),
    "MEHR":(0,(1,5)), # Densely dotted
    "MRM2":(5,(10,3)), # long dashes
    'AWI-_AWCM':'--',
    'BCC-_BCCS':'-.',
    "CMCC_CMR5":':',
    "ECEC_ECE3":(0, (3, 1, 1, 1, 1, 1)), #densely dashdotdotted
    'MPI-_MEHR':(0,(1,5)), # Densely dotted
    'MRI-_MRM2':(5,(10,3)), # long dashes
}

model_linestyles_plotly = {
    "ERA5": "solid",
    "AWCM": "dash",
    "BCCS": "dashdot",
    "CMR5": "dot",
    "ECE3": "solid",     
    "MEHR": "longdashdot", 
    "MRM2": "longdash",
}

def nb_event_timeseries(N_climate_events, N_energy_events, N_compound_events):
    fig, axs = plt.subplots(3, figsize = [12, 8], sharex = True) 
    Nrolls = {}
    for i, N in enumerate([N_climate_events, N_energy_events, N_compound_events]):
        for scenario in N_climate_events.scenario.unique():
            Nrolls[str(scenario)] = {}
            for model in N_climate_events.model.unique():
                N2plot = N[(N.scenario == scenario) & (N.model == model)].set_index("year")
                # Raw data
                #N2plot.eventID.plot(ax = axs[i], alpha = 0.25, 
                #                    c = scenario_colors[scenario], linestyle = model_linestyles[model])
                #axs[i].plot(N2plot.year, N2plot.eventID, alpha = 0.5,
                #            c = scenario_colors[scenario], linestyle = model_linestyles[model])
                # Running mean
                Nroll = N2plot.eventID.rolling(20, center = True).mean()
                Nrolls[str(scenario)][str(model)] = Nroll
                Nroll.plot(ax = axs[i], 
                           c = scenario_colors[scenario], 
                           linestyle = model_linestyles[model], 
                          alpha = 0.5)
            mm_mean = pd.concat(list(Nrolls[scenario].values())).rename(scenario).reset_index().groupby("year").mean()
            mm_mean.plot(ax = axs[i], linewidth = 5, color = scenario_colors[scenario],)
        axs[i].set_ylabel("#events")
    axs[0].set_title("Climate events")
    axs[1].set_title("Energy events")
    axs[2].set_title("Compound events")
    plt.suptitle("Evolution of the number of events")
    plt.tight_layout()

def event_duration_hist(climate_events, energy_events, compound_events):
    fig, axs = plt.subplots(3, figsize = [10, 10], sharex = True) # TODO: Rolling mean
    for i, e in enumerate([climate_events, energy_events, compound_events]):
        e["duration_days"] = e["duration"].astype(int) * 1e-9 / 3600 / 24
    
        # Scenarios
        for scenario in e.scenario.unique():
            e2plot = e[(e.scenario == scenario)].set_index("year")
            sns.histplot(data = e2plot, x = "duration_days", ax = axs[i], 
            color = scenario_colors[scenario], element = "step", alpha = 0.1,
            bins = np.arange(0.5,30,1), stat = "proportion", linewidth = 2,
            )
            mean = e2plot.duration_days.mean()
            axs[i].axvline(x = mean, color = scenario_colors[scenario], label = scenario)
    axs[0].set_title("Climate events")
    axs[1].set_title("Energy events")
    axs[2].set_title("Compound events")
    plt.suptitle("Duration of the events")
    plt.legend()
    plt.xlim(0,10)
    plt.tight_layout()

def vonmises_kde(data, kappa, n_bins=100):
    from scipy.special import i0
    bins = np.linspace(-np.pi, np.pi, n_bins)
    x = np.linspace(-np.pi, np.pi, n_bins)
    # integrate vonmises kernels
    kde = np.exp(kappa*np.cos(x[:, None]-data[None, :])).sum(1)/(2*np.pi*i0(kappa))
    kde /= np.trapezoid(kde, x=bins)
    return bins, kde

doy_first_day_month = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]

def event_seasonality_kde(climate_days, energy_days, compound_days):
    fig, axs = plt.subplots(1, 3, subplot_kw = dict(projection = "polar"), figsize = (15,5))
    for i, e in enumerate([climate_days, energy_days, compound_days]):
        e["doy"] = e["time"].dt.dayofyear
        for scenario in np.unique(e.scenario):
            days_scenario = e.sel(scenario = scenario)#.set_index("year")
            doys2plot = days_scenario.doy.where(days_scenario).values.flatten()
            x, kde = vonmises_kde(doys2plot[~np.isnan(doys2plot)] * 2 * np.pi / 365, 180)
            axs[i].plot(x, kde, color = scenario_colors[scenario], label = scenario)
        axs[i].set_xticks(np.array(doy_first_day_month) * 2 * np.pi / 365, 'JFMAMJJASOND')
        axs[i].set_yticks([])
    axs[0].set_title("Climate events")
    axs[1].set_title("Energy events")
    axs[2].set_title("Compound events")
    axs[2].legend(fontsize = "small", loc = "lower left")
    plt.suptitle("Seasonality of the events")
    
    plt.tight_layout()

    
def event_stripplot(var_days, ax, index= "date", title = '', color = None, fill_between_kws = dict()):
    """
    bool_series (pd.Series): Boolean series where the days when the condition is met are True, and the others are false
    ax (matplotlib.axes._axes.Axes): axis object on which to draw
    title (str): title for the time series
    color (str): color for the time series
    """

    ax.fill_between(var_days[index], np.where(var_days, 1, 0), color = color, **fill_between_kws)
    ax.set_ylim(0.1,0.9)
    ax.set_yticks([])
    ax.set_title(title)

def nb_events_barplot(events_dict, period_len_dict, ax, palette = dict()):
    """
    events_dict (dict): dictionary containing the events as output of find_events
    period_len_dict (dict): dictionary containing the duration of the period for each dataset in events_dict
    ax (matplotlib.axes._axes.Axes): axis object on which to draw
    palette (dict): dictionary containing the color for the events_dict keys
    """
    for i, a in enumerate(events_dict):
        if a in palette.keys():
            ax.bar([i], [len(events_dict[a]) / period_len_dict[a]], label = a, color = palette[a],)
        else:
            ax.bar([i], [len(events_dict[a]) / period_len_dict[a]], label = a,)
    ax.set_xticks(np.arange(len(events_dict)), events_dict.keys(), rotation = 90)
    sns.despine(ax=ax)

def event_duration_histplot(events_dict, ax, palette = dict(), legend = True):
    """
    events_dict (dict): dictionary containing the events as output of find_events
    ax (matplotlib.axes._axes.Axes): axis object on which to draw
    palette (dict): dictionary containing the color for the events_dict keys
    legend (bool): whether to display the legend or not
    """
    
    for a in events_dict:
        duration = [len(event) for event in events_dict[a]]
        if a in palette.keys():
            sns.histplot(duration, label = a, ax = ax, kde = True, bins = np.arange(-0.5,max(duration) + 1), fill = False, element = "step", alpha = 0.5, color = palette[a])
        else:
            sns.histplot(duration, label = a, ax = ax, kde = True, bins = np.arange(-0.5,max(duration) + 1), fill = False, element = "step", alpha = 0.5,)
    ax.set_xlim(0.5)
    if legend: ax.legend()
    sns.despine(ax=ax)

doy_first_day_month = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
def event_seasonnality_histplot(doys, ax, palette = dict(), legend = True):
    """
    events_dict (dict): dictionary containing the events as output of find_events
    ax (matplotlib.axes._axes.Axes): axis object on which to draw
    palette (dict): dictionary containing the color for the events_dict keys
    legend (bool): whether to display the legend or not
    """
    
    for a in events_dict:
        doys = [event[0].dayofyear for event in events_dict[a]]
        H = np.histogram(doys, bins = np.arange(0.5,366+1,6))
        H_theta = H[1] * 2 * np.pi / 366
        theta_mid = (H_theta[:-1] + H_theta[1:]) / 2
        width = H_theta[1] - H_theta[0]
        if a in palette.keys():
            ax.bar(theta_mid, H[0], width = width, bottom = 0, alpha = 0.5, color = palette[a], label = a)
        else:
            ax.bar(theta_mid, H[0], width = width, bottom = 0, alpha = 0.5, label = a)
    ax.set_xticks(np.array(doy_first_day_month) * 2 * np.pi / 366, 'JFMAMJJASOND')
    if legend: ax.legend()
# TODO : circular kde (Use : https://stackoverflow.com/questions/28839246/scipy-gaussian-kde-and-circular-data ?)
