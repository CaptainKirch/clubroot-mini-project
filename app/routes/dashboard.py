from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    csv_path = "app/data/form_log.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        records = df.to_dict(orient="records")
    else:
        records = []
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "records": records
    })

@router.get("/view-pdf/{submission_id}")
def view_pdf(submission_id: str):
    pdf_path = f"app/data/submissions/{submission_id}/form_report.pdf"
    if os.path.exists(pdf_path):
        return FileResponse(pdf_path, media_type='application/pdf', filename="report.pdf")
    return {"error": "PDF not found"}
