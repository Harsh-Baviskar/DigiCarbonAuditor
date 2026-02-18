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

try:
    # Try relative import (when used as part of app package)
    from .core.config import Config
except ImportError:
    # Fall back to absolute import (when used directly or in tests)
    try:
        from app.core.config import Config
    except ImportError:
        # Last resort: define minimal config for backward compatibility
        class Config:
            class FileSystem:
                HASH_CHUNK_SIZE = 65536
                LARGE_FILE_THRESHOLD = 500 * 1024 * 1024
                OLD_FILE_AGE_DAYS = 180
                SECONDS_PER_DAY = 24 * 3600
                OLD_FILE_AGE_SECONDS = OLD_FILE_AGE_DAYS * SECONDS_PER_DAY
                PROGRESS_UPDATE_FREQUENCY = 10
                MAX_RECOVERY_NAME_ATTEMPTS = 100
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
            
            class Recovery:
                RETENTION_DAYS = 7
                RECOVERY_DIR = "backend/app/deleted_files_recovery"
                RECOVERY_METADATA_DIR = os.path.join(RECOVERY_DIR, ".metadata")
            
            class Storage:
                BYTES_PER_KB = 1024
                BYTES_PER_MB = 1024 * 1024
                BYTES_PER_GB = 1024 * 1024 * 1024
                BYTES_PER_TB = 1024 * 1024 * 1024 * 1024
            
            class Carbon:
                CARBON_PER_GB_PER_YEAR = 0.2
            
            class Performance:
                MAX_RESULTS_PER_CATEGORY = 100

# Import constants from Config for backward compatibility and usage
SYSTEM_FILE_EXTENSIONS = Config.FileSystem.SYSTEM_FILE_EXTENSIONS
SYSTEM_DIRECTORIES = Config.FileSystem.SYSTEM_DIRECTORIES
RECOVERY_DIR = Config.Recovery.RECOVERY_DIR
RECOVERY_METADATA_DIR = Config.Recovery.RECOVERY_METADATA_DIR
RECOVERY_RETENTION_DAYS = Config.Recovery.RETENTION_DAYS


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


def get_file_hash(file_path, chunk_size=None):
    """Calculate SHA256 hash of a file with error handling."""
    if chunk_size is None:
        chunk_size = Config.FileSystem.HASH_CHUNK_SIZE
        
    try:
        # Skip very large files for performance
        if os.path.getsize(file_path) > Config.FileSystem.LARGE_FILE_THRESHOLD:
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
        age_days = age_seconds / Config.FileSystem.SECONDS_PER_DAY
        return age_days
    except (IOError, OSError):
        return 0


def _count_files_quickly(folder_path, base_real_path):
    """
    Quick file count for progress tracking (no hashing).
    Counts total files to be processed in main scan.
    
    Args:
        folder_path: Path to scan
        base_real_path: Real path of base directory
    
    Returns:
        Total file count
    """
    total_files = 0
    try:
        for root, dirs, files in os.walk(base_real_path):
            # Filter system directories like in main scan
            dirs[:] = [d for d in dirs if (
                not d.startswith('.') and 
                d.lower() not in SYSTEM_DIRECTORIES and
                not os.path.islink(os.path.join(root, d))
            )]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Count only safe files
                if is_safe_path(file_path, base_real_path):
                    try:
                        if os.path.exists(file_path):
                            total_files += 1
                    except (IOError, OSError):
                        pass
    except (IOError, OSError):
        pass
    
    return max(1, total_files)  # Ensure at least 1 to avoid division by zero


def scan_folder_for_waste(folder_path, progress_callback=None):
    """
    Scan a folder and identify wasteful files.
    Uses efficient two-pass approach:
    1. First pass: Group files by size and age
    2. Second pass: Hash only files in same-size groups (duplicates)
    
    SECURITY: Validates all paths to prevent directory traversal attacks
    
    Args:
        folder_path: Directory to scan
        progress_callback: Optional callback function(processed, total, percentage) for progress tracking
    
    Returns:
        Results dictionary with findings and progress metadata
    """
    results = {
        "scanStatus": "success",
        "scannedPath": folder_path,
        "scanTimestamp": datetime.now().isoformat(),
        "progress": {
            "total": 0,
            "processed": 0,
            "percentage": 0,
            "stage": "initializing"
        },
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
        results["progress"]["stage"] = "error"
        return results
    
    if not os.path.isdir(folder_path):
        results["scanStatus"] = "error"
        results["error"] = f"Path is not a directory: {folder_path}"
        results["progress"]["stage"] = "error"
        return results
    
    try:
        # SECURITY: Resolve base directory to real path once at start
        # This prevents any directory traversal from affecting the base check
        base_real_path = os.path.realpath(folder_path)
        
        # PROGRESS: Pre-scan to count total files for progress percentage
        results["progress"]["stage"] = "counting"
        total_files = _count_files_quickly(folder_path, base_real_path)
        results["progress"]["total"] = total_files
        
        current_time = time.time()
        age_threshold_seconds = Config.FileSystem.OLD_FILE_AGE_SECONDS  # 180 days in seconds
        
        # First pass: Collect file metadata
        files_by_size = defaultdict(list)
        old_files = []
        system_files = []
        
        # PROGRESS: Update stage
        results["progress"]["stage"] = "scanning"
        processed_count = 0
        
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
                
                # PROGRESS: Update progress callback if provided
                processed_count += 1
                if processed_count % Config.FileSystem.PROGRESS_UPDATE_FREQUENCY == 0:  # Update every N files to minimize overhead
                    percentage = round((processed_count / total_files) * 100, 1) if total_files > 0 else 0
                    results["progress"]["processed"] = processed_count
                    results["progress"]["percentage"] = percentage
                    
                    if progress_callback:
                        try:
                            progress_callback(processed_count, total_files, percentage)
                        except Exception:
                            pass  # Silently ignore callback errors
                
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
        
        # Final progress update
        results["progress"]["processed"] = processed_count
        results["progress"]["percentage"] = 100.0
        
        # PROGRESS: Update stage to hashing
        results["progress"]["stage"] = "hashing"
        
        # Second pass: Hash only files in same-size groups (potential duplicates)
        file_hashes = defaultdict(list)
        
        for file_size, file_list in files_by_size.items():
            # Only hash if there are multiple files of same size
            if len(file_list) > 1:
                for file_info in file_list:
                    file_path = file_info["path"]
                    try:
                        # Skip large files for performance
                        if file_size > Config.FileSystem.LARGE_FILE_THRESHOLD:
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
        
        # Calculate carbon savings (kg CO2 per GB per year)
        waste_gb = results["summary"]["potentialWasteSizeBytes"] / Config.Storage.BYTES_PER_GB
        results["statistics"]["carbonSaveKgPerYear"] = round(waste_gb * Config.Carbon.CARBON_PER_GB_PER_YEAR, 4)
        
        # Sort results
        results["duplicateGroups"].sort(key=lambda x: x["totalWasteBytes"], reverse=True)
        old_files.sort(key=lambda x: x["size"], reverse=True)
        system_files.sort(key=lambda x: x["size"], reverse=True)
        
        # Limit to top results for performance
        results["oldFiles"] = old_files[:Config.Performance.MAX_RESULTS_PER_CATEGORY]
        results["systemFiles"] = system_files[:Config.Performance.MAX_RESULTS_PER_CATEGORY]
        
        # PROGRESS: Mark as complete
        results["progress"]["stage"] = "complete"
        results["progress"]["percentage"] = 100.0
        
        return results
        
    except Exception as e:
        results["scanStatus"] = "error"
        results["error"] = f"Scan failed: {str(e)}"
        results["progress"]["stage"] = "error"
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
            while os.path.exists(recovery_path) and counter < Config.FileSystem.MAX_RECOVERY_NAME_ATTEMPTS:
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
        if bytes_value < Config.Storage.BYTES_PER_KB:
            if unit == 'B':
                return f"{int(bytes_value)} {unit}"
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= Config.Storage.BYTES_PER_KB
    return f"{bytes_value:.2f} PB"
