from config import pwd_context
import string
import secrets
import random
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def generate_reset_token():
    characters = string.ascii_letters + string.digits  + string.punctuation
    token = ''.join(secrets.choice(characters) for _ in range(random.randint(16,32)))
    return token

def send_email_with_token(email, token, sender = os.getenv("REPORTING_EMAIL"), password = os.getenv("REPORTING_EMAIL_PASSWORD")):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = email
    msg['subject'] = "Podscale Password Reset Token"
    body = f'Password Reset Token\n\n{token}\n\nDO NOT SHARE THIS WITH ANYONE.'
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, email, msg.as_string())
    except Exception as e:
        return f"failed to send email: {e}"
    finally:
        server.quit()