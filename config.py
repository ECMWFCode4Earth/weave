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

