# Waste Detector - "BAD REQUEST" Error Fix

## Problem Analysis

**Error:** "Scan failed: Backend error: BAD REQUEST" (HTTP 400)

**Root Causes:**
1. Path from folder picker is empty (user canceled dialog)
2. Path validation was not catching empty paths
3. Vite proxy not configured for `/waste-detect` endpoint
4. Frontend using direct backend URL instead of proxy

## Solutions Implemented

### 1. Backend Improvements (`app.py`)

**Better Error Handling:**
```python
# Before: Minimal error messages
if not data or 'path' not in data:
    return jsonify({"detail": "JSON body with 'path' is required."}), 400

# After: Clear validation with detailed messages
data = request.get_json(silent=True)

if data is None:
    return jsonify({"detail": "Request body must be JSON with Content-Type: application/json", "scanStatus": "error"}), 400

if not isinstance(data, dict):
    return jsonify({"detail": "Request body must be a JSON object", "scanStatus": "error"}), 400

folder_path = data.get('path', '').strip()

if not folder_path:
    return jsonify({"detail": "Path is required and cannot be empty", "scanStatus": "error"}), 400
```

**Benefits:**
- Catches empty/whitespace-only paths
- Clear JSON validation
- Better error messages

### 2. Frontend - ScanInputSection (`ScanInputSection.jsx`)

**Better Path Validation:**
```javascript
// Before: Just checked if path exists
if (data.path) {
    setPath(data.path);
}

// After: Check if path is valid and non-empty
if (data.path && data.path.trim().length > 0) {
    setPath(data.path);
} else {
    setPathError('No folder was selected. Please try again.');
}
```

**Benefits:**
- Prevents empty paths from being submitted
- Clear message when user cancels folder dialog
- Validates path is meaningful

### 3. Frontend - WastefulFilesPage (`WastefulFilesPage.jsx`)

**Improved Error Messages:**
```javascript
// Before: Generic error
throw new Error(errorMessage);

// After: Specific handling with logging
console.log('Starting waste detection scan for:', path);
console.log('Response status:', response.status);
console.log('Response data:', data);

if (!response.ok) {
    const errorMessage = data.detail || data.error || `Scan failed with status ${response.status}`;
    throw new Error(errorMessage);
}

if (data.scanStatus === 'error') {
    throw new Error(data.error || data.detail || 'Scan encountered an unexpected error');
}
```

**Benefits:**
- Detailed console logging for debugging
- Multiple error message fallbacks
- Checks both HTTP status and response body

### 4. Vite Proxy Configuration (`vite.config.js`)

**Added Missing Endpoint Proxies:**
```javascript
'/waste-detect': {
    target: 'http://127.0.0.1:5000',
    changeOrigin: true,
    secure: false,
},
'/waste-detect/delete-duplicates': {
    target: 'http://127.0.0.1:5000',
    changeOrigin: true,
    secure: false,
},
```

**Frontend URL Updates:**
```javascript
// Before: Direct backend URL (CORS risk)
fetch('http://127.0.0.1:5000/waste-detect')

// After: Via vite proxy (safer, dev-friendly)
fetch('/waste-detect')
```

**Benefits:**
- Consistent with other API calls
- Avoids CORS issues during development
- Better separation of dev/prod configurations

### 5. Error Messages Improvements

**ScanInputSection Hint Text:**
```
"Make sure the backend is running (python app.py in /backend)."
```

**Validation Flow:**
```
User clicks "Browse Folder"
    ↓
Dialog opens (tkinter)
    ↓
User selects folder OR cancels
    ↓
If canceled: data.path = "" (empty string)
    ↓
Frontend checks: if (data.path && data.path.trim().length > 0)
    ↓
If empty: Show error "No folder was selected"
    ↓
If valid: Auto-fill path field
```

## Testing

### Test 1: Endpoint Health
```bash
cd backend
python test_waste_detect_endpoint.py
```

**Expected Output:**
```
✅ Endpoint working correctly!
Scan Status: success
Total Files: 36
Duplicates: 10
```

### Test 2: Folder Picker
```bash
cd backend
python test_select_folder_endpoint.py
```

**Expected:**
- If user selects folder: Shows path
- If user cancels: Shows empty path (normal)

### Test 3: End-to-End Flow
1. Start backend: `python app/app.py` in `/backend`
2. Start frontend: `npm run dev` in `/frontend`
3. Navigate to Wasteful Files Detector
4. Click "Browse Folder" → Select a folder
5. Should show: "Selected: C:\Users\..."
6. Click "Start Scan" → Scanning begins
7. Results display with statistics

## Common Issues & Solutions

### Issue 1: "Failed to open folder browser"
**Cause:** Backend not running
**Solution:** 
```bash
cd backend
python app/app.py
# or
python -m flask --app app.app run
```

### Issue 2: "No folder was selected"
**Cause:** User canceled the folder picker dialog
**Solution:** Click "Browse Folder" again and select a folder

### Issue 3: "Path does not exist"
**Cause:** Invalid or deleted folder path
**Solution:** Re-select the folder using "Browse Folder"

### Issue 4: "Scan failed" with specific error
**Solution:** Check browser console (F12) for detailed error message

## Files Modified

1. **backend/app/app.py**
   - Better JSON validation
   - Clear error messages
   - Empty path detection

2. **frontend/vite.config.js**
   - Added `/waste-detect` proxy
   - Added `/waste-detect/delete-duplicates` proxy

3. **frontend/src/components/ScanInputSection/ScanInputSection.jsx**
   - Empty path validation
   - Better error messages
   - Uses vite proxy (`/select-folder`)

4. **frontend/src/components/WastefulFilesPage/WastefulFilesPage.jsx**
   - Better error handling
   - Detailed console logging
   - Uses vite proxy (`/waste-detect`)
   - Multiple error fallbacks

5. **frontend/src/components/WastefulFilesStatistics/WastefulFilesStatistics.jsx**
   - Uses vite proxy (`/waste-detect/delete-duplicates`)

## Testing Files Created

1. **backend/test_waste_detect_endpoint.py**
   - Tests `/waste-detect` endpoint
   - Verifies JSON response format
   - Checks CORS headers

2. **backend/test_select_folder_endpoint.py**
   - Tests `/select-folder` endpoint
   - Verifies folder path return

## What Now Works

✅ **Folder Selection**
- Click "Browse Folder" → Native OS folder picker
- Select folder → Auto-filled path field
- Clear error if user cancels

✅ **Scan Submission**
- Path validated before sending to backend
- Clear error messages if validation fails
- Loading state during scan

✅ **Error Handling**
- Empty paths caught on frontend
- Detailed backend error messages
- Console logging for debugging

✅ **API Communication**
- All endpoints use vite proxy
- Consistent with other endpoints
- Better CORS handling

## Recommended Development Setup

**Terminal 1 - Backend:**
```bash
cd backend
python app/app.py
# Backend runs on http://127.0.0.1:5000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Frontend runs on http://localhost:3000
# Proxy routes to backend
```

**Browser:**
- Open http://localhost:3000
- Navigate to Wasteful Files Detector
- Click "Browse Folder" and select a folder to scan

## Future Improvements

1. **Progress Bar** - Show scanning progress for large folders
2. **Batch Delete** - Delete multiple duplicate groups at once
3. **Archive Instead of Delete** - Option to zip old files
4. **Schedule Scans** - Automatic periodic scanning
5. **Export Reports** - Save results as CSV/PDF
