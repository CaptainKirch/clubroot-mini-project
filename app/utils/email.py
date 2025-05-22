import smtplib
from email.message import EmailMessage
import os

def send_email_with_pdf(pdf_path: str, recipient: str):
    msg = EmailMessage()
    msg['Subject'] = "Clubroot Equipment Report"
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = recipient
    msg.set_content("Attached is your report PDF.")

    with open(pdf_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename='report.pdf')

    with smtplib.SMTP(os.getenv("EMAIL_HOST"), int(os.getenv("EMAIL_PORT"))) as server:
        server.starttls()
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
        server.send_message(msg)
