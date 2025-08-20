import importlib.util
from pathlib import Path

from socket import gethostname
host = gethostname()

_local_config = Path(__file__).with_name("local_config.py")
if _local_config.exists():
    spec = importlib.util.spec_from_file_location("local_config", _local_config)
    local_config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(local_config)

    # update globals with anything defined in local_config
    globals().update({
        k: v for k, v in vars(local_config).items() if not k.startswith("_")
    })
    
if host.startswith("spirit"):
    #LOCAL PATHS
    BDD_VERSION = 42
    BDD_PATH = Path('/modfs/project/')
    OUTPUT_DATA_PATH = Path('/modfs/project/')
    CACHE_DATA_PATH = Path('/data/sbourdin/PECD42_cache_data/')
    TRASH_PATH = Path('/scratchu/sbourdin/PECD42_trash')