"""
Wasteful File Detector
Identifies duplicate files via SHA256 hash, and detects unused/old files.
Provides statistics and options for deletion.
Uses robust error handling similar to storage_scanner.py
"""

import os
import hashlib
import time
from datetime import datetime, timedelta
from collections import defaultdict
import mimetypes

SYSTEM_FILE_EXTENSIONS = {
    '.dll', '.exe', '.sys', '.msi', '.app', '.so', '.o',
    '.lock', '.tmp', '.temp', '.cache', '.log', '.bak',
    '.db', '.sqlite', '.ini', '.cfg', '.conf', '.pdb',
    '.ilk', '.obj', '.lib', '.a', '.so', '.dylib'
}

SYSTEM_DIRECTORIES = {
    'windows', 'system32', 'system64', 'appdata', 'programfiles',
    'node_modules', '__pycache__', '.git', '.venv', 'venv',
    '.next', 'dist', 'build', '.env', 'node_modules', 'packages',
    'system volume information', 'recycler', 'backup', 'cache'
}


def is_safe_path(file_path, base_directory):
    """
    Validate that a file path is safe to process.
    
    Security checks:
    1. Reject symlinks (both files and directories) to prevent directory traversal
    2. Ensure the real path is within the base directory (prevents ../ escaping)
    3. Compare absolute real paths to eliminate path normalization bypasses
    
    Args:
        file_path: Path to validate
        base_directory: Base directory that scanning is restricted to (already real path)
    
    Returns:
        True if safe, False if unsafe
    """
    try:
        # Check if the file/directory is a symlink - reject all symlinks
        if os.path.islink(file_path):
            return False
        
        # Resolve to real path to detect any directory traversal attempts
        real_file_path = os.path.realpath(file_path)
        
        # Ensure the real path starts with base directory
        # Add os.sep to avoid prefix matching issues (e.g., /base vs /base2)
        if not real_file_path.startswith(os.path.realpath(base_directory) + os.sep):
            # Also check if it's exactly the base directory itself
            if real_file_path != os.path.realpath(base_directory):
                return False
        
        return True
    except (OSError, ValueError):
        # If path resolution fails, reject it
        return False


def is_system_file(file_path):
    """Check if file is a system file based on extension and path."""
    file_lower = file_path.lower()
    
    # Check file extension
    _, ext = os.path.splitext(file_lower)
    if ext in SYSTEM_FILE_EXTENSIONS:
        return True
    
    # Check if path contains system directories
    path_parts = file_lower.replace('\\', '/').split('/')
    for part in path_parts:
        if part in SYSTEM_DIRECTORIES:
            return True
    
    return False


def get_file_hash(file_path, chunk_size=65536):
    """Calculate SHA256 hash of a file with error handling."""
    try:
        # Skip very large files for performance (> 500MB)
        if os.path.getsize(file_path) > 500 * 1024 * 1024:
            return None
            
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except (IOError, OSError, PermissionError):
        return None
    except Exception:
        return None


def get_file_age_days(file_path):
    """Get the age of a file in days based on last modified time."""
    try:
        mod_time = os.path.getmtime(file_path)
        current_time = time.time()
        age_seconds = current_time - mod_time
        age_days = age_seconds / (24 * 3600)
        return age_days
    except (IOError, OSError):
        return 0


def scan_folder_for_waste(folder_path):
    """
    Scan a folder and identify wasteful files.
    Uses efficient two-pass approach:
    1. First pass: Group files by size and age
    2. Second pass: Hash only files in same-size groups (duplicates)
    
    SECURITY: Validates all paths to prevent directory traversal attacks
    """
    results = {
        "scanStatus": "success",
        "scannedPath": folder_path,
        "scanTimestamp": datetime.now().isoformat(),
        "summary": {
            "totalFiles": 0,
            "totalSizeBytes": 0,
            "duplicateFilesCount": 0,
            "duplicateSizeBytes": 0,
            "oldFilesCount": 0,
            "oldFilesSizeBytes": 0,
            "systemFilesCount": 0,
            "systemFilesSizeBytes": 0,
            "potentialWasteSizeBytes": 0,
            "errorCount": 0
        },
        "duplicateGroups": [],
        "oldFiles": [],
        "systemFiles": [],
        "statistics": {
            "wastePercentage": 0,
            "carbonSaveKgPerYear": 0
        }
    }
    
    if not os.path.exists(folder_path):
        results["scanStatus"] = "error"
        results["error"] = f"Path does not exist: {folder_path}"
        return results
    
    if not os.path.isdir(folder_path):
        results["scanStatus"] = "error"
        results["error"] = f"Path is not a directory: {folder_path}"
        return results
    
    try:
        # SECURITY: Resolve base directory to real path once at start
        # This prevents any directory traversal from affecting the base check
        base_real_path = os.path.realpath(folder_path)
        
        current_time = time.time()
        age_threshold_seconds = 180 * 24 * 3600  # 180 days
        
        # First pass: Collect file metadata
        files_by_size = defaultdict(list)
        old_files = []
        system_files = []
        
        for root, dirs, files in os.walk(base_real_path):
            # SECURITY: Filter out symlink directories to prevent traversal
            # This prevents os.walk from descending into symlinked directories
            dirs[:] = [d for d in dirs if (
                not d.startswith('.') and 
                d.lower() not in SYSTEM_DIRECTORIES and
                not os.path.islink(os.path.join(root, d))  # Reject symlinks
            )]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # SECURITY: Validate file path before processing
                # This catches any symlinks or path traversal attempts
                if not is_safe_path(file_path, base_real_path):
                    results["summary"]["errorCount"] += 1
                    continue
                
                # Error handling - continue on any file access issue
                try:
                    file_size = os.path.getsize(file_path)
                    results["summary"]["totalFiles"] += 1
                    results["summary"]["totalSizeBytes"] += file_size
                    
                    # Check if it's a system file
                    if is_system_file(file_path):
                        results["summary"]["systemFilesCount"] += 1
                        results["summary"]["systemFilesSizeBytes"] += file_size
                        system_files.append({
                            "path": file_path,
                            "size": file_size,
                            "sizeFormatted": format_bytes(file_size)
                        })
                        continue
                    
                    # Check file age
                    try:
                        mod_time = os.path.getmtime(file_path)
                        age_seconds = current_time - mod_time
                        age_days = age_seconds / (24 * 3600)
                        
                        if age_seconds > age_threshold_seconds:
                            results["summary"]["oldFilesCount"] += 1
                            results["summary"]["oldFilesSizeBytes"] += file_size
                            old_files.append({
                                "path": file_path,
                                "size": file_size,
                                "sizeFormatted": format_bytes(file_size),
                                "ageDays": round(age_days, 1),
                                "lastModified": datetime.fromtimestamp(mod_time).isoformat()
                            })
                            continue
                    except (IOError, OSError):
                        continue
                    
                    # Group files by size (for duplicate detection)
                    files_by_size[file_size].append({
                        "path": file_path,
                        "size": file_size,
                        "sizeFormatted": format_bytes(file_size)
                    })
                    
                except (IOError, OSError, PermissionError):
                    results["summary"]["errorCount"] += 1
                    continue
                except Exception:
                    results["summary"]["errorCount"] += 1
                    continue
        
        # Second pass: Hash only files in same-size groups (potential duplicates)
        file_hashes = defaultdict(list)
        
        for file_size, file_list in files_by_size.items():
            # Only hash if there are multiple files of same size
            if len(file_list) > 1:
                for file_info in file_list:
                    file_path = file_info["path"]
                    try:
                        # Skip large files (> 500MB) for performance
                        if file_size > 500 * 1024 * 1024:
                            continue
                            
                        file_hash = get_file_hash(file_path)
                        if file_hash:
                            file_hashes[file_hash].append(file_info)
                    except (IOError, OSError, PermissionError):
                        results["summary"]["errorCount"] += 1
                        continue
                    except Exception:
                        results["summary"]["errorCount"] += 1
                        continue
        
        # Extract duplicate groups
        for file_hash, files in file_hashes.items():
            if len(files) > 1:  # Only include if there are actual duplicates
                duplicate_size = files[0]["size"]
                results["summary"]["duplicateFilesCount"] += len(files) - 1
                results["summary"]["duplicateSizeBytes"] += duplicate_size * (len(files) - 1)
                
                results["duplicateGroups"].append({
                    "hash": file_hash,
                    "fileSizeBytes": duplicate_size,
                    "sizeFormatted": format_bytes(duplicate_size),
                    "duplicateCount": len(files),
                    "totalWasteBytes": duplicate_size * (len(files) - 1),
                    "totalWasteFormatted": format_bytes(duplicate_size * (len(files) - 1)),
                    "paths": [f["path"] for f in files]
                })
        
        # Calculate potential waste
        results["summary"]["potentialWasteSizeBytes"] = (
            results["summary"]["duplicateSizeBytes"] +
            results["summary"]["oldFilesSizeBytes"]
        )
        
        # Calculate waste percentage
        if results["summary"]["totalSizeBytes"] > 0:
            waste_pct = (results["summary"]["potentialWasteSizeBytes"] / 
                         results["summary"]["totalSizeBytes"]) * 100
            results["statistics"]["wastePercentage"] = round(waste_pct, 2)
        
        # Calculate carbon savings (0.02 kg CO2 per GB per year)
        waste_gb = results["summary"]["potentialWasteSizeBytes"] / (1024 ** 3)
        results["statistics"]["carbonSaveKgPerYear"] = round(waste_gb * 0.02, 4)
        
        # Sort results
        results["duplicateGroups"].sort(key=lambda x: x["totalWasteBytes"], reverse=True)
        old_files.sort(key=lambda x: x["size"], reverse=True)
        system_files.sort(key=lambda x: x["size"], reverse=True)
        
        # Limit to top 100 for performance
        results["oldFiles"] = old_files[:100]
        results["systemFiles"] = system_files[:100]
        
        return results
        
    except Exception as e:
        results["scanStatus"] = "error"
        results["error"] = f"Scan failed: {str(e)}"
        return results


def delete_duplicate_files(file_paths, keep_index=0):
    """
    Delete specific duplicate files from the provided list.
    Ensures files are actually deleted and verifies deletion.
    
    SECURITY: Validates all paths before deletion to prevent unauthorized access
    
    Args:
        file_paths: List of file paths to delete (specific duplicates to remove)
        keep_index: Deprecated parameter, kept for backward compatibility
    
    Returns:
        Dictionary with deletion results and statistics
    """
    results = {
        "status": "success",
        "deletedCount": 0,
        "failedCount": 0,
        "deletedSizeBytes": 0,
        "deletions": []
    }
    
    if not file_paths:
        results["status"] = "warning"
        results["message"] = "No files to delete"
        return results
    
    # Delete each file and verify deletion
    for file_path in file_paths:
        try:
            # Verify file exists before deletion
            if not os.path.exists(file_path):
                results["failedCount"] += 1
                results["deletions"].append({
                    "path": file_path,
                    "status": "not_found",
                    "error": "File does not exist"
                })
                continue
            
            # SECURITY: Validate path before deletion to prevent unauthorized removal
            if os.path.islink(file_path):
                results["failedCount"] += 1
                results["deletions"].append({
                    "path": file_path,
                    "status": "blocked",
                    "error": "Symlinks cannot be deleted (security policy)"
                })
                continue
            
            # Get file size before deletion
            try:
                file_size = os.path.getsize(file_path)
            except (IOError, OSError):
                file_size = 0
            
            # Attempt deletion with multiple strategies
            deletion_success = False
            
            # Strategy 1: Direct deletion
            try:
                os.remove(file_path)
                deletion_success = True
            except (IOError, OSError, PermissionError) as e:
                # Strategy 2: Try forcing deletion on Windows
                if os.name == 'nt':
                    try:
                        import stat
                        os.chmod(file_path, stat.S_IWRITE | stat.S_IREAD)
                        os.remove(file_path)
                        deletion_success = True
                    except (IOError, OSError, Exception):
                        deletion_success = False
            
            # Verify deletion was successful
            if deletion_success and not os.path.exists(file_path):
                results["deletedCount"] += 1
                results["deletedSizeBytes"] += file_size
                results["deletions"].append({
                    "path": file_path,
                    "status": "deleted",
                    "sizeBytes": file_size
                })
            else:
                results["failedCount"] += 1
                results["deletions"].append({
                    "path": file_path,
                    "status": "failed",
                    "error": "File still exists after deletion attempt"
                })
        
        except Exception as e:
            results["failedCount"] += 1
            results["deletions"].append({
                "path": file_path,
                "status": "failed",
                "error": str(e)
            })
    
    # Set final status
    if results["failedCount"] > 0:
        results["status"] = "partial_success" if results["deletedCount"] > 0 else "error"
    
    return results


def format_bytes(bytes_value):
    """Format bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            if unit == 'B':
                return f"{int(bytes_value)} {unit}"
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"
