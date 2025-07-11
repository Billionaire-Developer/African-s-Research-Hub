from app import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    fullname = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, index=True)
    country = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(64), index=True, default='student')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Abstracts(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text, nullable=False)
    field = db.Column(db.String(128), index=True, nullable=False)
    institution = db.Column(db.String(128), index=True, nullable=False)
    country = db.Column(db.String(64), index=True, nullable=False)
    year = db.Column(db.Integer, index=True, nullable=False)
    keywords = db.Column(db.String(256), nullable=True)
    status = db.Column(db.String(64), default='pending')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('Users', backref=db.backref('abstracts', lazy=True))
    date_submitted = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc)) # Default to current UTC time during submition

    def __repr__(self):
        return f'<Abstract: {self.title}, Status: {self.status}>'
