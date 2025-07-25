from flask import Flask
from config import Config
from flask_cors import CORS # type: ignore
from flask_login import LoginManager # type: ignore
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail # type: ignore

app = Flask(__name__)
CORS(app)
app.config.from_object('config.Config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'  # Redirect to login page if not authenticated
mail = Mail(app)

from app import routes, models
