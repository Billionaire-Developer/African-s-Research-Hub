
from flask import current_app, render_template
from flask_mail import Message
from app.extensions import mail
from threading import Thread


def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {str(e)}")


def send_email(subject, recipient, text_body, html_body):
    """Send email with both text and HTML versions"""
    msg = Message(
        subject=subject,
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[recipient]
    )
    msg.body = text_body
    msg.html = html_body
    
    # Send asynchronously
    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg)
    ).start()


def send_password_reset_email(user, reset_url):
    """Send password reset email"""
    subject = "Reset Your Password - Conference Portal"
    
    # Text version (fallback)
    text_body = f"""
        Dear {user.fullname},

        You recently requested to reset your password for your Conference Portal account.

        Click the link below to reset your password:
        {reset_url}

        This link will expire in 5 minutes for security reasons.

        If you did not request a password reset, please ignore this email or contact support if you have concerns.

        Best regards,
        African Research Hub Team
    """
    
    # HTML version (rich formatting)
    html_body = render_template(
        'email/password_reset.html',
        user=user,
        reset_url=reset_url
    )
    
    send_email(subject, user.email, text_body, html_body)
