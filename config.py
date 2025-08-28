import importlib.util
from pathlib import Path

# Read hostname to determine how to configure 
from socket import gethostname
host = gethostname()

import getpass
username = getpass.getuser()

# --- ECMWF JupyterHub ---
if host.endswith('bullx'):
    BDD_VERSION = 4.2
    BDD_PATH = Path('/perm/gbr6848/')
    CACHE_DATA_PATH = Path('/ec/res4/scratch/'+username)

# --- ECMWF JupyterHub Clément ---
if host.startswith('jupyter'):
    BDD_VERSION = 4.2
    BDD_PATH = Path(f'/home/{username}/scratch')
    CACHE_DATA_PATH = Path(f'/home/{username}/scratch/cache')

# --- IPSL Mesocenter: Spirit ---
elif host.startswith("spirit"):
    #LOCAL PATHS
    BDD_VERSION = 42
    BDD_PATH = Path('/modfs/project/')
    CACHE_DATA_PATH = Path('/data/sbourdin/PECD42_cache_data/')
    TRASH_PATH = Path('/scratchu/sbourdin/PECD42_trash')

# --- LOCAL ---
else: 
    # Easy: Add you paths below
    
    # Advanced: Local hidden config file (To keep your paths private when contributing)
    _local_config = Path(__file__).with_name("local_config.py")
    if _local_config.exists():
        spec = importlib.util.spec_from_file_location("local_config", _local_config)
        local_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(local_config)
    
        # update globals with anything defined in local_config
        globals().update({
            k: v for k, v in vars(local_config).items() if not k.startswith("_")
        })

# PECD4.2 parameters

CLIM_VARS = ['10WS','100WS','GHI','TA','TP'] 
ENER_VARS = ['SPV','WOF','WON'] 
# -- GLOBAL VARIABLES -- #

CLIM_VARS_DICT = {'10WS':
                    {'name': '10m wind speed',
                        'units': 'm/s',
                        'min': 0,
                        'max': 30,
                        'step': 0.5,
                        'default': 3.5,
                    },
                  '100WS':
                    {'name': '100m wind speed',
                        'units': 'm/s',
                        'min': 0,
                        'max': 30,
                        'step': 1,
                        'default': 3.5,
                    },
                  'GHI':
                      {'name': 'Surface solar radiation downwards',
                        'units': 'W/m²',
                        'min': 0,
                        'max': 1000,
                        'step': 50,
                        'default': 300,
                      },
                  'TA':
                      {'name': '2m temperature',
                        'units': '°C',
                        'min': -10,
                        'max': 50,
                        'step': 1,
                        'default': 5,
                      },
                  'TP':
                      {'name': 'Total precipitation',
                        'units': 'mm',
                        'min': 0,
                        'max': 1000,
                        'step': 50,
                        'default': 100,
                      },
                  }

ENER_VARS_DICT = {'SPV':'Solar generation capacity factor',
                  'WOF':'Wind power offshore capacity factor',
                  'WON':'Wind power onshore capacity factor',
                  }

ENER_VARS_TECHNOS = {
    'SPV': {'60':'Industrial rooftop',
            '61':'Residential rooftop',
            '62':'Utility-scale fixed',
            '63':'Utility-scale 1-axis tracking',
            },
    'WOF': {'20':'Existing technologies',
            '21':'SP316 HH155',
            '22':'SP370 HH155',
            },
    'WON': {'30':'Existing technologies',
            '31':'SP199 HH100',
            '32':'SP199 HH150',
            '33':'SP199 HH200',
            '34':'SP277 HH100',
            '35':'SP277 HH150',
            '36':'SP277 HH200',
            '37':'SP335 HH100',
            '38':'SP335 HH150',
            '39':'SP335 HH200',
            },
}

FREQUENCIES_DICT = {"H":'Hourly',
                    "D":'Daily',
                    "M":'Monthly',
                    "Y":'Yearly',}

MODEL_NAMES = ["ERA5", "AWI-_AWCM", "BCC-_BCCS", "CMCC_CMR5", "ECEC_ECE3", "MPI-_MEHR", "MRI-_MRM2"]

SCENARIOS = ["historical", "SP126", "SP245", "SP370", "SP585"]

COUNTRIES_LIST = ['AL','AT','BA','BE','BG','CH','CY','CZ','DE','DK','DZ','EE','EG','EH','EL','ES','FI','FR','HR','HU','IE','IL','IS','IT','JO','LB','LI','LT','LU','LV','LY','MA','MD','ME','MK','MT','NL','NO','PL','PS','PT','RO','RS','SE','SI','SK','SY','TN','TR','UA','UK','XK']

COUNTRIES_DICT = {'AL': 'Albania', 'AT': 'Austria',
                  'BA': 'Bosnia and Herzegovina', 'BE': 'Belgium', 'BG': 'Bulgaria',
                  'CH': 'Switzerland', 'CY': 'Cyprus', 'CZ': 'Czech Republic',
                  'DE': 'Germany', 'DK': 'Denmark', 'DZ': 'Algeria',
                  'EE': 'Estonia', 'EG': 'Egypt', 'EH': 'Western Sahara', 'EL': 'EL', 'ES': 'Spain',
                  'FI': 'Finland', 'FR': 'France',
                  'HR': 'Croatia', 'HU': 'Hungary',
                  'IE': 'Ireland', 'IL': 'Israel', 'IS': 'Iceland', 'IT': 'Italy', 'JO': 'Jordan',
                  'LB': 'Lebanon', 'LI': 'Liechtenstein', 'LT': 'Lithuania', 'LU': 'Luxembourg', 'LV': 'Latvia', 'LY': 'Libya',
                  'MA': 'Morocco', 'MD': 'Moldova, Republic of', 'ME': 'Montenegro', 'MK': 'Macedonia, the Former Yugoslav Republic of', 'MT': 'Malta',
                  'NL': 'Netherlands', 'NO': 'Norway',
                  'PL': 'Poland', 'PS': 'Palestine, State of', 'PT': 'Portugal',
                  'RO': 'Romania', 'RS': 'Serbia',
                  'SE': 'Sweden', 'SI': 'Slovenia', 'SK': 'Slovakia', 'SY': 'Syrian Arab Republic',
                  'TN': 'Tunisia', 'TR': 'Turkey',
                  'UA': 'Ukraine', 'UK': 'UK', 'XK': 'XK'}

model_aliases = {
    "historical":"historical",
    "cmcc_cm2_sr5":"CMR5",
    "ec_earth3":"ECE3", 
    "mpi_esm1_2_hr":"MEHR", 
}