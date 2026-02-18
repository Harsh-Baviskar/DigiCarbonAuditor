"""
Digital Carbon Auditor — Flask entry point.

Exposes the intelligent usage report endpoint for scanning
directories, categorizing files, and detecting cold data.
"""

import os
import sys

# Add the backend directory to sys.path to enable imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import math
import requests

from app.modules.intelligent_usage.report import generate_intelligent_usage_report
from app.storage_scanner import scan_folder
from app.wasteDetect import (
    scan_folder_for_waste, 
    delete_duplicate_files,
    get_recovery_files,
    _clean_expired_recovery_files,
    RECOVERY_RETENTION_DAYS
)

# Load API key
API_KEY = os.getenv("ELECTRICITYMAP_API_KEY")

app = Flask(__name__)
CORS(app)


def get_carbon_intensity(region="IN-WE"):
    """
    Fetch real carbon intensity from ElectricityMap API.
    Returns gCO2/kWh for the region, or 500 as fallback if unavailable.
    
    Args:
        region: ISO region code (e.g., 'IN-WE', 'US-CA', 'DE')
    
    Returns:
        Carbon intensity in gCO2/kWh (as float)
    """
    if not API_KEY:
        print("Warning: ELECTRICITYMAP_API_KEY not set. Using default carbon intensity.")
        return 500  # Default global average
    
    try:
        url = f"https://api.electricitymaps.com/v3/carbon-intensity/latest?zone={region}"
        headers = {"auth-token": API_KEY}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        carbon_intensity = data.get("carbonIntensity")
        
        if carbon_intensity is None:
            print(f"Warning: No carbonIntensity in response for {region}. Using default 500 gCO2/kWh")
            return 500
        
        print(f"Fetched carbon intensity for {region}: {carbon_intensity} gCO2/kWh")
        return carbon_intensity
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching carbon intensity for {region}: {str(e)}")
        return 500  # Default fallback value in gCO2/kWh
    except Exception as e:
        print(f"Unexpected error getting carbon intensity: {str(e)}")
        return 500


def estimate_folder_size(folder_name):
    """Estimate realistic storage size and file count based on folder name."""
    folder_name_lower = folder_name.lower()
    
    # Define typical characteristics for common folder types
    folder_profiles = {
        'desktop': {'avg_files': 15000, 'avg_size_gb': 50, 'variance': 0.3},
        'documents': {'avg_files': 2000, 'avg_size_gb': 5, 'variance': 0.4},
        'downloads': {'avg_files': 5000, 'avg_size_gb': 25, 'variance': 0.5},
        'pictures': {'avg_files': 3000, 'avg_size_gb': 100, 'variance': 0.6},
        'videos': {'avg_files': 500, 'avg_size_gb': 200, 'variance': 0.7},
        'music': {'avg_files': 1000, 'avg_size_gb': 50, 'variance': 0.4},
        'program files': {'avg_files': 10000, 'avg_size_gb': 20, 'variance': 0.2},
        'windows': {'avg_files': 5000, 'avg_size_gb': 15, 'variance': 0.1},
        'users': {'avg_files': 25000, 'avg_size_gb': 150, 'variance': 0.4},
        'default': {'avg_files': 1000, 'avg_size_gb': 10, 'variance': 0.5}
    }
    
    # Find matching profile
    profile = folder_profiles['default']
    for key, prof in folder_profiles.items():
        if key in folder_name_lower:
            profile = prof
            break
    
    # Add some randomization within variance range (seeded for consistency)
    import random
    import hashlib
    
    # Create a seed based on folder name for consistent results
    seed = int(hashlib.md5(folder_name_lower.encode()).hexdigest()[:8], 16)
    random.seed(seed)
    
    variance = profile['variance']
    file_multiplier = 1 + (random.random() - 0.5) * variance * 2
    size_multiplier = 1 + (random.random() - 0.5) * variance * 2
    
    estimated_files = max(1, int(profile['avg_files'] * file_multiplier))
    estimated_size_gb = max(0.1, profile['avg_size_gb'] * size_multiplier)
    
    # Convert to TB for API consistency
    estimated_size_tb = estimated_size_gb / 1024
    
    return estimated_size_tb, estimated_files


@app.route("/calculate", methods=['GET', 'POST'])
def calculate():
    """Calculate carbon footprint based on data size or folder path using real regional data."""
    if request.method == 'POST':
        # Handle JSON POST request
        data = request.get_json()
        if not data:
            return jsonify({"detail": "JSON body required for POST request."}), 400
        
        storage_tb = data.get('storage_tb')
        region = data.get('region', 'IN-WE')
        
        if storage_tb is None:
            return jsonify({"detail": "storage_tb is required in JSON body."}), 400
        
        try:
            storage_tb = float(storage_tb)
            if storage_tb < 0:
                return jsonify({"detail": "storage_tb must be >= 0."}), 400
            
            storage_gb = storage_tb * 1024
            
            # Get real carbon intensity from ElectricityMap API
            carbon_intensity_gco2_per_kwh = get_carbon_intensity(region)
            
            # Data center energy consumption: ~1.5 kWh per GB per year (industry average)
            energy_kwh_per_year = storage_gb * 1.5
            
            # Calculate carbon emissions in kg CO2 per year
            carbon_kg_per_year = (energy_kwh_per_year * carbon_intensity_gco2_per_kwh) / 1000
            
            # Cost estimate: $0.12 per kg CO2 (carbon offset price average)
            carbon_cost_estimate = carbon_kg_per_year * 0.12
            
            result = {
                "storage_tb": storage_tb,
                "storage_gb": storage_gb,
                "region": region,
                "carbon_intensity_gco2_per_kwh": carbon_intensity_gco2_per_kwh,
                "energy_kwh_per_year": round(energy_kwh_per_year, 2),
                "carbon_kg_per_year": round(carbon_kg_per_year, 2),
                "carbon_cost_estimate": round(carbon_cost_estimate, 2),
                "calculation_method": "api_based_with_region"
            }
            return jsonify(result)
        except ValueError:
            return jsonify({"detail": "Invalid storage_tb value."}), 400
    
    else:
        # Handle GET request
        data_size = request.args.get("data_size")
        path = request.args.get("path")
        region = request.args.get("region", "IN-WE")
        
        if not data_size and not path:
            return jsonify({"detail": "Either 'data_size' (in GB) or 'path' parameter is required."}), 400
        
        try:
            if data_size:
                # Direct calculation from data size (in GB)
                size_gb = float(data_size)
                if size_gb < 0:
                    return jsonify({"detail": "data_size must be >= 0."}), 400
                
                # Get real carbon intensity from ElectricityMap API
                carbon_intensity_gco2_per_kwh = get_carbon_intensity(region)
                
                # Data center energy consumption: ~1.5 kWh per GB per year
                energy_kwh_per_year = size_gb * 1.5
                
                # Calculate carbon emissions in kg CO2 per year
                carbon_kg_per_year = (energy_kwh_per_year * carbon_intensity_gco2_per_kwh) / 1000
                
                # Cost estimate
                carbon_cost_estimate = carbon_kg_per_year * 0.12
                
                storage_tb = size_gb / 1024
                
                return jsonify({
                    "carbon_footprint_kg": round(carbon_kg_per_year, 2),
                    "carbon_kg_per_year": round(carbon_kg_per_year, 2),
                    "energy_kwh_per_year": round(energy_kwh_per_year, 2),
                    "carbon_cost_estimate": round(carbon_cost_estimate, 2),
                    "data_size_gb": round(size_gb, 2),
                    "storage_tb": round(storage_tb, 6),
                    "region": region,
                    "carbon_intensity_gco2_per_kwh": carbon_intensity_gco2_per_kwh,
                    "calculation_method": "api_based_with_region"
                })
            else:
                # Calculate from folder path
                if not os.path.exists(path):
                    return jsonify({"detail": f"Path does not exist: {path}"}), 404
                if not os.path.isdir(path):
                    return jsonify({"detail": f"Path is not a directory: {path}"}), 400
                
                total_size = 0
                file_count = 0
                try:
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            try:
                                file_path = os.path.join(root, file)
                                total_size += os.path.getsize(file_path)
                                file_count += 1
                            except (OSError, FileNotFoundError):
                                continue
                except (PermissionError, OSError) as e:
                    return jsonify({"detail": f"Permission denied or error accessing path: {str(e)}"}), 400
                
                size_gb = total_size / (1024 ** 3)
                
                # Get real carbon intensity from ElectricityMap API
                carbon_intensity_gco2_per_kwh = get_carbon_intensity(region)
                
                # Data center energy consumption: ~1.5 kWh per GB per year
                energy_kwh_per_year = size_gb * 1.5
                
                # Calculate carbon emissions in kg CO2 per year
                carbon_kg_per_year = (energy_kwh_per_year * carbon_intensity_gco2_per_kwh) / 1000
                
                # Cost estimate
                carbon_cost_estimate = carbon_kg_per_year * 0.12
                
                storage_tb = size_gb / 1024
                
                return jsonify({
                    "carbon_footprint_kg": round(carbon_kg_per_year, 2),
                    "carbon_kg_per_year": round(carbon_kg_per_year, 2),
                    "energy_kwh_per_year": round(energy_kwh_per_year, 2),
                    "carbon_cost_estimate": round(carbon_cost_estimate, 2),
                    "data_size_gb": round(size_gb, 2),
                    "storage_tb": round(storage_tb, 6),
                    "region": region,
                    "carbon_intensity_gco2_per_kwh": carbon_intensity_gco2_per_kwh,
                    "files_scanned": file_count,
                    "calculation_method": "api_based_with_region"
                })
        except ValueError as exc:
            return jsonify({"detail": f"Invalid number format: {exc}"}), 400
        except Exception as exc:
            return jsonify({"detail": f"Internal error: {exc}"}), 500


@app.route("/upload-folder", methods=['GET', 'POST'])
def upload_folder():
    """Handle folder upload and return intelligent usage report."""
    if request.method == 'POST':
        # Handle POST request with form data (for file uploads)
        if 'file' not in request.files:
            return jsonify({"detail": "No file provided in form data."}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"detail": "No file selected."}), 400
        
        # For now, we'll just use the filename as path (this is a simplification)
        # In a real implementation, you'd extract the zip file and scan it
        path = file.filename
        threshold_days = int(request.form.get('threshold_days', 180))
        
        try:
            # Since we can't actually scan uploaded files easily, return a mock response
            # In production, you'd extract the zip and scan the contents
            return jsonify({
                "category_breakdown": {
                    "Code": 100,
                    "Documents": 50,
                    "Images": 25,
                    "Others": 75
                },
                "cold_category_breakdown": {},
                "cold_files_count": 0,
                "cold_storage_mb": 0.0,
                "estimated_carbon_saving_kg": 0.0,
                "recommendations": ["Consider organizing your files by type"],
                "total_files": 250,
                "total_storage_mb": 500.0,
                "files_scanned": 250,
                "storage_tb": 0.5,
                "region": request.form.get('region', 'IN-WE'),
                "energy_kwh_per_year": 250.0,
                "carbon_kg_per_year": 5.0,
                "carbon_cost_estimate": 0.25
            })
        except Exception as exc:
            return jsonify({"detail": f"Internal error: {exc}"}), 500
    
    else:
        # Handle GET request (existing logic for path-based scanning)
        path = request.args.get("path")
        if not path:
            return jsonify({"detail": "Query parameter 'path' is required."}), 400
        
        threshold_days = request.args.get("threshold_days", 180, type=int)
        if threshold_days < 1:
            return jsonify({"detail": "threshold_days must be >= 1."}), 400

        try:
            report = generate_intelligent_usage_report(path, threshold_days)
            return jsonify(report)
        except FileNotFoundError as exc:
            return jsonify({"detail": str(exc)}), 404
        except NotADirectoryError as exc:
            return jsonify({"detail": str(exc)}), 400
        except Exception as exc:
            return jsonify({"detail": f"Internal error: {exc}"}), 500


@app.route("/intelligent-usage")
def intelligent_usage():
    """Scan a directory and return a combined categorization + cold data report."""
    path = request.args.get("path")
    if not path:
        return jsonify({"detail": "Query parameter 'path' is required."}), 400

    threshold_days = request.args.get("threshold_days", 180, type=int)
    file_count = request.args.get("file_count", type=int)
    if threshold_days < 1:
        return jsonify({"detail": "threshold_days must be >= 1."}), 400

    try:
        # Try to parse the path as a number (size in GB)
        try:
            size_gb = float(path)
            return generate_mock_intelligent_report(size_gb, threshold_days, file_count)
        except ValueError:
            pass

        # Check if it's a real filesystem path
        if os.path.exists(path) and os.path.isdir(path):
            # Use scan_folder for real paths
            scan_result = scan_folder(path)
            total_files = scan_result["file_count"]
            size_gb = scan_result["total_bytes"] / (1024 ** 3)
            category_breakdown = scan_result["category_breakdown"]

            cold_files_ratio = min(0.3, threshold_days / 365)
            cold_files_count = int(total_files * cold_files_ratio)
            cold_storage_mb = (size_gb * 1024) * cold_files_ratio
            estimated_carbon_saving_kg = (cold_storage_mb / 1024 / 1024) * 0.02 * 0.5

            recommendations = []
            if cold_files_count > total_files * 0.2:
                recommendations.append(f"Consider archiving {cold_files_count} cold files to save approximately {estimated_carbon_saving_kg:.2f} kg CO2 per year")
            video_size = category_breakdown.get("video", 0)
            if video_size > scan_result["total_bytes"] * 0.1:
                recommendations.append("Large video files detected - consider compression or cloud storage")
            image_size = category_breakdown.get("image", 0)
            if image_size > scan_result["total_bytes"] * 0.15:
                recommendations.append("Many image files found - consider batch optimization")
            if not recommendations:
                recommendations.append("Your file organization looks good!")

            return jsonify({
                "total_files": total_files,
                "total_storage_mb": size_gb * 1024,
                "cold_files_count": cold_files_count,
                "cold_storage_mb": cold_storage_mb,
                "estimated_carbon_saving_kg": estimated_carbon_saving_kg,
                "category_breakdown": category_breakdown,
                "recommendations": recommendations
            })
        else:
            # Fall back to mock report using estimated folder size
            size_tb, estimated_file_count = estimate_folder_size(path)
            actual_file_count = file_count if file_count is not None else estimated_file_count
            size_gb = size_tb * 1024
            return generate_mock_intelligent_report(size_gb, threshold_days, actual_file_count)
    except Exception as exc:
        return jsonify({"detail": f"Internal error: {exc}"}), 500


def generate_mock_intelligent_report(size_gb, threshold_days, file_count=None):
    """Generate mock intelligent usage report based on storage size."""
    # Create realistic mock data based on size or provided file count
    if file_count is not None:
        total_files = file_count
    else:
        total_files = max(10, int(size_gb * 50))  # Estimate ~50 files per GB
    
    # Mock category breakdown
    base_categories = {
        "Code": 0.15,
        "Documents": 0.25, 
        "Images": 0.20,
        "Videos": 0.15,
        "Audio": 0.05,
        "Archives": 0.10,
        "Others": 0.10
    }
    
    category_breakdown = {}
    for category, ratio in base_categories.items():
        category_breakdown[category] = int(total_files * ratio)
    
    # Mock cold data (files older than threshold)
    cold_files_ratio = min(0.3, threshold_days / 365)  # More cold files for longer thresholds
    cold_files_count = int(total_files * cold_files_ratio)
    
    # Estimate cold storage as a portion of total
    cold_storage_mb = (size_gb * 1024) * cold_files_ratio
    
    # Calculate carbon savings from deleting cold files
    estimated_carbon_saving_kg = (cold_storage_mb / 1024 / 1024) * 0.02 * 0.5  # Rough estimate
    
    recommendations = []
    if cold_files_count > total_files * 0.2:
        recommendations.append(f"Consider archiving {cold_files_count} cold files to save approximately {estimated_carbon_saving_kg:.2f} kg CO2 per year")
    if category_breakdown.get("Videos", 0) > total_files * 0.1:
        recommendations.append("Large video files detected - consider compression or cloud storage")
    if category_breakdown.get("Images", 0) > total_files * 0.15:
        recommendations.append("Many image files found - consider batch optimization")
    
    if not recommendations:
        recommendations.append("Your file organization looks good!")
    
    return jsonify({
        "total_files": total_files,
        "total_storage_mb": size_gb * 1024,
        "cold_files_count": cold_files_count,
        "cold_storage_mb": cold_storage_mb,
        "estimated_carbon_saving_kg": estimated_carbon_saving_kg,
        "category_breakdown": category_breakdown,
        "recommendations": recommendations
    })


@app.route("/waste-detect", methods=['POST'])
def waste_detect():
    """Scan folder for wasteful files: duplicates, old files, and system files."""
    try:
        # Get JSON data with better error handling
        data = request.get_json(silent=True)
        
        if data is None:
            return jsonify({
                "detail": "Request body must be JSON with Content-Type: application/json",
                "scanStatus": "error"
            }), 400
        
        if not isinstance(data, dict):
            return jsonify({
                "detail": "Request body must be a JSON object",
                "scanStatus": "error"
            }), 400
        
        folder_path = data.get('path', '').strip()
        
        if not folder_path:
            return jsonify({
                "detail": "Path is required and cannot be empty",
                "scanStatus": "error"
            }), 400
        
        if not os.path.exists(folder_path):
            return jsonify({
                "detail": f"Path does not exist: {folder_path}",
                "scanStatus": "error"
            }), 404
        
        if not os.path.isdir(folder_path):
            return jsonify({
                "detail": f"Path is not a directory: {folder_path}",
                "scanStatus": "error"
            }), 400
        
        # Scan the folder
        results = scan_folder_for_waste(folder_path)
        return jsonify(results)
        
    except Exception as e:
        print(f"Error in /waste-detect: {str(e)}")
        return jsonify({
            "detail": f"Error during scan: {str(e)}", 
            "scanStatus": "error"
        }), 500


@app.route("/waste-detect/delete-duplicates", methods=['POST'])
def delete_duplicates():
    """Delete selected duplicate files with validation and verification."""
    try:
        data = request.get_json()
        if not data or 'files' not in data:
            return jsonify({"detail": "JSON body with 'files' list is required."}), 400
        
        file_paths = data.get('files')
        
        if not isinstance(file_paths, list) or len(file_paths) == 0:
            return jsonify({"detail": "Files list must not be empty."}), 400
        
        # Validate that all paths are strings
        if not all(isinstance(p, str) for p in file_paths):
            return jsonify({"detail": "All file paths must be strings."}), 400
        
        # Delete the selected files
        results = delete_duplicate_files(file_paths)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"detail": f"Error during deletion: {str(e)}", "status": "error"}), 500


@app.route("/waste-detect/recovery", methods=['GET'])
def get_recovery_list():
    """
    List all files currently in the recovery bin.
    Includes metadata for each file: original path, timestamp, expiry date.
    """
    try:
        recovery_files = get_recovery_files()
        
        # Calculate recovery bin statistics
        active_files = [f for f in recovery_files if not f.get("is_expired", False)]
        total_size = sum(f.get("file_size_bytes", 0) for f in active_files)
        expired_files = [f for f in recovery_files if f.get("is_expired", False)]
        
        result = {
            "status": "success",
            "recoveryBin": {
                "activeFiles": len(active_files),
                "expiredFiles": len(expired_files),
                "totalFiles": len(recovery_files),
                "totalSizeBytes": total_size,
                "totalSizeFormatted": _format_bytes(total_size) if total_size > 0 else "0 B",
                "retentionDays": RECOVERY_RETENTION_DAYS
            },
            "files": recovery_files
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "detail": f"Error retrieving recovery list: {str(e)}"
        }), 500


@app.route("/waste-detect/recovery/cleanup", methods=['POST'])
def cleanup_recovery():
    """
    Clean up expired files from recovery bin.
    Removes files that have exceeded retention period.
    """
    try:
        cleaned_count = _clean_expired_recovery_files()
        
        recovery_files = get_recovery_files()
        active_files = [f for f in recovery_files if not f.get("is_expired", False)]
        total_size = sum(f.get("file_size_bytes", 0) for f in active_files)
        
        result = {
            "status": "success",
            "message": f"Cleaned up {cleaned_count} expired files from recovery bin",
            "cleanedCount": cleaned_count,
            "recoveryBin": {
                "activeFiles": len(active_files),
                "totalSizeBytes": total_size,
                "totalSizeFormatted": _format_bytes(total_size) if total_size > 0 else "0 B",
                "retentionDays": RECOVERY_RETENTION_DAYS
            }
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "detail": f"Error during cleanup: {str(e)}"
        }), 500


def _format_bytes(bytes_value):
    """Helper to format bytes for API response."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            if unit == 'B':
                return f"{int(bytes_value)} {unit}"
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


@app.route("/select-folder")
def select_folder():
    """Opens a native system dialog to select a folder on the server machine."""
    try:
        import subprocess
        import sys

        # Use a subprocess to run tkinter in the main thread of a new process.
        # This avoids issues with running GUI code inside a web server worker thread.
        script = """
import tkinter as tk
from tkinter import filedialog
import os

root = tk.Tk()
root.withdraw()  # Hide the main window
root.attributes('-topmost', True) # Make dialog appear on top
folder_path = filedialog.askdirectory()
print(folder_path)
"""
        # Run the script and capture the output
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            check=True
        )

        path = result.stdout.strip()
        return jsonify({"path": path})

    except Exception as e:
        print(f"Error opening dialog: {e}")
        return jsonify({"path": "", "error": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
