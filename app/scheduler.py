from apscheduler.schedulers.background import BackgroundScheduler
from app.utils.email import send_email_with_pdf

scheduler = BackgroundScheduler()
scheduler.start()

def schedule_email(pdf_path: str, recipient: str, delay_minutes: int = 60):
    scheduler.add_job(
        send_email_with_pdf,
        'date',
        run_date=None,  # will set below
        args=[pdf_path, recipient]
    )
