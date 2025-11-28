import os
from flask import Flask
from config import Config
from flask_cors import CORS
from dotenv import load_dotenv
from flask_migrate import Migrate
from app.email_service import mail
from flask_login import LoginManager
from paychangu import PayChanguClient
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(Config)

CORS(
    app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", f"{app.config['WEBSITE_URL'] or app.config['FRONTEND_URL']}"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"],
            "support_credentials": True
        }
    }
)


# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'  # Redirect to login page if not authenticated

# Initialize Flask-Mail
mail.init_app(app)

# PayChangu client
load_dotenv()
PAYCHANGU_SECRET = os.getenv('PAYCHANGU_SECRET')
paychangu_client = PayChanguClient(secret_key=PAYCHANGU_SECRET)

from app import routes, models
