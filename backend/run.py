import os
from app import create_app
from app.extensions import db
from app.models import Users, Abstracts, Payments, Invoices, Feedback, Notifications, BlogPosts

# Get config from environment variable, default to 'development'
config_name = os.getenv('FLASK_CONFIG', 'development')
app = create_app(config_name)

@app.shell_context_processor
def make_shell_context():
    from app.models import Users, Abstracts
    return {
        'db': db,
        'users': Users,
        'invoices': Invoices,
        'payments': Payments,
        'feedback': Feedback,
        'abstracts': Abstracts,
        'blogPosts': BlogPosts,
        'notifications': Notifications,
        
        }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=config_name.DEBUG, port=5000)