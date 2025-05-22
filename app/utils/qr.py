import qrcode
from pathlib import Path

def generate_qr(data: str, output_path: str):
    img = qrcode.make(data)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
