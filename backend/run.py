from app import app
from app.models import db, Users, Abstracts, Payments, Invoices, Feedback, Notifications, BlogPosts

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
    app.run(debug=True, port=5000)