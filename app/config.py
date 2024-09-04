import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:password@db:5432/mydatabase'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
