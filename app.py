from flask import Flask
from flask_sqlalchemy import SQLAlchemy

class Configuration(object):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://'
    SQLALCHEMY_BINDS = {
        'chainState': 'mysql+mysqlconnector://',
    }

application = Flask(__name__)
application.config.from_object(Configuration)
db = SQLAlchemy(application)