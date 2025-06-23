import smtplib
import os
from email.message import EmailMessage

def send_email_with_pdf(to_email: str, subject: str, body: str, pdf_path: str):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = to_email
    msg.set_content(body)

    # Attach the PDF
    with open(pdf_path, 'rb') as f:
        file_data = f.read()
        filename = os.path.basename(pdf_path)
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=filename)

    # Send email using Gmail SMTP + app password
    with smtplib.SMTP_SSL(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as smtp:
        smtp.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
        smtp.send_message(msg)
