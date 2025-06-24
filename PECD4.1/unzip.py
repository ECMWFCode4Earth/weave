import os
import sys
import shutil
import zipfile
from pathlib import Path

trash = False # Set to True if you want to throw away the zipped files

# Import config
config_dir = os.path.abspath("../")
sys.path.append(config_dir)

from config import BDD_PATH

PECD_BDD_PATH = Path.joinpath(BDD_PATH, 'PECD4.1')

if trash:
    from config import TRASH_PATH
    # Create trash folder
    os.makedirs(TRASH_PATH, exist_ok=True)

files_to_unzip=[f for f in Path().glob('**/*.zip')]

for input_file in files_to_unzip:

    # Determine where file should be unzipped and create if necessary
    output_path = Path.joinpath(PECD_BDD_PATH,input_file.parent)
    os.makedirs(output_path, exist_ok=True)

    # Actually unzip the file (if it does not already exists)
    with zipfile.ZipFile(input_file, 'r') as zip_ref:
        if not os.path.isfile(Path.joinpath(output_path,zip_ref.namelist()[0])):
            print(f'Unzipping file {input_file} to {output_path}')
            zip_ref.extractall(output_path)

    # Trash if necessary
    if trash:
        shutil.move(input_file, TRASH_PATH)