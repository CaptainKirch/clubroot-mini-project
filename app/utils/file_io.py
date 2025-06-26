import shutil
import csv
from typing import Dict
from fastapi import UploadFile
import requests
import os

from pillow_heif import register_heif_opener
from PIL import Image

# Enable HEIC support
register_heif_opener()

async def save_file(upload: UploadFile, folder: str, filename: str):
    path = f"{folder}/{filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)

CSV_COLUMNS = [
    "submission_id", "client", "unit_number", "service_date", "description",
    "gps_location", "dirt_level", "inspection_notes", "technician_name",
    "technician_signature", "supervisor_name", "supervisor_signature",
    "email", "status", "pdf_path"
]

def save_csv(data: Dict, csv_path: str):
    write_header = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0
    with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, quoting=csv.QUOTE_ALL)
        if write_header:
            print("[INFO] Writing header to CSV")
            writer.writeheader()
        print("[INFO] Writing row:", data)
        writer.writerow(data)

def convert_heic_to_jpg(input_path: str, output_path: str):
    img = Image.open(input_path)
    img = img.convert("RGB")  # force RGB mode
    img.save(output_path, format="JPEG")
    print(f"[✅] Converted HEIC to real JPG: {output_path}")


def remove_background(image_path: str, output_path: str):
    from PIL import UnidentifiedImageError

    api_key = os.getenv("SLAZZER_API_KEY")
    if not api_key:
        raise EnvironmentError("SLAZZER_API_KEY not set in .env")

    try:
        img = Image.open(image_path)
        detected_format = img.format.lower()
        print(f"[DEBUG] Detected image format: {detected_format}")

        if detected_format == "heif" or image_path. lower().endswith(".heic"):
            converted_path = image_path.rsplit(".", 1)[0] + ".jpg"
            convert_heic_to_jpg(image_path, converted_path)
            image_path = converted_path
        else:
            print(f"[✅] Using image as-is: {image_path}")

    except UnidentifiedImageError as e:
        print(f"[❌] Could not identify image format: {e}")
        raise Exception("Image format identification failed.")
    except Exception as e:
        print(f"[❌] General error while opening image: {e}")
        raise Exception("Image opening/conversion failed.")

    with open(image_path, "rb") as image_file:
        response = requests.post(
            "https://api.slazzer.com/v2.0/remove_image_background",
            headers={"API-KEY": api_key},
            files={"source_image_file": image_file},
            data={"format": "jpg"}  # force Slazzer to return JPG
        )

    print(f"[DEBUG] Slazzer API response {response.status_code}: {response.text}")

    if response.status_code == 200:
        with open(output_path, "wb") as out_file:
            out_file.write(response.content)
        print(f"[✅] Background removed: {output_path}")
    else:
        raise Exception(f"Background removal failed: {response.status_code} - {response.text}")
