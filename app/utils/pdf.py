from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path

def generate_pdf(data: dict, images: dict, qr_path: str, output_path: str, background_template_path: str):
    overlay_path = output_path.replace(".pdf", "_overlay.pdf")

    # Step 1: Create overlay PDF with data
    c = canvas.Canvas(overlay_path, pagesize=letter)

    # Draw text
    c.setFont("Helvetica", 12)
    c.drawString(50, 700, f"Client: {data['client']}")
    c.drawString(50, 680, f"Unit #: {data['unit_number']}")
    c.drawString(50, 660, f"Date: {data['service_date']}")
    c.drawString(50, 640, f"Tech: {data['technician_name']}")
    c.drawString(50, 620, f"Supervisor: {data['supervisor_name']}")
    c.drawString(50, 600, f"Dirt Level: {data['dirt_level']}")
    
    # Draw QR Code
    c.drawImage(qr_path, x=450, y=620, width=100, height=100)

    c.save()

    # Step 2: Merge overlay with template
    bg_pdf = PdfReader(background_template_path)
    overlay_pdf = PdfReader(overlay_path)
    writer = PdfWriter()

    bg_page = bg_pdf.pages[0]
    bg_page.merge_page(overlay_pdf.pages[0])
    writer.add_page(bg_page)

    # Write final output
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)

    # Optionally: delete the overlay
    Path(overlay_path).unlink(missing_ok=True)
