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

def save_csv(data: Dict, csv_path: str):
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def convert_heic_to_jpg(input_path: str, output_path: str):
    img = Image.open(input_path)
    img.save(output_path, format="JPEG")
    print(f"[✅] Converted HEIC to JPG: {output_path}")

def remove_background(image_path: str, output_path: str):
    api_key = os.getenv("SLAZZER_API_KEY")
    if not api_key:
        raise EnvironmentError("SLAZZER_API_KEY not set in .env")

    # Check if file is HEIC → convert to JPG first
    if image_path.lower().endswith(".heic"):
        converted_path = image_path.replace(".heic", ".jpg")
        convert_heic_to_jpg(image_path, converted_path)
        image_path = converted_path

    with open(image_path, "rb") as image_file:
        response = requests.post(
            "https://api.slazzer.com/v2.0/remove_image_background",
            headers={"API-KEY": api_key},
            files={"source_image_file": image_file}
        )

    if response.status_code == 200:
        with open(output_path, "wb") as out_file:
            out_file.write(response.content)
        print(f"[✅] Background removed: {output_path}")
    else:
        print(f"[❌] Slazzer API failed ({response.status_code}): {response.text}")
        raise Exception("Background removal failed.")

    