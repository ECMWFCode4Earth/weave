from pathlib import Path

from socket import gethostname
host = gethostname()

if host.startswith("spirit"):
    #LOCAL PATHS
    BDD_PATH = Path('/modfs/project/')
    OUTPUT_DATA_PATH = Path('/modfs/project/')
