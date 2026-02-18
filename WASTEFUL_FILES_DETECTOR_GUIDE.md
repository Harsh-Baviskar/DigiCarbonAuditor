# Wasteful Files Detector - Usage Guide

## Overview

The **Wasteful Files Detector** identifies and analyzes three types of wasteful files:

1. **Duplicate Files** - Identical files (detected via SHA256 hash)
2. **Old/Unused Files** - Files not modified for 180+ days
3. **System Files** - System, cache, and temporary files

## Backend Components

### `wasteDetect.py`
Located at `backend/app/wasteDetect.py`

**Key Features:**
- Efficient two-pass scanning algorithm
- First pass: Collect file metadata by size
- Second pass: Hash only same-sized files (actual duplicates)
- Graceful error handling - continues even if files are inaccessible
- Skips large files (>500MB) for performance
- System file detection
- Carbon footprint calculation (0.02 kg CO2 per GB/year)

**Main Functions:**
- `scan_folder_for_waste(folder_path)` - Scan a folder
- `delete_duplicate_files(file_paths, keep_index)` - Safely delete duplicates
- `format_bytes(bytes_value)` - Format bytes to human-readable format

### API Endpoints

#### POST `/waste-detect`
Scan a folder for wasteful files.

**Request:**
```json
{
  "path": "C:\\Users\\Documents"
}
```

**Response:**
```json
{
  "scanStatus": "success",
  "scannedPath": "C:\\Users\\Documents",
  "scanTimestamp": "2026-02-18T10:30:00.000000",
  "summary": {
    "totalFiles": 5000,
    "totalSizeBytes": 107374182400,
    "duplicateFilesCount": 50,
    "duplicateSizeBytes": 5368709120,
    "oldFilesCount": 200,
    "oldFilesSizeBytes": 10737418240,
    "systemFilesCount": 100,
    "systemFilesSizeBytes": 2147483648,
    "potentialWasteSizeBytes": 16105927360,
    "errorCount": 5
  },
  "duplicateGroups": [
    {
      "hash": "e3b0c44298fc1c149afbf4c8996fb924427ae41e4649b934ca495991b7852b855",
      "fileSizeBytes": 1048576,
      "sizeFormatted": "1.00 MB",
      "duplicateCount": 3,
      "totalWasteBytes": 2097152,
      "totalWasteFormatted": "2.00 MB",
      "paths": [
        "C:\\Users\\Documents\\file1.jpg",
        "C:\\Users\\Documents\\backup\\file1.jpg",
        "C:\\Users\\Downloads\\file1.jpg"
      ]
    }
  ],
  "oldFiles": [...],
  "systemFiles": [...],
  "statistics": {
    "wastePercentage": 15.0,
    "carbonSaveKgPerYear": 0.3242
  }
}
```

#### POST `/waste-detect/delete-duplicates`
Delete duplicate files.

**Request:**
```json
{
  "files": [
    "C:\\Users\\Documents\\file1.jpg",
    "C:\\Users\\Documents\\backup\\file1.jpg",
    "C:\\Users\\Downloads\\file1.jpg"
  ],
  "keepIndex": 0
}
```

**Response:**
```json
{
  "status": "success",
  "deletedCount": 2,
  "failedCount": 0,
  "deletedSizeBytes": 2097152,
  "deletions": [
    {
      "path": "C:\\Users\\Documents\\file1.jpg",
      "status": "kept",
      "message": "This copy was kept"
    },
    {
      "path": "C:\\Users\\Documents\\backup\\file1.jpg",
      "status": "deleted",
      "sizeBytes": 1048576
    },
    {
      "path": "C:\\Users\\Downloads\\file1.jpg",
      "status": "deleted",
      "sizeBytes": 1048576
    }
  ]
}
```

## Frontend Components

### WastefulFilesPage
Main page for waste detection.

### WastefulFilesStatistics
Displays detailed statistics with:
- **Summary Cards**: Total storage, waste, carbon savings, duplicate/old/system files
- **Duplicate Files**: Interactive UI to select which copy to keep
- **Old Files**: List of unused files with modification dates
- **System Files**: Informational display of system files

### ScanInputSection (Updated)
Enhanced to accept folder paths for waste detection.

## How to Use

### 1. Start Backend
```bash
cd backend
python -m flask --app app.app run
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Scan a Folder
1. Navigate to **Wasteful Files Detector** tab
2. Enter a folder path:
   - Windows: `C:\Users\YourName\Documents`
   - Linux/Mac: `/home/username/documents`
3. Click **Start Scan**
4. Wait for scan to complete (depends on folder size)

### 4. View Results
- **Summary**: Quick overview of waste
- **Duplicates**: Select which copy to keep, then delete others
- **Old Files**: Review and archive old files
- **System Files**: Reference only

### 5. Delete Duplicates
1. Review the duplicate file paths
2. Select which copy to keep (radio button)
3. Click **Delete Duplicates**
4. Confirm the action
5. Files are deleted and freed storage is reported

## Algorithm Details

### First Pass: Metadata Collection
- Walks directory tree
- Gets file size, modification time
- Identifies system files
- Groups files by size
- Identifies old files

### Second Pass: Hash Calculation
- Only hashes files in same-size groups
- Skips system files
- Skips files >500MB
- Gracefully handles permission errors
- Detects actual duplicates (same content)

### Error Handling
- Continues if file is inaccessible
- Continues if permission denied
- Counts and reports errors
- Returns best-effort results

## System File Detection

### System File Extensions
.dll, .exe, .sys, .log, .cache, .sqlite, .db, etc.

### System Directories
windows, system32, node_modules, __pycache__, .git, .venv, dist, build, etc.

## Carbon Footprint Calculation

**Formula:** 0.02 kg CO2 per GB per year

**Example:** 
- 10 GB of waste × 0.02 = 0.2 kg CO2/year
- Over 10 years: 2.0 kg CO2

## Performance Notes

- Large folders may take time to scan
- Files >500MB are skipped for hash calculation to improve performance
- Duplicate detection is accurate (SHA256)
- Memory usage depends on number of unique file sizes

## Troubleshooting

### "Scan failed - An unexpected error occurred"
**Solutions:**
1. Check the path exists and is accessible
2. Try a smaller folder first
3. Ensure backend is running on port 5000
4. Check file browser console for detailed errors

### No results shown
- Folder might have no duplicates or old files
- System files are not included in main results
- Some files might be inaccessible

### Deletion failed
- Check file permissions
- Ensure the files are not open in other applications
- Try deleting a smaller group first

## Example Scenarios

### Scenario 1: Find Duplicate Photos
1. Scan Downloads folder
2. Photos might be duplicated due to multiple syncs
3. Keep the original, delete copies
4. Frees significant space (photos are large)

### Scenario 2: Old Documents
1. Scan Documents folder
2. Review files >180 days old
3. Archive important ones
4. Delete unneeded ones

### Scenario 3: Cache Cleanup
1. Scan entire user folder
2. System files will be marked
3. Get overview of storage usage
4. Identify patterns (many photos, many documents, etc.)

## Testing

Run the test file to verify installation:
```bash
cd backend
python test_waste_detect.py
```

Expected output shows scan status, file counts, and statistics.
