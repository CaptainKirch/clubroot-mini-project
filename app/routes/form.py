from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Form, File, UploadFile
from uuid import uuid4
import os
from app.utils import file_io
from app.utils.qr import generate_qr
from app.utils.pdf import generate_pdf
from app.scheduler import schedule_email
import datetime
templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

@router.get("/form", response_class=HTMLResponse)
async def show_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@router.post("/submit")
async def handle_form(
    request: Request,
    client: str = Form(...),
    unit_number: str = Form(...),
    service_date: str = Form(...),
    equipment_description: str = Form(...),
    gps_location: str = Form(...),
    dirt_level: int = Form(...),
    before_left: UploadFile = File(...),
    before_right: UploadFile = File(...),
    technician_name: str = Form(...),
    technician_signature: str = Form(...),
    supervisor_name: str = Form(...),
    supervisor_signature: str = Form(...),
):
    submission_id = str(uuid4())
    save_dir = f"app/data/submissions/{submission_id}"
    os.makedirs(save_dir, exist_ok=True)


    qr_data = f"Unit: {unit_number} | Client: {client} | Date: {service_date}"
    qr_path = f"{save_dir}/qr_code.png"
    generate_qr(qr_data, qr_path)

    await file_io.save_file(before_left, save_dir, "before_left.jpg")
    await file_io.save_file(before_right, save_dir, "before_right.jpg")

    file_io.save_csv(
        {
            "submission_id": submission_id,
            "client": client,
            "unit_number": unit_number,
            "service_date": service_date,
            "equipment_description": equipment_description,
            "gps_location": gps_location,
            "dirt_level": dirt_level,
            "technician_name": technician_name,
            "technician_signature": technician_signature,
            "supervisor_name": supervisor_name,
            "supervisor_signature": supervisor_signature,
        },
        "app/data/form_log.csv"
    )

    form_data = {
        "client": client,
        "unit_number": unit_number,
        "service_date": service_date,
        "equipment_description": equipment_description,
        "gps_location": gps_location,
        "dirt_level": dirt_level,
        "technician_name": technician_name,
        "technician_signature": technician_signature,
        "supervisor_name": supervisor_name,
        "supervisor_signature": supervisor_signature,
}
    images = {
        "before_left": f"{save_dir}/before_left.jpg",
        "before_right": f"{save_dir}/before_right.jpg"
}

    # PDF generation using template background
    template_path = "static/pdf_template.pdf"  # update with your actual path

    pdf_path = f"{save_dir}/form_report.pdf"
    generate_pdf(form_data, images, qr_path, pdf_path, background_template_path=template_path)

    # Delay email by 60 minutes
    run_at = datetime.datetime.now() + datetime.timedelta(minutes=60)
    schedule_email(pdf_path=pdf_path, recipient="marj@albertapowerwash.ca", delay_minutes=60)

    return templates.TemplateResponse("form.html", {
        "request": request,
        "message": "Form submitted successfully!"
    })
