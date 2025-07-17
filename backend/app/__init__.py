from flask import Flask
from config import Config
# from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# CORS(app)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models