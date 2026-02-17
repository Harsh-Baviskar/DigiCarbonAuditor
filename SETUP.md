# Backend-Frontend Connection Setup

## Overview
Your Digital Carbon Auditor application now has the backend and frontend connected. The frontend (React with Vite) communicates with the Flask backend to calculate carbon emissions.

## Architecture
- **Backend**: Flask server running on `http://localhost:5000`
- **Frontend**: React/Vite development server on `http://localhost:3000`
- **Communication**: Direct HTTP calls with CORS enabled

## Prerequisites
- **Backend**: Python 3.8+, pip
- **Frontend**: Node.js 14+, npm/yarn

## Backend Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file in the `backend` folder with:
```env
ELECTRICITYMAP_API_KEY=your_api_key_here
```

Get your API key from: https://electricitymap.org/api

### 3. Run the Backend Server
```bash
cd backend/app
python app.py
```

The backend will start at `http://localhost:5000`

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Backend URL (Optional)
The default backend URL is `http://localhost:5000` (set in `.env.local`).

If you need to change it:
```bash
# Edit .env.local
VITE_API_URL=http://your-backend-url:5000
```

### 3. Run the Development Server
```bash
npm run dev
```

The frontend will start at `http://localhost:3000`

## API Endpoints

### POST /calculate
Calculate carbon emissions for a given storage size.

**Request:**
```json
{
  "storage_tb": 2.5,
  "region": "IN-WE"
}
```

**Response:**
```json
{
  "storage_tb": 2.5,
  "energy_kwh_per_year": 125,
  "carbon_kg_per_year": 50,
  "carbon_cost_estimate": 2.5
}
```

### POST /upload-folder
Upload and scan a folder (as a zip file).

**Request:** multipart/form-data
- `file`: zip file of the folder
- `region`: region code (default: IN-WE)

**Response:** Same as /calculate endpoint

## Usage

1. **Start Backend**: `python backend/app/app.py`
2. **Start Frontend**: `npm run dev` in the frontend folder
3. **Open Browser**: Navigate to `http://localhost:3000`
4. **Enter Storage Size**: Type in a storage size in GB (e.g., "500" for 500GB)
5. **View Results**: See carbon emissions and recommendations

## Regions Supported
- `IN-WE`: India (West)
- `IN-KA`: India (Karnataka)
- `US-VA`: United States (Virginia)
- `US-NY`: United States (New York)
- `GB`: Great Britain
- `DE`: Germany
- `FR`: France
- And many more from ElectricityMap

## Troubleshooting

### CORS Errors
- Ensure Flask CORS is enabled (already configured)
- Check that backend is running on port 5000
- Verify `VITE_API_URL` in `.env.local`

### Backend Connection Failed
- Check if backend is running: `curl http://localhost:5000/calculate`
- Verify port 5000 is not in use
- Check firewall settings

### Missing ElectricityMap API
- Get an API key from https://electricitymap.org/api
- Set `ELECTRICITYMAP_API_KEY` in backend `.env`

## File Structure
```
project/
├── backend/
│   ├── app/
│   │   ├── app.py (main Flask app with CORS enabled)
│   │   ├── calculator.py
│   │   ├── database.py
│   │   ├── energy.py
│   │   └── ...
│   └── requirements.txt (updated with flask-cors)
│
└── frontend/
    ├── src/
    │   ├── api/
    │   │   ├── api.js (real API client - NEW)
    │   │   └── mockApi.js (kept for reference)
    │   ├── App.jsx (updated to use real API)
    │   └── ...
    ├── .env.local (NEW - backend URL config)
    ├── .env.example (NEW - template)
    └── vite.config.js (updated with correct proxy)
```

## What Changed

### Backend
- ✅ Added `flask-cors` to requirements.txt
- ✅ Imported and enabled CORS in `app.py`

### Frontend
- ✅ Created `src/api/api.js` - Real API client
- ✅ Created `.env.local` - Backend URL configuration
- ✅ Created `.env.example` - Environment template
- ✅ Updated `App.jsx` - Uses real API instead of mock
- ✅ Updated `vite.config.js` - Correct backend proxy

## Next Steps

1. **Test the connection**: Enter a storage size and verify the backend responds
2. **Add folder scanning**: Modify frontend to accept zip file uploads (browser limitation)
3. **Deploy**: Configure production URLs and CORS origins
4. **Authentication**: Add API key or JWT authentication if needed
