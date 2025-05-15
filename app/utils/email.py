import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..core import config
import logging
import traceback
import os

logger = logging.getLogger(__name__)

async def send_verification_email(email: str, token: str):
    """Send verification email using SMTP"""
    try:
        # Create verification URL
        verification_url = f"http://localhost:8000/auth/verify?email={email}&token={token}"
        
        # Print token for development purposes
        print(f"\n=== DEVELOPMENT MODE ===")
        print(f"Verification URL for {email}: {verification_url}")
        print(f"Token: {token}")
        print(f"=== END DEVELOPMENT INFO ===\n")
        
        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Verify your email address"
        message["From"] = config.MAIL_FROM
        message["To"] = email
        
        # Email body in HTML
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to the Secure File Sharing System!</h2>
            <p>Please click the link below to verify your email address:</p>
            <p><a href="{verification_url}">Verify Email</a></p>
            <p>Or copy and paste this URL into your browser:</p>
            <p>{verification_url}</p>
            <p>This link will expire in 24 hours.</p>
            <p>If you did not sign up for this service, please ignore this email.</p>
        </body>
        </html>
        """
        
        # Plain text version
        text_content = f"""
        Welcome to the Secure File Sharing System!
        
        Please click the link below to verify your email address:
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you did not sign up for this service, please ignore this email.
        """
        
        # Attach parts
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Debug info
        print(f"Sending email to: {email}")
        print(f"Using SMTP server: {config.MAIL_SERVER}")
        print(f"From address: {config.MAIL_FROM}")
        
        # Connect to SMTP server and send email
        try:
            server = smtplib.SMTP(config.MAIL_SERVER, config.MAIL_PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            # Login to email account
            print("Logging in to SMTP server...")
            server.login(config.MAIL_FROM, config.MAIL_PASSWORD)
            
            # Send email
            print("Sending email via SMTP...")
            server.sendmail(config.MAIL_FROM, email, message.as_string())
            server.quit()
            
            logger.info(f"Verification email sent to {email} using SMTP")
            return True
        except Exception as smtp_error:
            logger.error(f"SMTP error: {str(smtp_error)}")
            print(f"SMTP error: {str(smtp_error)}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
        print(f"Email sending error: {str(e)}")
        print(traceback.format_exc())
        
        # For development: Show the verification URL but still return False
        print("\n=== VERIFICATION INFO (FOR DEVELOPMENT ONLY) ===")
        print(f"Email sending failed but here's the verification URL: {verification_url}")
        print("NOTE: User will NOT be created in the database since email sending failed.")
        print("To bypass this in development, modify the signup endpoint to ignore email failures.")
        print(f"=== END VERIFICATION INFO ===\n")
        
        # Still return False to prevent user creation
        return False 