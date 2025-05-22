from fpdf import FPDF
from pathlib import Path

class ReportPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Technician Report", ln=True, align="C")
        self.ln(10)

    def add_label_value(self, label, value):
        self.set_font("Arial", "", 12)
        self.cell(40, 10, f"{label}:", ln=0)
        self.cell(0, 10, value, ln=1)

def generate_pdf(data: dict, images: dict, qr_path: str, output_path: str):
    pdf = ReportPDF()
    pdf.add_page()

    for key, val in data.items():
        pdf.add_label_value(key.replace("_", " ").title(), str(val))

    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "QR Code:", ln=True)
    pdf.image(qr_path, w=40)

    for label, path in images.items():
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, label.replace("_", " ").title(), ln=True)
        pdf.image(path, w=100)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    pdf.output(output_path)
