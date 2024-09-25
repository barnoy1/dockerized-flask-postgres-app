import logging
import os
import pprint
from typing import List
import yaml
from app.utilities.conf.slconfig import SLConfig
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from app import logger


db = SQLAlchemy()


class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:password@db:5432/custom_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PROCESS_CONFIG = SLConfig.fromfile('app/data/proc.yaml')
    from pprint import pprint
    logger.info(pprint(PROCESS_CONFIG))
