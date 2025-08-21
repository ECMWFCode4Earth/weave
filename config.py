import importlib.util
from pathlib import Path

# Read hostname to determine how to configurate
from socket import gethostname
host = gethostname()

# --- ECMWF JupyterHub ---
if host == 'ad6-206.bullx':
    pass # TODO
# --- IPSL Mesocenter: Spirit ---
elif host.startswith("spirit"):
    #LOCAL PATHS
    BDD_VERSION = 42
    BDD_PATH = Path('/modfs/project/')
    OUTPUT_DATA_PATH = Path('/modfs/project/')
    CACHE_DATA_PATH = Path('/data/sbourdin/PECD42_cache_data/')
    TRASH_PATH = Path('/scratchu/sbourdin/PECD42_trash')

else: 
    # --- Advanced: Local hidden config file (To keep your paths private when contributing) ---
    _local_config = Path(__file__).with_name("local_config.py")
    if _local_config.exists():
        spec = importlib.util.spec_from_file_location("local_config", _local_config)
        local_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(local_config)
    
        # update globals with anything defined in local_config
        globals().update({
            k: v for k, v in vars(local_config).items() if not k.startswith("_")
        })

CLIM_VARS = ['10WS','100WS','GHI','TA','TP'] 
ENER_VARS = ['SPV','WOF','WON'] 

ENER_VARS_TECHNOS = {
    'SPV': ['60','61','62','63'],
    'WOF': ['20','21','22'],
    'WON': ['30','31','32','33','34','35','36','37','38','39'],
}

MODEL_NAMES = ["ERA5", "AWI-_AWCM", "BCC-_BCCS", "CMCC_CMR5", "ECEC_ECE3", "MPI-_MEHR", "MRI-_MRM2"]

COUNTRIES_LIST = ['AL','AT','BA','BE','BG','CH','CY','CZ','DE','DK','DZ','EE','EG','EH','EL','ES','FI','FR','HR','HU','IE','IL','IS','IT','JO','LB','LI','LT','LU','LV','LY','MA','MD','ME','MK','MT','NL','NO','PL','PS','PT','RO','RS','SE','SI','SK','SY','TN','TR','UA','UK','XK']

model_aliases = {
    "historical":"historical",
    "cmcc_cm2_sr5":"CMR5",
    "ec_earth3":"ECE3", 
    "mpi_esm1_2_hr":"MEHR", 
}