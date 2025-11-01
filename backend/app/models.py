from app import db, login
from flask_login import UserMixin
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    firstname = db.Column(db.String(128), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, index=True)
    fullname = db.Column(db.String(225), nullable=False)
    country = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.now(timezone.utc), index=True)
    role = db.Column(db.String(64), index=True, default='student')
    abstracts = db.relationship('Abstracts', backref='author', lazy='dynamic')
    notifications = db.relationship('Notifications', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User ID: {self.id}, Fullname: {self.fullname}, Email: {self.email}, Role: {self.role}>"


class Abstracts(db.Model):
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
    date_submitted = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc)) # Default to current UTC time during submition

    def __repr__(self):
        return f'<Abstract: {self.title}, Abstract ID: {self.id} Status: {self.status}>'


class Payments(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    abstract_id = db.Column(db.Integer, db.ForeignKey('abstracts.id'), index=True)
    amount = db.Column(db.Float, default=1.99, nullable=False)
    currency = db.Column(db.String(64), default='USD')
    status = db.Column(db.String(64), default='pending', index=True)
    payment_date = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    method = db.Column(db.String(64), default='PayChangu', nullable=False)
    abstract = db.relationship('Abstracts', backref=db.backref('payments', lazy=True))
    transaction_id = db.Column(db.String(128), nullable=False) # PayChangu transaction ID
    payment_link = db.Column(db.String(255), nullable=False) # Generated checkout URL

    # Realationship to Invoices
    invoice = db.relationship('Invoices', backref='payment', uselist=False)
    
    def __repr__(self):
        return f'''<Payment ID: {self.id}, Abstract ID: {self.abstract_id}, Currency: {self.currency}\n,
    Amount: {self.amount}, Method: {self.method}, Status: {self.status}'''
    

class Invoices(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    abstract_id = db.Column(db.Integer, db.ForeignKey('abstracts.id'), index=True)
    invoice_url = db.Column(db.String(255), index=True, nullable=False)
    amount = db.Column(db.Float, default=1.99, nullable=False)
    generated_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    due_date = db.Column(db.DateTime, default=datetime.now(timezone.utc) + timedelta(weeks=2), nullable=True)
    paid = db.Column(db.Boolean, default=False, index=True)
    abstract = db.relationship('Abstracts', backref=db.backref('invoices', lazy=True))

    # Realationship to Payments
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=True)
    
    def __repr__(self):
        return f'''<Invoice ID: {self.id}, Abstract ID: {self.abstract_id}, Generated At: {self.generated_date}, 
    Due Date: {self.due_date}, Paid: {self.paid}\n Invoice URL:{self.invoice_url}'''


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    abstract_id = db.Column(db.Integer, db.ForeignKey('abstracts.id'), index=True)
    admin_id = db.Column(db.Integer, index=True)
    comment = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Feedback ID: {self.id}, Abstract ID: {self.abstract_id}, Admin ID: {self.admin_id}, Created At: {self.created_at}>"


class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    message = db.Column(db.String(255), nullable=False)
    read = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f"<NOtification ID: {self.id}, User ID: {self.user_id}, Read: {self.read}>"


class BlogPosts(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    author = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    body = db.Column(db.String(510), nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<BlogPost ID: {self.id}, Author: {self.author}, Created At: {self.created_at}>"


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Contact ID: {self.id}, Name: {self.name}, Email: {self.email}, Created At: {self.created_at}>"


class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc))
    user = db.relationship('Users', backref=db.backref('reviews', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat(),
            'user_name': self.user.fullname if self.user else 'Anonymous'
        }
    
    def __repr__(self):
        return f"<Review ID: {self.id}, Rating: {self.rating}, User: {self.user_id}>"


class PasswordResetToken(db.Model):
    """Stores password reset tokens with expiry"""
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(500), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    # Relationship
    user = db.relationship('Users', backref='reset_tokens')
    
    def __repr__(self):
        return f'<PasswordResetToken {self.token[:20]}... for user {self.user_id}>'
    
    def is_expired(self):
        """Check if token has expired"""
        return datetime.now(timezone.utc) > self.expires_at
    
    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.used and not self.is_expired()


@login.user_loader
def load_user(id):
    return Users.query.get(int(id))