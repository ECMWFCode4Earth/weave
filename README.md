![image](logo/Logo/Slide1.png)

This is a Code for Earth Project developed by **[Stella Bourdin](https://stella-bourdin.github.io/) & [Clément Devenet](https://climatclement.com/)**,
mentored by Edward Comyn-Platt, Laurent Dubus, Aron Zuicker, Stefano Cordeddu & Niclas Rieger.

In this project, we will develop an interactive platform to visualise the impact of extreme weather events on the energy systems.
We will leverage the latest Pan-European Climate Database and Jupyter Notebooks to build our platform.
It will allow users to identify and analyse problematic events using historical data and future climate scenarios.

[Code for Earth page](https://codeforearth.ecmwf.int/project/weave-weather-energy-analysis-visualisation-for-extremes/)

# WEAVE Concept
WEAVE is designed to study compound climate-energy events that put the electricity systems under stress in the present and future climate.
The user defines problem days based on a threshold on a variable, and problematic events are defined as a continuous series of problem days. 
For example, times when the temperature is cold (corresponding to high heating demand) and renewable energy production is low, threaten the demand-supply balance. 

# How to use WEAVE?
## Download the repository and the data
### On your own laptop
1. Download or clone the present repository.
2. Make sure you work in an environment where all the packages listed in `environment.yml` are installed.
3. Download the [data archive](TODO: Provide link), and unzip it in the folder of your choice.
4. Setup config.py

### On the [ECMWF JupyterHub](jupyterhub.ecmwf.int/)
0. If you do not already, obtain an ECMWF account and setup your access to the JupyterHub (may require you to setup ssh parameters if you have HPC access)
1. ??

## Use the "Easy" interactive notebook
The `easy.ipynb` notebook is an interactive notebook meant for direct and easy use. It allows for the comparison of events concerning one climate and one energy variable, for one country and one technology. 
Open it in your Jupyter environment, and run its only cell (you can hide it for later). An interactive interface will appear, allowing you to select your parameters with interactive buttons and generate the figures automatically.
Once your selection is complete, click the "Execute" button to process the data.
After changing your selection, click "Execute" for the program to reprocess the data.
You can then save the figures as desired.

**Disclamer:** The processing time can vary greatly depending on the existance or not of cached data corresponding to your selection. It is not unusual for it to run for about 10 minutes before displaying the results. The long process involves the time aggregation of climate and energy variables, as well as country extraction.

**NB**: By default, the aggregation will be performed over the entire data. It is in particular to be noted for Solar Photovoltaic variables, that are going to be averaged without taking into account day/night times. 

**Here is a description of the selectable parameters:**
- Climate Variable: The climate parameter you want to study
- Energy Variable: The energy parameter you want to study
    - Technology: The type of technology attached to the energy variable you want to study
Aggregation Frequency: Raw data is hourly; you can aggregate it to daily, monthly, or yearly.
- Aggregation Function: The method of aggregation, for instance, if you select "monthly" and "max", the program will take for each month the maximum hourly value
- Country: The country you want to study
- Historical Period: The range of years between which ERA5 data is considered
- Future Period: The range of years between which projected data is considered
- Climate Operator: The logical operator used to define climate events (e.g., month where climate variable >= climate threshold)
- Climate Threshold: The value used to define climate events along with the climate operator (e.g., month where climate variable >= 4)
- Energy Operator: The logical operator used to define energy events (e.g. month where the energy variable < energy threshold)
- Energy Threshold: The value used to define energy events along with the energy operator (e.g., month where energy variable < 0,2)
- Models: The models you want to consider (ERA5 only covers the historical period; the other models only cover the future period)
- Scenarios: The scenarios you want to consider (historical only applies to ERA5; "SP" stands for "SSP" (i.e., Shared Socioeconomic Pathways))

## Use the "expert" notebook

## About the plotly plots
We use plotly to display the figures, which allows user interactions with the plots. In particular, you can: 
* hover over the plot to show the values to the different points/lines/bar;
* click on legend entries to hide/show the corresponding traces;
* double-click on legend entries to isolate a given trace.


## Notes on the WeavePy back-end package
All the functions underpinning the WEAVE visualisation platform are stored in a package named `weavepy`.

# Understand WEAVE's visualisations
