from app.config import settings
import requests
import smtplib
from email.mime.text import MIMEText




def send_slack(message: str) -> bool:
    if not settings.SLACK_WEBHOOK_URL:
        return False
    try:
        r = requests.post(settings.SLACK_WEBHOOK_URL, json={"text": message}, timeout=10)
        return r.status_code // 100 == 2
    except Exception:
        return False




def send_email(to_email: str, subject: str, body: str) -> bool:
    host = settings.SMTP_HOST
    username = settings.SMTP_USERNAME
    password = settings.SMTP_PASSWORD
    if not (host and username and password):
        return False
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email


    try:
        with smtplib.SMTP(host, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(settings.EMAIL_FROM, [to_email], msg.as_string())
            return True
    except Exception:
        return False