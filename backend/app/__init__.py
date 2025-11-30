from flask import Flask
from app.config import config
from app.extensions import db, migrate, login, mail, cors, limiter, PayChanguClient

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load config
    if not isinstance(config_name, str):
         app.config.from_object(config_name)
    else:
        app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", f"{app.config['WEBSITE_URL'] or app.config['FRONTEND_URL']}"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"],
            "support_credentials": True
        }
    })
    limiter.init_app(app)
    
    # Initialize PayChangu Client
    # We store it in app.extensions or just make it available globally via current_app if we attached it
    # Since PayChanguClient is a simple class, we can just instantiate it and attach to app
    if app.config.get('PAYCHANGU_SECRET'):
        app.paychangu_client = PayChanguClient(secret_key=app.config['PAYCHANGU_SECRET'])
    
    login.login_view = 'main.login' # Updated to blueprint endpoint

    # Register Blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
