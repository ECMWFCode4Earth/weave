import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import seaborn as sns
import numpy as np

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
def event_seasonnality_histplot(events_dict, ax, palette = dict(), legend = True):
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
