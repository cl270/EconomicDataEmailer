import smtplib
from email.message import EmailMessage
import os

SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 465))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
FROM_EMAIL = os.getenv('FROM_EMAIL', SMTP_USER)

def format_raw_body(indicator_name, data):
    lines = [f"{indicator_name} Release Data:"]
    for k, v in data.items():
        lines.append(f"{k}: {v}")
    return "\n".join(lines)

def send_email(subject, body, recipients):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = ', '.join(recipients)
    msg.set_content(body)
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

def send_raw_email(indicator_name, data, recipients):
    subject = f"{indicator_name} Release - Raw Data"
    body = format_raw_body(indicator_name, data)
    send_email(subject, body, recipients)

def send_analysis_email(indicator_name, analysis_text, recipients):
    subject = f"{indicator_name} - Analysis"
    body = analysis_text
    send_email(subject, body, recipients)
