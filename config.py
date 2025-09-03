"""
Configuration module for determining BDD paths and cache data paths
based on the current host and username.

- Supports ECMWF JupyterHub (with and without HPC)
- Supports IPSL Mesocenter: Spirit
- Allows for local custom configuration via local_config.py

Variables:
    BDD_VERSION: Version of the BDD dataset
    BDD_PATH: Path to the BDD dataset
    CACHE_DATA_PATH: Path for cached data (user-specific)
"""

import importlib.util
from pathlib import Path
from socket import gethostname
import getpass
import warnings  # Added for proper warning reporting

# Read hostname & username to determine configuration
host = gethostname()
username = getpass.getuser()

# --- ECMWF JupyterHub with HPC ---
if host.endswith('bullx'):
    BDD_VERSION = 4.2
    BDD_PATH = Path('/perm/gbr6848/')
    CACHE_DATA_PATH = Path('/ec/res4/scratch') / username

# --- ECMWF JupyterHub without HPC ---
elif host.startswith('jupyter'):
    BDD_VERSION = 4.2
    BDD_PATH = Path('/home') / username / 'scratch'
    CACHE_DATA_PATH = BDD_PATH / 'cache'

# --- IPSL Mesocenter: Spirit ---
elif host.startswith("spirit"):
    BDD_VERSION = 42
    BDD_PATH = Path('/modfs/project/')
    # Choose between data or scratch dir
    CACHE_DATA_PATH = Path('/data') / username  # Persistent data
    # CACHE_DATA_PATH = Path('/scratchu') / username  # For temporary storage

# --- LOCAL ---
else:
    ############################### LOCAL USER PATHS ###############################
    # Easy: Add your paths below

    #BDD_PATH = Path('/path/to/your/bdd')  # Example: Path('/home/username/data/bdd')
    #CACHE_DATA_PATH = Path('/path/to/your/cache')  # Example: Path('/home/username/data/cache')
    #BDD_VERSION = 4.2

    ################################################################################

    # Advanced: Local hidden config file (To keep your paths private when contributing)
    # Create a file named local_config.py in the same directory as this config.py
    # and define BDD_PATH, CACHE_DATA_PATH, and BDD_VERSION there.
    #DO NOT MODIFY THE LINES BELOW

    _local_config = Path(__file__).with_name("local_config.py")
    if _local_config.exists():
        try:
            spec = importlib.util.spec_from_file_location("local_config", _local_config)
            local_config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(local_config)

            # update globals with the config vars if they exist
            ALLOWED_CONFIG_VARS = {'BDD_PATH', 'CACHE_DATA_PATH', 'BDD_VERSION'}
            globals().update({
                k: getattr(local_config, k) for k in ALLOWED_CONFIG_VARS if hasattr(local_config, k)
            })
        except Exception as e:
            warnings.warn(f"Failed to load local_config.py: {e}", RuntimeWarning)
    else:
        warnings.warn(
            "No local_config.py found. If you setup the local variables directly in config.py, ignore this message.",
            RuntimeWarning,
        )