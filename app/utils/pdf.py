from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path
from io import BytesIO
import os
import textwrap

def generate_pdf(data: dict, images: dict, qr_path: str, output_path: str, background_template_path: str):
    bg_pdf = PdfReader(background_template_path)
    writer = PdfWriter()
    overlay_streams = []

    for page_num in range(len(bg_pdf.pages)):
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        c.setFont("Helvetica", 10)

        if page_num == 0:
            # Page 1 – Info
            c.drawString(182, 773, data.get("service_date", ""))
            c.drawString(183, 747, data.get("unit_number", ""))
            desc = data.get("description", "")
            text = c.beginText(184, 722)
            text.setFont("Helvetica", 9)
            wrapped_lines = textwrap.wrap(desc, width=90)
            for line in wrapped_lines:
                text.textLine(line)
            c.drawText(text)
            c.drawString(181, 660, data.get("gps_location", ""))

        elif page_num == 1:
            # Page 2 – Before Pictures
            if images.get("before_left"):
                c.drawImage(images["before_left"], x=100, y=529, width=180, height=120, preserveAspectRatio=True, mask='auto')
            if images.get("before_right"):
                c.drawImage(images["before_right"], x=357, y=520, width=180, height=120, preserveAspectRatio=True, mask='auto')
            if images.get("before_wheel"):
                c.drawImage(images["before_wheel"], x=66, y=218, width=180, height=120, preserveAspectRatio=True, mask='auto')
            if images.get("before_undercarriage"):
                c.drawImage(images["before_undercarriage"], x=338, y=228, width=180, height=120, preserveAspectRatio=True, mask='auto')

        elif page_num == 2:
            # Page 3 – After Pictures
            if images.get("after_left"):
                c.drawImage(images["after_left"], x=77, y=543, width=180, height=120, preserveAspectRatio=True, mask='auto')
            if images.get("after_right"):
                c.drawImage(images["after_right"], x=342, y=554, width=180, height=120, preserveAspectRatio=True, mask='auto')
            if images.get("after_wheel"):
                c.drawImage(images["after_wheel"], x=74, y=256, width=180, height=120, preserveAspectRatio=True, mask='auto')
            if images.get("after_undercarriage"):
                c.drawImage(images["after_undercarriage"], x=348, y=260, width=180, height=120, preserveAspectRatio=True, mask='auto')

        elif page_num == 3:
            # Page 4 – Disinfecting Pics + Technician Info
            if images.get("disinfecting_wheel"):
                c.drawImage(images["disinfecting_wheel"], x=71, y=549, width=180, height=120, preserveAspectRatio=True, mask='auto')
            if images.get("disinfecting_undercarriage"):
                c.drawImage(images["disinfecting_undercarriage"], x=349, y=553, width=180, height=120, preserveAspectRatio=True, mask='auto')

            c.drawString(177, 279, data.get("technician_name", ""))
            sig_path = data.get("technician_signature_path")
            if sig_path and os.path.exists(sig_path):
                c.drawImage(sig_path, x=446, y=282, width=90, height=35, mask='auto')
            c.drawImage(qr_path, x=33, y=25, width=100, height=100, mask='auto')
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
