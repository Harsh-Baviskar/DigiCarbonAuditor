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

from app.modules.intelligent_usage.report import generate_intelligent_usage_report

app = Flask(__name__)
CORS(app)


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
    """Calculate carbon footprint based on data size or folder path."""
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
            # Check if storage_tb is a folder name (contains letters)
            if isinstance(storage_tb, str) and not storage_tb.replace('.', '').replace('-', '').isdigit():
                # It's a folder name, generate realistic estimates
                storage_tb, file_count = estimate_folder_size(storage_tb)
                result = {
                    "storage_tb": storage_tb,
                    "region": region,
                    "energy_kwh_per_year": storage_tb * 1024 * 0.02 * 0.5,
                    "carbon_kg_per_year": storage_tb * 1024 * 0.02,
                    "carbon_cost_estimate": storage_tb * 1024 * 0.02 * 0.05,
                    "calculation_method": "folder_estimation",
                    "estimated_files": file_count,
                    "folder_name": data.get('storage_tb')
                }
            else:
                # It's a numeric size
                storage_tb = float(storage_tb)
                if storage_tb < 0:
                    return jsonify({"detail": "storage_tb must be >= 0."}), 400
                
                # Calculate carbon footprint: 0.02 kg CO2 per GB per year
                carbon_kg_per_year = storage_tb * 1024 * 0.02  # Convert TB to GB first
                
                result = {
                    "storage_tb": storage_tb,
                    "region": region,
                    "energy_kwh_per_year": carbon_kg_per_year * 0.5,  # Rough estimate
                    "carbon_kg_per_year": carbon_kg_per_year,
                    "carbon_cost_estimate": carbon_kg_per_year * 0.05,  # Rough cost estimate
                    "calculation_method": "direct_input"
                }
            return jsonify(result)
        except ValueError:
            return jsonify({"detail": "Invalid storage_tb value."}), 400
    
    else:
        # Handle GET request (existing logic)
        data_size = request.args.get("data_size")
        path = request.args.get("path")
        
        if not data_size and not path:
            return jsonify({"detail": "Either 'data_size' (in GB) or 'path' parameter is required."}), 400
        
        try:
            if data_size:
                # Direct calculation from data size
                size_gb = float(data_size)
                if size_gb < 0:
                    return jsonify({"detail": "data_size must be >= 0."}), 400
                carbon_footprint = size_gb * 0.02  # 0.02 kg CO2 per GB per year
                return jsonify({
                    "carbon_footprint_kg": round(carbon_footprint, 2),
                    "data_size_gb": size_gb,
                    "calculation_method": "direct"
                })
            else:
                # Calculate from folder path
                if not os.path.exists(path):
                    return jsonify({"detail": f"Path does not exist: {path}"}), 404
                if not os.path.isdir(path):
                    return jsonify({"detail": f"Path is not a directory: {path}"}), 400
                
                total_size = 0
                for root, dirs, files in os.walk(path):
                    total_size += sum(os.path.getsize(os.path.join(root, file)) for file in files)
                
                size_gb = total_size / (1024 ** 3)  # Convert bytes to GB
                carbon_footprint = size_gb * 0.02  # 0.02 kg CO2 per GB per year
                return jsonify({
                    "carbon_footprint_kg": round(carbon_footprint, 2),
                    "data_size_gb": round(size_gb, 2),
                    "calculation_method": "folder_scan"
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
            # If it's a number, return mock intelligent usage data based on size
            return generate_mock_intelligent_report(size_gb, threshold_days, file_count)
        except ValueError:
            # Check if it's a folder name/path (contains typical folder characters or is a common folder name)
            # More lenient check: if it contains letters and looks like a path or folder name
            path_clean = path.replace('\\', '/').replace(':', '').lower()
            is_folder_like = (
                any(char.isalpha() for char in path) and  # Contains letters
                ('desktop' in path_clean or 'documents' in path_clean or 'downloads' in path_clean or
                 'pictures' in path_clean or 'videos' in path_clean or 'music' in path_clean)  # Only common user folders
            )
            
            if is_folder_like:
                # It's a folder name/path, generate realistic estimates
                size_tb, estimated_file_count = estimate_folder_size(path)
                # Use provided file_count if available, otherwise use estimate
                actual_file_count = file_count if file_count is not None else estimated_file_count
                size_gb = size_tb * 1024
                return generate_mock_intelligent_report(size_gb, threshold_days, actual_file_count)
            else:
                # If it's not a number or folder name, treat it as a file path
                if not os.path.exists(path):
                    return jsonify({"detail": f"Path does not exist: {path}"}), 404
                if not os.path.isdir(path):
                    return jsonify({"detail": f"Path is not a directory: {path}"}), 400
                
                report = generate_intelligent_usage_report(path, threshold_days)
                return jsonify(report)
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
