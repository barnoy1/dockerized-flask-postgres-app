import os

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Config:
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:password@db:5432/custom_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
