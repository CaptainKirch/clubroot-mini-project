from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path
from io import BytesIO
import os

def generate_pdf(data: dict, images: dict, qr_path: str, output_path: str, background_template_path: str):
    bg_pdf = PdfReader(background_template_path)
    writer = PdfWriter()

    overlay_streams = []

    for page_num in range(len(bg_pdf.pages)):
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        c.setFont("Helvetica", 10)

        # Page 1: Info + QR
        if page_num == 0:
            c.drawString(187, 650, data.get("service_date", ""))
            c.drawString(186, 624, data.get("unit_number", ""))
            c.drawString(185, 596, data.get("description", ""))
            c.drawString(185, 537, data.get("gps_location", ""))
            c.drawImage(qr_path, x=459, y=680, width=100, height=100, mask='auto')

        # Page 2: No overlay needed
        if page_num == 1:
            pass

        # Page 3: Before Photos
        if page_num == 2:
            if images.get("before_left"):
                c.drawImage(images["before_left"], x=125, y=629, width=180, height=120, preserveAspectRatio=True, mask='auto')
            if images.get("before_right"):
                c.drawImage(images["before_right"], x=381, y=614, width=180, height=120, preserveAspectRatio=True, mask='auto')
            if images.get("before_wheel"):
                c.drawImage(images["before_wheel"], x=101, y=312, width=180, height=120, preserveAspectRatio=True, mask='auto')
            if images.get("before_undercarriage"):
                c.drawImage(images["before_undercarriage"], x=371, y=313, width=180, height=120, preserveAspectRatio=True, mask='auto')

        # Page 4: After Photos
        if page_num == 3:
            if images.get("after_left"):
                c.drawImage(images["after_left"], x=86, y=608, width=180, height=120, preserveAspectRatio=True, mask='auto')
            if images.get("after_right"):
                c.drawImage(images["after_right"], x=358, y=590, width=180, height=120, preserveAspectRatio=True, mask='auto')
            if images.get("after_wheel"):
                c.drawImage(images["after_wheel"], x=67, y=286, width=180, height=120, preserveAspectRatio=True, mask='auto')
            if images.get("after_undercarriage"):
                c.drawImage(images["after_undercarriage"], x=348, y=306, width=180, height=120, preserveAspectRatio=True, mask='auto')

        # Page 5: Disinfection + Signature
        if page_num == 4:
            if images.get("disinfecting_wheel"):
                c.drawImage(images["disinfecting_wheel"], x=92, y=588, width=180, height=120, preserveAspectRatio=True, mask='auto')
            if images.get("disinfecting_undercarriage"):
                c.drawImage(images["disinfecting_undercarriage"], x=346, y=589, width=180, height=120, preserveAspectRatio=True, mask='auto')

            # Technician info
            c.drawString(182, 321, data.get("technician_name", ""))
            if data.get("technician_signature_path") and os.path.exists(data["technician_signature_path"]):
                c.drawImage(data["technician_signature_path"], x=448, y=302, width=90, height=35, mask='auto')

        c.save()
        packet.seek(0)
        overlay_streams.append(PdfReader(packet).pages[0])

    for i, page in enumerate(bg_pdf.pages):
        overlay = overlay_streams[i] if i < len(overlay_streams) else None
        if overlay:
            page.merge_page(overlay)
        writer.add_page(page)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)
