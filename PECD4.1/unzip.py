import os
import sys
import shutil
import zipfile
from pathlib import Path

config_dir = os.path.abspath("../")
sys.path.append(config_dir)

from config import BDD_PATH, TRASH_PATH

os.makedirs(TRASH_PATH, exist_ok=True)

files_to_unzip=[f for f in Path().glob('**/*.zip')]

for input_file in files_to_unzip:

    output_path = BDD_PATH.joinpath(input_file.parent)
    os.makedirs(output_path, exist_ok=True)

    print(f'Unzipping file {input_file} to {output_path}')

    with zipfile.ZipFile(input_file, 'r') as zip_ref:
        zip_ref.extractall(output_path)

#    shutil.move(input_file, TRASH_PATH)