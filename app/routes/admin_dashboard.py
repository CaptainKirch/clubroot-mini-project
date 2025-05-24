from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import os
import csv
from pathlib import Path
import random
from app.scheduler import schedule_email  # make sure this is imported!

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def verify_admin_session(request: Request):
    if not request.session.get("admin_logged_in"):
        return RedirectResponse("/admin-login", status_code=303)

@router.get("/admin-dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    if not request.session.get("admin_logged_in"):
        return RedirectResponse("/admin-login", status_code=303)

    csv_path = "app/data/form_log.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        records = df.to_dict(orient="records")
    else:
        records = []

    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "records": records
    })

@router.get("/view-pdf/{submission_id}")
def view_pdf(submission_id: str):
    pdf_path = f"app/data/submissions/{submission_id}/form_submission_template.pdf"
    if os.path.exists(pdf_path):
        return FileResponse(pdf_path, media_type='application/pdf', filename="report.pdf")
    return {"error": "PDF not found"}


@router.get("/pending-requests", response_class=HTMLResponse)
def pending_requests(request: Request):
    csv_path = "app/data/pending_pin_requests.csv"
    try:
        df = pd.read_csv(csv_path)
        records = df.to_dict(orient="records")
    except Exception:
        records = []

    return templates.TemplateResponse("pending_requests.html", {
        "request": request,
        "records": records
    })

@router.get("/approve-request/{company_name}")
def approve_request(company_name: str):
    pending_path = Path("app/data/pending_pin_requests.csv")
    approved_path = Path("app/data/client_pins.csv")

    # Load all pending requests
    with open(pending_path, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Find and remove the approved row
    remaining = [r for r in rows if r["company_name"] != company_name]
    approved = [r for r in rows if r["company_name"] == company_name]

    if approved:
        pin = str(random.randint(1000, 9999))
        with open(approved_path, "a", newline="") as f:
            writer = csv.writer(f)
            if not approved_path.exists() or approved_path.stat().st_size == 0:
                writer.writerow(["client_name", "pin"])
            writer.writerow([company_name, pin])

        # Optional: send welcome email here using approved[0]["email"]

    # Overwrite pending file with remaining entries
    with open(pending_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["company_name", "full_name", "email", "phone", "province"])
        writer.writeheader()
        writer.writerows(remaining)

    return RedirectResponse("/pending-requests", status_code=303)

@router.get("/delete-request/{company_name}")
def delete_request(company_name: str):
    pending_path = Path("app/data/pending_pin_requests.csv")

    with open(pending_path, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    remaining = [r for r in rows if r["company_name"] != company_name]

    with open(pending_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["company_name", "full_name", "email", "phone", "province"])
        writer.writeheader()
        writer.writerows(remaining)

    return RedirectResponse("/pending-requests", status_code=303)

@router.get("/admin-login", response_class=HTMLResponse)
def admin_login(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@router.post("/admin-login")
def do_admin_login(request: Request, password: str = Form(...)):
    if password == os.getenv("ADMIN_PASSWORD"):
        request.session["admin_logged_in"] = True
        return RedirectResponse("/admin-dashboard", status_code=303)
    return templates.TemplateResponse("admin_login.html", {
        "request": request,
        "error": "Invalid password"
    })

@router.get("/approve-pdf/{submission_id}")
def approve_pdf(submission_id: str):
    df = pd.read_csv("app/data/form_log.csv")

    # Update status to approved
    df.loc[df["submission_id"] == submission_id, "status"] = "approved"
    df.to_csv("app/data/form_log.csv", index=False)

    # Get email and PDF path
    email_row = df[df["submission_id"] == submission_id]
    if not email_row.empty:
        recipient_email = email_row["email"].values[0]
        pdf_path = f"app/data/submissions/{submission_id}/form_report.pdf"

        # Send email immediately (no delay)
        schedule_email(pdf_path=pdf_path, recipient=recipient_email, delay_minutes=0)

    return RedirectResponse("/admin-dashboard", status_code=303)

@router.post("/update-email/{submission_id}")
async def update_email(submission_id: str, email: str = Form(...)):
    df = pd.read_csv("app/data/form_log.csv")
    df.loc[df["submission_id"] == submission_id, "email"] = email
    df.to_csv("app/data/form_log.csv", index=False)
    return RedirectResponse("/admin-dashboard", status_code=303)
