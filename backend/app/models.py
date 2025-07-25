from app import db, login
from flask_login import UserMixin # type: ignore
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


@login.user_loader
def load_user(id):
    return Users.query.get(int(id))


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    fullname = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, index=True)
    country = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.now(timezone.utc), index=True)
    role = db.Column(db.String(64), index=True, default='student')
    submissions = db.relationship('Abstracts', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User ID: {self.id}, Fullname: {self.fullname}, Email: {self.email}, Role: {self.role}>"
    
class Abstracts(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.String(), nullable=False)
    field = db.Column(db.String(80), index=True, nullable=False)
    institution = db.Column(db.String(128), index=True, nullable=False)
    country = db.Column(db.String(50), index=True, nullable=False)
    year = db.Column(db.Integer, index=True, nullable=False)
    keywords = db.Column(db.String(256), nullable=True, index=True)
    status = db.Column(db.String(15), default='pending', index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    author = db.relationship('Users', backref=db.backref('abstracts', lazy=True))
    date_submitted = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc)) # Default to current UTC time during submition

    def __repr__(self):
        return f'<Abstract: {self.title}, Abstract ID: {self.id} Status: {self.status}>'

class Payments(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    abstract_id = db.Column(db.Integer, db.ForeignKey('abstracts.id'), index=True)
    amount = db.Column(db.Float, default=1.99, nullable=False)
    currency = db.Column(db.String(64), default='USD')
    status = db.Column(db.String(64), default='pending', index=True)
    payment_date = db.Column(db.DateTime, nullable=True)
    method = db.Column(db.String(64), default='Bank')
    abstract = db.relationship('Abstracts', backref=db.backref('payments', lazy=True))
    
    def __repr__(self):
        return f'''<Payment ID: {self.id}, Abstract ID: {self.abstract_id}, Currency: {self.currency}\n,
    Amount: {self.amount}, Method: {self.method}, Status: {self.status}'''
    
class Invoices(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    abstract_id = db.Column(db.Integer, db.ForeignKey('abstracts.id'), index=True)
    invoice_url = db.Column(db.String(255), index=True)
    amount = db.Column(db.Float, default=1.99, nullable=False)
    generated_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    due_date = db.Column(db.DateTime, default=datetime.now(timezone.utc) + timedelta(weeks=2), nullable=True)
    paid = db.Column(db.Boolean, default=False, index=True)
    abstract = db.relationship('Abstracts', backref=db.backref('invoices', lazy=True))
    
    def __repr__(self):
        return f'''<Invoice ID: {self.id}, Abstract ID: {self.abstract_id}, Generated At: {self.generated_date}, 
    Due Date: {self.due_date}, Paid: {self.paid}\n Invoice URL:{self.invoice_url}'''

class Feedback(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    abstract_id = db.Column(db.Integer, db.ForeignKey('abstracts.id'), index=True)
    admin_id = db.Column(db.Integer, index=True)
    comment = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Feedback ID: {self.id}, Abstract ID: {self.abstract_id}, Admin ID: {self.admin_id}, Created At: {self.created_at}>"

class Notifications(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    message = db.Column(db.String(255), nullable=False)
    read = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f"<NOtification ID: {self.id}, User ID: {self.user_id}, Read: {self.read}>"

class BlogPosts(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    author = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    body = db.Column(db.String(510), nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<BlogPost ID: {self.id}, Author: {self.author}, Created At: {self.created_at}>"

class Contact(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Contact ID: {self.id}, Name: {self.name}, Email: {self.email}, Created At: {self.created_at}>"
