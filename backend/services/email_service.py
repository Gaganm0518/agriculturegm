"""
Email service.
Handles sending emails using Flask-Mail.
"""

from flask import current_app, render_template
from flask_mail import Message
from backend.extensions import mail
import threading


def send_async_email(app, msg):
    """Send email asynchronously to avoid blocking the request."""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {str(e)}")


def send_email(subject, recipients, html_body):
    """Helper to construct and send an email."""
    if not isinstance(recipients, list):
        recipients = [recipients]
        
    msg = Message(
        subject,
        recipients=recipients,
        html=html_body,
        sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@smartagri.com')
    )
    
    # Send email in background thread
    app = current_app._get_current_object()
    thread = threading.Thread(target=send_async_email, args=(app, msg))
    thread.daemon = True
    thread.start()


def send_welcome_email(user):
    """Send welcome email to new user."""
    try:
        html = render_template('emails/welcome.html', user=user)
        send_email('Welcome to AI Smart Agriculture!', user.email, html)
    except Exception as e:
        current_app.logger.error(f"Error preparing welcome email: {str(e)}")


def send_prediction_report(user, prediction_type, data):
    """Send a summary of a prediction to the user."""
    try:
        html = render_template('emails/prediction_report.html', user=user, type=prediction_type, data=data)
        subject = f"Your {prediction_type.replace('_', ' ').title()} Report"
        send_email(subject, user.email, html)
    except Exception as e:
        current_app.logger.error(f"Error preparing prediction report email: {str(e)}")


def send_password_reset(user, token):
    """Send password reset link."""
    try:
        reset_url = f"http://127.0.0.1:5000/reset-password.html?token={token}"
        html = render_template('emails/reset_password.html', user=user, reset_url=reset_url)
        send_email('Password Reset Request', user.email, html)
    except Exception as e:
        current_app.logger.error(f"Error preparing password reset email: {str(e)}")
