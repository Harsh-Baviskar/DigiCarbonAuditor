# Frontend Backend Integration - Updated

## What Was Changed

### 1. **Frontend API Client** (`src/api/api.js`)
- ✅ Added `transformCategoryBreakdown()` - Converts backend category data to file type array with percentages
- ✅ Added `createSuggestedActions()` - Generates actionable recommendations based on carbon impact
- ✅ Updated `startScan()` - Properly transforms backend response to match frontend component expectations

### 2. **Scan Input Section** (`src/components/ScanInputSection/ScanInputSection.jsx`)
- ✅ Added region selector dropdown (IN-WE, IN-KA, US-VA, GB, DE, FR, etc.)
- ✅ Updated hints to reflect storage size input (GB)
- ✅ Updated `handleSubmit()` to pass region parameter to backend
- ✅ Updated hint text to guide users to enter storage in GB

### 3. **Scan Input Styles** (`src/components/ScanInputSection/ScanInputSection.module.css`)
- ✅ Added `.regionSection` - Container for region selector
- ✅ Added `.select` - Styled select dropdown with focus states

### 4. **Main App** (`src/App.jsx`)
- ✅ Updated `handleScan()` callback to accept and pass region parameter

## How It Works Now

1. **User Flow:**
   - User enters storage size in GB (e.g., 500)
   - User selects region (e.g., India West)
   - Click "Start Scan" button
   - Frontend calls backend `/calculate` endpoint with storage_tb and region

2. **Data Transformation:**
   - Backend returns: `{files_scanned, storage_tb, category_breakdown, energy_kwh_per_year, carbon_kg_per_year, carbon_cost_estimate}`
   - Frontend transforms category_breakdown (e.g., `{image: 5GB, video: 10GB}`) into:
   ```javascript
   byFileType: [
     { type: 'video', count: 0, sizeBytes: 10GB, percentOfTotal: 66.7 },
     { type: 'image', count: 0, sizeBytes: 5GB, percentOfTotal: 33.3 }
   ]
   ```

3. **Components Work With:**
   - **SummaryMetrics**: Displays total files, storage size, duplicates, wasted storage
   - **TopContributors**: Shows file type breakdown and folder duplication (from backend data)
   - **SuggestedActions**: Shows carbon reduction recommendations based on current storage
   - **DuplicateFilesView**: Currently empty (not provided by backend)

## Backend Response Example

**Request:**
```json
{
  "storage_tb": 0.5,
  "region": "IN-WE"
}
```

**Response:**
```json
{
  "storage_tb": 0.5,
  "energy_kwh_per_year": 25.0,
  "carbon_kg_per_year": 8.5,
  "carbon_cost_estimate": 0.42,
  "category_breakdown": {
    "video": 536870912,
    "image": 268435456,
    "application": 201326592
  },
  "files_scanned": 150
}
```

## Frontend Limitations (By Design)

Based on current backend implementation:
- ❌ Duplicate file detection (not built in backend)
- ❌ Folder-level duplication analysis (not built in backend)
- ✅ File type/category breakdown (implemented via MIME type detection)
- ✅ Carbon emissions calculation (implemented)
- ✅ Energy consumption estimation (implemented)

## Testing

To test the integration:

1. **Backend running:**
   ```bash
   cd backend/app
   python app.py
   ```

2. **Frontend running:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test a scan:**
   - Navigate to `http://localhost:3000`
   - Enter storage size: `500` (GB)
   - Select region: `India (West)`
   - Click "Start Scan"
   - View results in dashboard

## Environment Variables

**Frontend** (`.env.local`):
```
VITE_API_URL=http://localhost:5000
```

**Backend** (`.env`):
```
ELECTRICITYMAP_API_KEY=your_key_here
```

Get API key from: https://electricitymap.org/api
