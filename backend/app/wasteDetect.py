"""
Wasteful File Detector
Identifies duplicate files via SHA256 hash, and detects unused/old files.
Provides statistics and options for deletion via safe recovery mechanism.
Uses robust error handling similar to storage_scanner.py
"""

import os
import hashlib
import time
import json
import shutil
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

# RECOVERY CONFIGURATION
# Safe deletion mechanism: files moved to recovery directory instead of permanent deletion
RECOVERY_DIR = "backend/app/deleted_files_recovery"
RECOVERY_METADATA_DIR = os.path.join(RECOVERY_DIR, ".metadata")
RECOVERY_RETENTION_DAYS = 7  # Files automatically cleaned after 7 days


def _ensure_recovery_dirs():
    """Ensure recovery directories exist."""
    try:
        os.makedirs(RECOVERY_DIR, exist_ok=True)
        os.makedirs(RECOVERY_METADATA_DIR, exist_ok=True)
    except (IOError, OSError):
        pass  # Best effort - directory might already exist or be inaccessible


def _create_recovery_metadata(original_path, recovery_path):
    """
    Create metadata file for recovered file.
    
    Args:
        original_path: Original file location
        recovery_path: Path in recovery directory
    
    Returns:
        Path to metadata JSON file
    """
    try:
        _ensure_recovery_dirs()
        
        now = datetime.now()
        expiry = now + timedelta(days=RECOVERY_RETENTION_DAYS)
        
        metadata = {
            "original_path": original_path,
            "recovery_path": recovery_path,
            "recovered_at": now.isoformat(),
            "expires_at": expiry.isoformat(),
            "file_size_bytes": os.path.getsize(recovery_path) if os.path.exists(recovery_path) else 0
        }
        
        # Create metadata filename from recovery path
        basename = os.path.basename(recovery_path)
        metadata_path = os.path.join(RECOVERY_METADATA_DIR, f"{basename}.json")
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata_path
    except (IOError, OSError, json.JSONDecodeError) as e:
        # Log but don't raise - recovery still happened
        return None


def _clean_expired_recovery_files():
    """
    Remove files from recovery bin that have expired.
    Called automatically during deletion operations.
    """
    if not os.path.exists(RECOVERY_METADATA_DIR):
        return 0
    
    cleaned_count = 0
    now = datetime.now()
    
    try:
        for metadata_file in os.listdir(RECOVERY_METADATA_DIR):
            if not metadata_file.endswith('.json'):
                continue
            
            metadata_path = os.path.join(RECOVERY_METADATA_DIR, metadata_file)
            
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                expiry = datetime.fromisoformat(metadata.get("expires_at", now.isoformat()))
                
                # If expired, remove both recovery file and metadata
                if now > expiry:
                    recovery_path = metadata.get("recovery_path")
                    
                    # Remove recovery file
                    if recovery_path and os.path.exists(recovery_path):
                        try:
                            os.remove(recovery_path)
                        except (IOError, OSError):
                            pass
                    
                    # Remove metadata file
                    try:
                        os.remove(metadata_path)
                    except (IOError, OSError):
                        pass
                    
                    cleaned_count += 1
            except (IOError, OSError, json.JSONDecodeError, ValueError):
                # Skip problematic metadata files
                continue
    except (IOError, OSError):
        pass  # Directory might be inaccessible
    
    return cleaned_count


def get_recovery_files():
    """
    List all files currently in recovery.
    
    Returns:
        List of recovery file metadata dictionaries
    """
    recovery_files = []
    
    if not os.path.exists(RECOVERY_METADATA_DIR):
        return recovery_files
    
    try:
        for metadata_file in sorted(os.listdir(RECOVERY_METADATA_DIR)):
            if not metadata_file.endswith('.json'):
                continue
            
            metadata_path = os.path.join(RECOVERY_METADATA_DIR, metadata_file)
            
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                # Add indicator if file is expired
                now = datetime.now()
                expiry = datetime.fromisoformat(metadata.get("expires_at", now.isoformat()))
                metadata["is_expired"] = now > expiry
                
                recovery_files.append(metadata)
            except (IOError, OSError, json.JSONDecodeError):
                continue
    except (IOError, OSError):
        pass
    
    return recovery_files


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
    Move duplicate files to recovery folder instead of permanent deletion.
    
    SAFETY: Files are preserved in recovery bin with metadata for 7 days.
    This prevents accidental permanent loss of user data.
    
    SECURITY: Validates all paths before deletion to prevent unauthorized access
    
    AUDITABILITY: Each recovery is logged with original path, timestamp, and expiry date
    
    Args:
        file_paths: List of file paths to move to recovery
        keep_index: Deprecated parameter, kept for backward compatibility
    
    Returns:
        Dictionary with recovery results and statistics
    """
    results = {
        "status": "success",
        "recoveredCount": 0,
        "failedCount": 0,
        "recoveredSizeBytes": 0,
        "recoveredFiles": [],
        "message": f"Files moved to recovery bin (expires in {RECOVERY_RETENTION_DAYS} days)"
    }
    
    if not file_paths:
        results["status"] = "warning"
        results["message"] = "No files to recover"
        return results
    
    # Ensure recovery directories exist
    _ensure_recovery_dirs()
    
    # Clean expired files before processing new ones
    _clean_expired_recovery_files()
    
    # Move each file to recovery and track with metadata
    for file_path in file_paths:
        try:
            # Verify file exists before recovery
            if not os.path.exists(file_path):
                results["failedCount"] += 1
                results["recoveredFiles"].append({
                    "path": file_path,
                    "status": "not_found",
                    "error": "File does not exist"
                })
                continue
            
            # SECURITY: Validate path before recovery to prevent unauthorized access
            if os.path.islink(file_path):
                results["failedCount"] += 1
                results["recoveredFiles"].append({
                    "path": file_path,
                    "status": "blocked",
                    "error": "Symlinks cannot be recovered (security policy)"
                })
                continue
            
            # Get file size before recovery
            try:
                file_size = os.path.getsize(file_path)
            except (IOError, OSError):
                file_size = 0
            
            # Create unique recovery filename to avoid collisions
            # Format: TIMESTAMP_ORIGINAL_FILENAME
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            original_filename = os.path.basename(file_path)
            recovery_filename = f"{timestamp}_{original_filename}"
            recovery_path = os.path.join(RECOVERY_DIR, recovery_filename)
            
            # Ensure we don't overwrite existing recovery files
            counter = 0
            while os.path.exists(recovery_path) and counter < 100:
                counter += 1
                recovery_filename = f"{timestamp}_{counter}_{original_filename}"
                recovery_path = os.path.join(RECOVERY_DIR, recovery_filename)
            
            # Move file to recovery
            try:
                shutil.move(file_path, recovery_path)
                recovery_success = True
            except (IOError, OSError, shutil.Error):
                recovery_success = False
            
            # Verify recovery was successful
            if recovery_success and os.path.exists(recovery_path) and not os.path.exists(file_path):
                # Create metadata file for auditability
                metadata_path = _create_recovery_metadata(file_path, recovery_path)
                
                results["recoveredCount"] += 1
                results["recoveredSizeBytes"] += file_size
                results["recoveredFiles"].append({
                    "path": file_path,
                    "status": "recovered",
                    "recoveredAs": recovery_filename,
                    "sizeBytes": file_size,
                    "sizeFormatted": format_bytes(file_size),
                    "expiresAt": (datetime.now() + timedelta(days=RECOVERY_RETENTION_DAYS)).isoformat(),
                    "metadataFile": os.path.basename(metadata_path) if metadata_path else None
                })
            else:
                results["failedCount"] += 1
                results["recoveredFiles"].append({
                    "path": file_path,
                    "status": "failed",
                    "error": "File could not be moved to recovery"
                })
        
        except Exception as e:
            results["failedCount"] += 1
            results["recoveredFiles"].append({
                "path": file_path,
                "status": "failed",
                "error": str(e)
            })
    
    # Set final status
    if results["failedCount"] > 0:
        results["status"] = "partial_success" if results["recoveredCount"] > 0 else "error"
    
    # Add recovery bin summary
    all_recovery_files = get_recovery_files()
    total_recovery_size = sum(f.get("file_size_bytes", 0) for f in all_recovery_files)
    active_files = [f for f in all_recovery_files if not f.get("is_expired", False)]
    
    results["recoveryBin"] = {
        "totalFiles": len(active_files),
        "totalSizeBytes": total_recovery_size,
        "totalSizeFormatted": format_bytes(total_recovery_size),
        "retentionDays": RECOVERY_RETENTION_DAYS
    }
    
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
