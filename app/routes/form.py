from fastapi import APIRouter, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from uuid import uuid4
import os
import datetime
import base64

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

@router.get("/success", response_class=HTMLResponse)
async def success_page(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})

@router.post("/submit")
async def handle_form(
    request: Request,
    client: str = Form(...),
    unit_number: str = Form(...),
    service_date: str = Form(...),
    gps_location: str = Form(...),
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
    technician_signature: str = Form(...),  # base64 string
    technician_email: str = Form(...),
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
        if not os.path.exists(clean_path):
            print(f"[ERROR] Missing cleaned image: {clean_path}")
        else:
            print(f"[OK] Cleaned image created: {clean_path}")
            cleaned_images[label] = clean_path

    # Decode and save technician signature
    signature_data = technician_signature.split(",")[1]  # remove 'data:image/png;base64,'
    signature_bytes = base64.b64decode(signature_data)
    signature_path = f"{save_dir}/technician_signature.png"
    with open(signature_path, "wb") as f:
        f.write(signature_bytes)

    pdf_path = f"{save_dir}/form_report.pdf"

    file_io.save_csv(
    {
        "submission_id": submission_id,
        "client": client,
        "unit_number": unit_number,
        "service_date": service_date, 
        "gps_location": gps_location,
        "inspection_notes": inspection_notes,
        "technician_name": technician_name,
        "technician_signature": signature_path,
        "email": technician_email,
        "status": "awaiting_approval",
        "pdf_path": f"/submissions/{submission_id}/form_report.pdf"
  # ✅ This is the key line you're missing
    },
    "app/data/form_log.csv"
)


    # Generate PDF
    form_data = {
        "client": client,
        "unit_number": unit_number,
        "service_date": service_date,
        "gps_location": gps_location,
        "inspection_notes": inspection_notes,
        "technician_name": technician_name,
        "technician_signature_path": signature_path,  # pass to PDF generator
        "technician_email": technician_email
    }

    pdf_path = f"{save_dir}/form_report.pdf"
    template_path = "static/CLUBROOT PDF TEMPLATE.pdf"
    # Remap image keys to match what PDF expects
    pdf_images = {
        "before_left": cleaned_images["before_left"],
        "before_right": cleaned_images["before_right"],
        "before_wheel": cleaned_images["before_wheel"],
        "before_undercarriage": cleaned_images["before_underside"],

        "after_left": cleaned_images["after_left"],
        "after_right": cleaned_images["after_right"],
        "after_wheel": cleaned_images["after_wheel"],
        "after_undercarriage": cleaned_images["after_underside"],

        "disinfecting_wheel": cleaned_images["disinfect_wheel_1"],
        "disinfecting_undercarriage": cleaned_images["disinfect_wheel_2"]
}

    try:
        generate_pdf(form_data, pdf_images, qr_path, pdf_path, background_template_path=template_path)
    except Exception as e:
        print("[PDF GENERATION ERROR]", e)
        raise



    # # Schedule email
    # schedule_email(pdf_path=pdf_path, recipient="marj@albertapowerwash.ca", delay_minutes=60)

    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/success", status_code=303)

