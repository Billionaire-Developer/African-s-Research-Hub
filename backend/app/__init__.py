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
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

app.config.from_object(Config)

CORS(
    app, resources={
        r"/api/*": {
            "origins": [f"{app.config['WEBSITE_URL'] or app.config['FRONTEND_URL']}"],
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

# Initialize Flask-Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# PayChangu client
load_dotenv()
PAYCHANGU_SECRET = os.getenv('PAYCHANGU_SECRET')
paychangu_client = PayChanguClient(secret_key=PAYCHANGU_SECRET)

from app import routes, models
