from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path
from io import BytesIO

def generate_pdf(data: dict, images: dict, qr_path: str, output_path: str, background_template_path: str):
    bg_pdf = PdfReader(background_template_path)
    writer = PdfWriter()

    overlay_streams = []

    for page_num in range(len(bg_pdf.pages)):
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        c.setFont("Helvetica", 11)

        if page_num == 0:
            c.setFont("Helvetica", 10)
            c.drawString(183, 660, data.get("service_date", ""))
            c.drawString(184, 634, data.get("unit_number", ""))
            c.drawString(183, 608, data.get("description", ""))
            c.drawString(184, 582, data.get("gps_location", ""))
            c.drawImage(qr_path, x=469, y=680, width=100, height=100, mask='auto')

        if page_num == 1:
            if images.get("before_left"):
                c.drawImage(images["before_left"], x=154, y=568, width=120, height=80, mask='auto')
            if images.get("before_right"):
                c.drawImage(images["before_right"], x=421, y=558, width=120, height=80, mask='auto')
            if images.get("before_wheel"):
                c.drawImage(images["before_wheel"], x=161, y=257, width=120, height=80, mask='auto')
            if images.get("before_undercarriage"):
                c.drawImage(images["before_undercarriage"], x=430, y=252, width=120, height=80, mask='auto')

        if page_num == 2:
            if images.get("after_left"):
                c.drawImage(images["after_left"], x=155, y=551, width=120, height=80, mask='auto')
            if images.get("after_right"):
                c.drawImage(images["after_right"], x=428, y=550, width=120, height=80, mask='auto')
            if images.get("after_wheel"):
                c.drawImage(images["after_wheel"], x=161, y=256, width=120, height=80, mask='auto')
            if images.get("after_undercarriage"):
                c.drawImage(images["after_undercarriage"], x=427, y=275, width=120, height=80, mask='auto')

        if page_num == 3:
            if images.get("disinfecting_wheel"):
                c.drawImage(images["disinfecting_wheel"], x=160, y=559, width=120, height=80, mask='auto')
            if images.get("disinfecting_undercarriage"):
                c.drawImage(images["disinfecting_undercarriage"], x=422, y=552, width=120, height=80, mask='auto')

            # Technician name and signature
            c.setFont("Helvetica", 10)
            c.drawString(228, 208, data.get("technician_name", ""))
            if data.get("technician_signature_path"):
                c.drawImage(data["technician_signature_path"], x=505, y=210, width=100, height=40, mask='auto')

            # Supervisor name and (placeholder) signature
            c.drawString(225, 91, data.get("supervisor_name", ""))
            if data.get("technician_signature_path"):
                c.drawImage(data["technician_signature_path"], x=505, y=93, width=100, height=40, mask='auto')

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
