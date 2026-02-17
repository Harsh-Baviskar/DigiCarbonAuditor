from fastapi import UploadFile, File
import zipfile
import os
import shutil
from app.storage_scanner import scan_folder
from app.energy import calculate_energy
from app.carbon_api import get_carbon_intensity
from app.calculator import calculate_emissions
from app.database import insert_record

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-folder")
async def upload_folder(file: UploadFile = File(...), region: str = "IN-WE"):

    zip_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extract_path = os.path.join(UPLOAD_DIR, file.filename + "_extracted")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    scan_result = scan_folder(extract_path)

    energy = calculate_energy(scan_result["storage_tb"])
    carbon_intensity = await get_carbon_intensity(region)
    carbon_kg, carbon_cost = calculate_emissions(energy, carbon_intensity)

    insert_record(scan_result["storage_tb"], energy, carbon_kg, carbon_cost, region)

    return {
        "files_scanned": scan_result["file_count"],
        "storage_tb": scan_result["storage_tb"],
        "category_breakdown": scan_result["category_breakdown"],
        "energy_kwh_per_year": energy,
        "carbon_kg_per_year": carbon_kg,
        "carbon_cost_estimate": carbon_cost
    }
