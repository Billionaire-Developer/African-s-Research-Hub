import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # CRITICAL: Remove hardcoded secret key - use environment variable only
    SECRET_KEY = os.environ.get("SECRET_KEY")
    
    # If SECRET_KEY is not set, raise an error instead of using a default
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is not set. Please set it in your .env file.")
    
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "app.db")
    
    # Fixed typo: MODIFICATION -> MODIFICATIONS
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Additional recommended settings
    WTF_CSRF_ENABLED = True