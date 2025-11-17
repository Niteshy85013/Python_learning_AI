import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('ITS_SECRET_KEY') or 'change-this-secret-key'
    # e.g. postgresql://username:password@localhost:5432/itsdb
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:Password@localhost:5432/ai_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Limits for submission evaluation (used in evaluator)
    CODE_EXECUTION_TIME = 3  # seconds allowed for restricted execution
