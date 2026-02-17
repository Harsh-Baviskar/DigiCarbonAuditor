
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import zipfile
import shutil
import requests

from database import init_db, insert_record
from storage_scanner import scan_folder
from energy import calculate_energy
from calculator import calculate_emissions

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

init_db()

ELECTRICITYMAP_API_KEY = os.getenv("ELECTRICITYMAP_API_KEY")


# New endpoint: Carbon Intensity Forecast
@app.route("/carbon-forecast", methods=["GET"])
def carbon_forecast():
    """
    Returns the carbon intensity forecast for a given region (zone).
    Query param: zone (default: IN)
    """
    zone = request.args.get("zone", "IN")
    url = f"https://api.electricitymaps.com/v3/carbon-intensity/forecast?zone={zone}"
    headers = {"auth-token": ELECTRICITYMAP_API_KEY}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_carbon_intensity(region="IN-WE"):
    """Fetch carbon intensity from ElectricityMaps API.
    Returns gCO2/kWh for the region, or 500 as default if unavailable.
    """
    url = f"https://api.electricitymaps.com/v3/carbon-intensity/latest?zone={region}"
    headers = {"auth-token": ELECTRICITYMAP_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        carbon_intensity = data.get("carbonIntensity")
        
        if carbon_intensity is None:
            print(f"Warning: No carbonIntensity in response for {region}. Using default 500 gCO2/kWh")
            return 500
        
        return carbon_intensity
    except Exception as e:
        print(f"Error fetching carbon intensity for {region}: {str(e)}")
        return 500  # Default fallback value in gCO2/kWh


@app.route("/upload-folder", methods=["POST"])
def upload_folder():
    file = request.files["file"]
    region = request.form.get("region", "IN-WE")

    zip_path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(zip_path)

    extract_path = os.path.join(UPLOAD_DIR, file.filename + "_extracted")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    scan_result = scan_folder(extract_path)

    energy = calculate_energy(scan_result["storage_tb"])
    carbon_intensity = get_carbon_intensity(region)
    carbon_kg, carbon_cost = calculate_emissions(energy, carbon_intensity)

    insert_record(scan_result["storage_tb"], energy, carbon_kg, carbon_cost, region)

    # Cleanup
    shutil.rmtree(extract_path)
    os.remove(zip_path)

    return jsonify({
        "files_scanned": scan_result["file_count"],
        "storage_tb": scan_result["storage_tb"],
        "category_breakdown": scan_result["category_breakdown"],
        "energy_kwh_per_year": energy,
        "carbon_kg_per_year": carbon_kg,
        "carbon_cost_estimate": carbon_cost
    })


@app.route("/calculate", methods=["POST"])
def calculate_direct():
    data = request.json
    storage_tb = data["storage_tb"]
    region = data.get("region", "IN-WE")

    energy = calculate_energy(storage_tb)
    carbon_intensity = get_carbon_intensity(region)
    carbon_kg, carbon_cost = calculate_emissions(energy, carbon_intensity)

    insert_record(storage_tb, energy, carbon_kg, carbon_cost, region)

    return jsonify({
        "storage_tb": storage_tb,
        "energy_kwh_per_year": energy,
        "carbon_kg_per_year": carbon_kg,
        "carbon_cost_estimate": carbon_cost
    })


if __name__ == "__main__":
    app.run(debug=True)
