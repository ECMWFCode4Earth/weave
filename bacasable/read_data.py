import os
import sys
import pandas as pd
import glob
from tqdm import tqdm

config_dir = os.path.abspath("../")
sys.path.append(config_dir)

from config import BDD_PATH

data_path= BDD_PATH.joinpath('PECD4.1')

def get_data(variable:str='', period:str='', model:str='',verbose:bool=True) -> pd.DataFrame:
    global BDD_PATH, data_path

    # --
    # This block ensures that the user provides valid inputs for variable, period, and model.
    # The "explore_database" function is called to display the available options and help the user make a selection.

    while (variable == '')|(os.path.exists(str(data_path.joinpath(variable)))==False):
        variable = '' # Reset variable if the one provided by the user doesn't exist
        explore_database(variable, period)
        variable = input("Enter the variable name (from the list above): ")

    while (period == '')|(os.path.exists(str(data_path.joinpath(variable, period)))==False):
        period =''
        explore_database(variable, period)
        period = input("Enter the period (from the list above): ")

    if period == 'historical':
        model = ''
    else:
        while (model == '')|(os.path.exists(str(data_path.joinpath(variable, period, model)))==False):
            model = ''
            explore_database(variable, period)
            model = input("Enter the model name (from the list above): ")
    # --
    
    files_paths = [f for f in glob.glob(str(data_path.joinpath(variable, period, model))+'/*.csv')]
    
    data = pd.concat((pd.read_csv(f, sep=',',comment='#') for f in files_paths), ignore_index=True)

    data["Date"] = pd.to_datetime(data.Date) # Convert date to pandas datetime
    data = data.set_index("Date")
    
    if verbose:
        print()
        print(f'Data loaded from {data_path.joinpath(variable, period, model)}')

    return(data)

def explore_database(variable, period):
    '''
    This function explores the database and prints the available variables, periods, and models.
    It uses the global variable `data_path` to determine the root directory of the database.
    It prints the structure of the database 1 level down from the provided variable (and period if provided).
    '''
    global data_path
    exploration_depth = 1 if variable=='' else 2 if period=='' else 3
    for root, dirs, files in os.walk(str(data_path)):
        if (exploration_depth==1)|((exploration_depth==2)&(variable in root))|((exploration_depth==3)&(variable+'/'+period in root)):
            level = root.replace(str(data_path), '').count(os.sep)
            indent = ' ' * 4 * (level)
            if level == exploration_depth:
                print('{}{}'.format(indent, os.path.basename(root)))
