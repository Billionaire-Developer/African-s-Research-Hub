from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from paychangu import PayChanguClient
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
mail = Mail()
cors = CORS()
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")
paychangu_client = None # Will be initialized in create_app or accessed via current_app if needed, 
                        # but PayChanguClient doesn't seem to have an init_app method based on previous usage.
                        # Let's check how it was used. 
                        # It was: paychangu_client = PayChanguClient(secret_key=PAYCHANGU_SECRET)
                        # We might need to handle this differently or just initialize it globally if it's stateless enough,
                        # or wrap it. For now, let's keep it as is but we might need to lazy load it.

# Actually, PayChanguClient seems to be a simple wrapper. 
# We can just instantiate it in create_app or keep it here if we can access config.
# Since we need config to init it, we should probably do it in create_app or make a wrapper.
# For now, let's leave it as None and init in create_app, or just not have it here and init in create_app and store in app.extensions.
