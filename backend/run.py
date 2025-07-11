from app import app
from app.models import db, Users, Abstracts

@app.shell_context_processor
def make_shell_context():
    from app.models import Users, Abstracts
    return {'db': db, 'Users': Users, 'Abstracts': Abstracts}

if __name__ == '__main__':
    app.run(debug=True, port=5000)