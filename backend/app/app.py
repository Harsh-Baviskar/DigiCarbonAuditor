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

from app.modules.intelligent_usage.report import generate_intelligent_usage_report

app = Flask(__name__)
CORS(app)


@app.route("/intelligent-usage")
def intelligent_usage():
    """Scan a directory and return a combined categorization + cold data report."""
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
    app.run(host="0.0.0.0", port=8001, debug=True)
