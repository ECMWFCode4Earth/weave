"""
PECD4.2 parameters and global configuration for climate and energy datasets.
"""

# Climate and energy variable names
CLIM_VARS = ['10WS', '100WS', 'GHI', 'TA', 'TP']
ENER_VARS = ['SPV', 'WOF', 'WON']

# Climate variable parameters
CLIM_VARS_DICT = {
    '10WS': {
        'name': '10m wind speed',
        'units': 'm/s',
        'min': 0,
        'max': 30,
        'step': 0.5,
        'default': 3.5,
    },
    '100WS': {
        'name': '100m wind speed',
        'units': 'm/s',
        'min': 0,
        'max': 30,
        'step': 1,
        'default': 3.5,
    },
    'GHI': {
        'name': 'Surface solar radiation downwards',
        'units': 'W/m²',
        'min': 0,
        'max': 1000,
        'step': 50,
        'default': 300,
    },
    'TA': {
        'name': '2m temperature',
        'units': '°C',
        'min': -10,
        'max': 50,
        'step': 1,
        'default': 5,
    },
    'TP': {
        'name': 'Total precipitation',
        'units': 'mm',
        'min': 0,
        'max': 1000,
        'step': 50,
        'default': 100,
    },
}

# Energy variable long names
ENER_VARS_DICT = {
    'SPV': 'Solar generation capacity factor',
    'WOF': 'Wind power offshore capacity factor',
    'WON': 'Wind power onshore capacity factor',
}

# Energy technology mappings
ENER_VARS_TECHNOS = {
    'SPV': {
        '60': 'Industrial rooftop',
        '61': 'Residential rooftop',
        '62': 'Utility-scale fixed',
        '63': 'Utility-scale 1-axis tracking',
    },
    'WOF': {
        '20': 'Existing technologies',
        '21': 'SP316 HH155',
        '22': 'SP370 HH155',
    },
    'WON': {
        '30': 'Existing technologies',
        '31': 'SP199 HH100',
        '32': 'SP199 HH150',
        '33': 'SP199 HH200',
        '34': 'SP277 HH100',
        '35': 'SP277 HH150',
        '36': 'SP277 HH200',
        '37': 'SP335 HH100',
        '38': 'SP335 HH150',
        '39': 'SP335 HH200',
    },
}

# Frequency dictionary
FREQUENCIES_DICT = {
    "H": "Hourly",
    "D": "Daily",
    "M": "Monthly",
    "Y": "Yearly",
}

# Model and scenario definitions
MODEL_NAMES = [
    "ERA5", "AWI-_AWCM", "BCC-_BCCS", "CMCC_CMR5",
    "ECEC_ECE3", "MPI-_MEHR", "MRI-_MRM2"
]

SCENARIOS = ["historical", "SP126", "SP245", "SP370", "SP585"]

# Country codes and names
COUNTRIES_LIST = [
    'AL', 'AT', 'BA', 'BE', 'BG', 'CH', 'CY', 'CZ', 'DE', 'DK', 'DZ', 'EE', 'EG', 'EH', 'EL', 'ES',
    'FI', 'FR', 'HR', 'HU', 'IE', 'IL', 'IS', 'IT', 'JO', 'LB', 'LI', 'LT', 'LU', 'LV', 'LY', 'MA', 'MD', 'ME',
    'MK', 'MT', 'NL', 'NO', 'PL', 'PS', 'PT', 'RO', 'RS', 'SE', 'SI', 'SK', 'SY', 'TN', 'TR', 'UA', 'UK', 'XK'
]

COUNTRIES_DICT = {
    'AL': 'Albania',
    'AT': 'Austria',
    'BA': 'Bosnia and Herzegovina',
    'BE': 'Belgium',
    'BG': 'Bulgaria',
    'CH': 'Switzerland',
    'CY': 'Cyprus',
    'CZ': 'Czech Republic',
    'DE': 'Germany',
    'DK': 'Denmark',
    'DZ': 'Algeria',
    'EE': 'Estonia',
    'EG': 'Egypt',
    'EH': 'Western Sahara',
    'EL': 'Greece',
    'ES': 'Spain',
    'FI': 'Finland',
    'FR': 'France',
    'HR': 'Croatia',
    'HU': 'Hungary',
    'IE': 'Ireland',
    'IL': 'Israel',
    'IS': 'Iceland',
    'IT': 'Italy',
    'JO': 'Jordan',
    'LB': 'Lebanon',
    'LI': 'Liechtenstein',
    'LT': 'Lithuania',
    'LU': 'Luxembourg',
    'LV': 'Latvia',
    'LY': 'Libya',
    'MA': 'Morocco',
    'MD': 'Moldova',
    'ME': 'Montenegro',
    'MK': 'North Macedonia',
    'MT': 'Malta',
    'NL': 'Netherlands',
    'NO': 'Norway',
    'PL': 'Poland',
    'PS': 'State of Palestine',
    'PT': 'Portugal',
    'RO': 'Romania',
    'RS': 'Serbia',
    'SE': 'Sweden',
    'SI': 'Slovenia',
    'SK': 'Slovakia',
    'SY': 'Syrian Arab Republic',
    'TN': 'Tunisia',
    'TR': 'Turkey',
    'UA': 'Ukraine',
    'UK': 'United Kingdom',
    'XK': 'Kosovo',
}