import shutil
import csv
from typing import Dict
from fastapi import UploadFile

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
