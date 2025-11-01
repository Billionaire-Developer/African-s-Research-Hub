from flask import render_template, current_app
from flask_mail import Message, Mail
from threading import Thread
import logging

# Initialize Flask-Mail (will be configured in __init__.py)
mail = Mail()

def send_async_email(app, msg):
    """Send email asynchronously to avoid blocking the main thread"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {str(e)}")

def send_email(subject, sender, recipients, text_body, html_body):
    """Send email with both text and HTML versions"""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    
    # Send email asynchronously
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_abstract_confirmation_email(user_email, user_name, abstract_title, abstract_id):
    """Send confirmation email when abstract is submitted"""
    subject = "Abstract Submission Confirmation - African Research Hub"
    
    # Text version
    text_body = f"""
        Hello {user_name}!
        
        Thank you for submitting your abstract titled: "{abstract_title}"
        
        Abstract ID: {abstract_id}
        
        We will review your submission and get back to you as soon as possible.
        
        Best regards,
        African Research Hub Team
    """
    
    # HTML version using template
    html_body = render_template('email_confirmation.html', user_name=user_name, abstract_title=abstract_title, abstract_id=abstract_id)
    send_email(subject, current_app.config['MAIL_DEFAULT_SENDER'], [user_email], text_body, html_body)

def send_payment_confirmation_email(user_email, user_name, amount, currency, invoice_id):
    """Send confirmation email when payment is confirmed"""
    subject = "Payment Confirmation - African Research Hub"
    
    # Text version
    text_body = f"""
        Dear {user_name},

        Your payment of {currency}{amount} has been successfully processed.
        Invoice ID: {invoice_id}

        Your abstract has been published. You can view it from your dashboard.

        Thank you for your payment!

        Best regards,
        African Research Hub Team
    """
    
    # HTML version using template
    html_body = render_template('payment_confirmation.html', user_name=user_name, amount=amount, currency=currency, invoice_id=invoice_id)
    
    send_email(subject, current_app.config['MAIL_DEFAULT_SENDER'], [user_email], text_body, html_body)

def send_abstract_review_email(user_email, user_name, abstract_title, status, feedback=None):
    """Send email when abstract is reviewed (approved/rejected)"""
    if status == "approved":
        subject = "Abstract Approved - African Research Hub"
        status_text = "approved"
    else:
        subject = "Abstract Review Update - African Research Hub"
        status_text = "rejected"
    
    # Text version
    text_body = f"""
        Dear {user_name},

        Your abstract "{abstract_title}" has been {status_text}.

        {f"Feedback: {feedback}" if feedback else ""}

        {"Congratulations! Your abstract has been accepted for publication." if status == "approved" else "Please review the feedback and consider resubmitting with revisions."}

        Best regards,
        African Research Hub Team
    """
    
    # HTML version (you can create a template for this)
    html_body = f"""
        <html>
            <body>
                <h2>Dear {user_name},</h2>
                <p>Your abstract "<strong>{abstract_title}</strong>" has been <strong>{status_text}</strong>.</p>
                {f"<p><strong>Feedback:</strong> {feedback}</p>" if feedback else ""}
                <p>{"Congratulations! Your abstract has been accepted for publication." if status == "approved" else "Please review the feedback and consider resubmitting with revisions."}</p>
                <p>Best regards,<br>African Research Hub Team</p>
            </body>
        </html>
    """
    
    send_email(subject, current_app.config['MAIL_DEFAULT_SENDER'], [user_email], text_body, html_body)

def send_admin_notification_email(abstract_title, author_name, abstract_id):
    """Send notification to admin when new abstract is submitted"""
    subject = "New Abstract Submission - African Research Hub"
    admin_email = current_app.config['ADMIN_EMAIL']
    
    text_body = f"""
        New abstract submitted for review:

        Title: {abstract_title}
        Author: {author_name}
        Abstract ID: {abstract_id}
        Submitted: Just now

        Please log in to the admin dashboard to review.

        African Research Hub System
    """
    
    html_body = f"""
        <html>
            <body>
                <h2>New Abstract Submission</h2>
                <p><strong>Title:</strong> {abstract_title}</p>
                <p><strong>Author:</strong> {author_name}</p>
                <p><strong>Abstract ID:</strong> {abstract_id}</p>
                <p><strong>Submitted:</strong> Just now</p>
                <p>Please log in to the admin dashboard to review.</p>
                <hr>
                <p><em>African Research Hub System</em></p>
            </body>
        </html>
    """
    
    send_email(subject, current_app.config['MAIL_DEFAULT_SENDER'], [admin_email], text_body, html_body)

def send_contact_confirmation_email(user_email, user_name):
    """Send confirmation email to user when they submit a contact inquiry"""
    subject = "We Received Your Message - African Research Hub"
    
    # Text version
    text_body = f"""
        Hello {user_name},

        Thank you for contacting African Research Hub. We have received your message and will get back to you within 24-48 hours.

        If your inquiry is urgent, please don't hesitate to reach out to us directly.

        Best regards,
        African Research Hub Support Team
    """
    
    # Try to use template, fallback to HTML string
    try:
        html_body = render_template('contact_confirmation.html', user_name=user_name)
    except:
        # Fallback HTML version
        html_body = f"""
            <html>
                <body>
                    <h2>Hello {user_name},</h2>
                    <p>Thank you for contacting <strong>African Research Hub</strong>. We have received your message and will get back to you within <strong>24-48 hours</strong>.</p>
                    <p>If your inquiry is urgent, please don't hesitate to reach out to us directly.</p>
                    <p>Best regards,<br><strong>African Research Hub Support Team</strong></p>
                </body>
            </html>
        """
    
    send_email(subject, current_app.config['MAIL_DEFAULT_SENDER'], [user_email], text_body, html_body)

def send_contact_admin_notification_email(contact_name, contact_email, contact_message, contact_id):
    """Send notification to admin when new contact inquiry is submitted"""
    subject = "New Contact Inquiry - African Research Hub"
    admin_email = current_app.config['ADMIN_EMAIL']
    
    # Text version
    text_body = f"""
        New contact inquiry received:

        From: {contact_name}
        Email: {contact_email}
        Contact ID: {contact_id}
        Submitted: Just now

        Message:
        {contact_message}

        Please respond to this inquiry promptly.

        African Research Hub System
    """
    
    # Try to use template, fallback to HTML string
    try:
        html_body = render_template(
            'contact_admin_notification.html', 
            contact_name=contact_name, 
            contact_email=contact_email,
            contact_message=contact_message,
            contact_id=contact_id
        )
    except:
        # Fallback HTML version
        html_body = f"""
            <html>
                <body>
                    <h2>New Contact Inquiry</h2>
                        <p><strong>From:</strong> {contact_name}</p>
                        <p><strong>Email:</strong> <a href="mailto:{contact_email}">{contact_email}</a></p>
                        <p><strong>Contact ID:</strong> {contact_id}</p>
                        <p><strong>Submitted:</strong> Just now</p>
                        <h3>Message:</h3>
                        <p">{contact_message}</p>
                        <p><strong>Action Required:</strong> Please respond to this inquiry promptly.</p>
                    <hr>
                    <p><em>African Research Hub System</em></p>
                </body>
            </html>
        """
    
    send_email(subject, current_app.config['MAIL_DEFAULT_SENDER'], [admin_email], text_body, html_body)

