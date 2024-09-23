import logging
import os
import pprint
from typing import List
import yaml
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass

logger = logging.getLogger('app_logger')
db = SQLAlchemy()

@dataclass
class Proc:
    name: str
    entry_point: str
    config_file: str

# Function to load YAML and map to the list of Proc objects
def load_process_config(file_path: str) -> List[Proc]:
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        processes = []
        for process in data['processes']:
            proc_obj = Proc(**process['proc'])  
            processes.append(proc_obj)
        return processes

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:password@db:5432/custom_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Load the process mapping into the class variable
    PROCESS_MAPPING = load_process_config('app/utilities/process/proc_mapping.yaml')

    logger.info(pprint.pformat([
        {
            'name': proc.name,
            'entry_point': proc.entry_point,
            'config_file': proc.config_file
        }
        for proc in PROCESS_MAPPING
    ], indent=4))
