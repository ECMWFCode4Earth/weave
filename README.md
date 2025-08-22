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
Open it in your Jupyter environment, and run its only cell (you can hide it for later). An interactive interface will appear, that allows you to select your parameters with interactive buttons, and generate the figures automatically. You can then save the figures as desired. 

## Use the "expert" notebook


## Notes on the WeavePy back-end package
All the functions underpinning the WEAVE visualisation platform are stored in a package named `weavepy`.

# Understand WEAVE's visualisations
