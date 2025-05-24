from fastapi import APIRouter, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from uuid import uuid4
import os
import datetime

from app.utils import file_io
from app.utils.qr import generate_qr
from app.utils.pdf import generate_pdf
from app.scheduler import schedule_email
from app.utils.file_io import remove_background

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
    inspection_notes: str = Form(...),

    # BEFORE
    before_left: UploadFile = File(...),
    before_right: UploadFile = File(...),
    before_underside: UploadFile = File(...),
    before_wheel: UploadFile = File(...),

    # AFTER
    after_left: UploadFile = File(...),
    after_right: UploadFile = File(...),
    after_underside: UploadFile = File(...),
    after_wheel: UploadFile = File(...),

    # DISINFECTION
    disinfect_wheel_1: UploadFile = File(...),
    disinfect_wheel_2: UploadFile = File(...),

    technician_name: str = Form(...),
    technician_signature: str = Form(...),
    supervisor_name: str = Form(...),
    supervisor_signature: str = Form(...),
    technician_email: str = Form(...),  # <-- NEWLY ADDED
):
    submission_id = str(uuid4())
    save_dir = f"app/data/submissions/{submission_id}"
    os.makedirs(save_dir, exist_ok=True)

    # Generate QR
    qr_data = f"Unit: {unit_number} | Client: {client} | Date: {service_date}"
    qr_path = f"{save_dir}/qr_code.png"
    generate_qr(qr_data, qr_path)

    # Save & clean all images
    uploads = {
        "before_left": before_left,
        "before_right": before_right,
        "before_underside": before_underside,
        "before_wheel": before_wheel,
        "after_left": after_left,
        "after_right": after_right,
        "after_underside": after_underside,
        "after_wheel": after_wheel,
        "disinfect_wheel_1": disinfect_wheel_1,
        "disinfect_wheel_2": disinfect_wheel_2
    }

    cleaned_images = {}
    for label, file in uploads.items():
        raw_path = f"{save_dir}/{label}.jpg"
        clean_path = f"{save_dir}/{label}_cleaned.png"

        await file_io.save_file(file, save_dir, f"{label}.jpg")
        remove_background(raw_path, clean_path)
        cleaned_images[label] = clean_path

    # Log to CSV
    file_io.save_csv(
        {
            "submission_id": submission_id,
            "client": client,
            "unit_number": unit_number,
            "service_date": service_date,
            "equipment_description": equipment_description,
            "gps_location": gps_location,
            "dirt_level": dirt_level,
            "inspection_notes": inspection_notes,
            "technician_name": technician_name,
            "technician_signature": technician_signature,
            "supervisor_name": supervisor_name,
            "supervisor_signature": supervisor_signature,
            "email": technician_email,  # <-- ADDED HERE
            "status": "awaiting_approval"
        },
        "app/data/form_log.csv"
    )

    # Generate PDF
    form_data = {
        "client": client,
        "unit_number": unit_number,
        "service_date": service_date,
        "equipment_description": equipment_description,
        "gps_location": gps_location,
        "dirt_level": dirt_level,
        "inspection_notes": inspection_notes,
        "technician_name": technician_name,
        "technician_signature": technician_signature,
        "supervisor_name": supervisor_name,
        "supervisor_signature": supervisor_signature,
        "technician_email": technician_email  # <-- ADDED HERE
    }

    pdf_path = f"{save_dir}/form_report.pdf"
    template_path = "static/pdf_template.pdf"
    generate_pdf(form_data, cleaned_images, qr_path, pdf_path, background_template_path=template_path)

    # Schedule email
    schedule_email(pdf_path=pdf_path, recipient="marj@albertapowerwash.ca", delay_minutes=60)

    return templates.TemplateResponse("form.html", {
        "request": request,
        "message": "Form submitted successfully!"
    })