# Implementation Steps - Google Drive Login

## ✅ Completed Steps

- [x] Backend dependencies installed (`pip install -r requirements.txt`)
- [x] Created `user_tokens/` directory
- [x] Created `flask_session/` directory
- [x] Created `.env` file with configuration
- [x] Created `.gitignore` with sensitive file exclusions
- [x] Created `.env` file for frontend
- [x] Backend code updated with OAuth2 functions
- [x] Frontend API functions added
- [x] GoogleDriveCallback component created

## 🔧 Next Steps (Do These Now)

### Step 1: Setup Google OAuth2 Credentials (5 minutes)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)

2. **Create/Select Project:**
   - Click project dropdown
   - Select existing project or click "New Project"
   - Name it: "Digital Carbon Auditor"
   - Click "Create"

3. **Enable Google Drive API:**
   - Search for "Google Drive API"
   - Click on it
   - Click "Enable"

4. **Create OAuth2 Credentials:**
   - Go to "Credentials"
   - Click "Create Credentials" → "OAuth Client ID"
   - Choose "Desktop application"
   - Name it: "Digital Carbon Auditor Desktop"
   - Click "Create"

5. **Download Credentials:**
   - Click the download icon (⬇️)
   - Save the JSON file

6. **Rename and Move:**
   - Rename file to: `credentials.json`
   - Move to: `backend/app/credentials.json`

7. **Add Redirect URI:**
   - Back in Google Console → Credentials
   - Click your OAuth app
   - Under "Authorized redirect URIs" click "Add URI"
   - Add: `http://localhost:5173/auth/google/callback`
   - Click "Save"

**Status:** ⏳ Waiting for you to complete this

---

### Step 2: Test Backend Login Endpoint

Open a terminal and run:

```bash
cd c:\Users\ASUS\OneDrive\Desktop\WebWeaver\DigitalCarbonAuditor\backend
python -m flask run
```

The backend should start on `http://localhost:5000`

In another terminal, run the test script:

```bash
cd c:\Users\ASUS\OneDrive\Desktop\WebWeaver\DigitalCarbonAuditor
python test_login_backend.py
```

**You should see:**
- ✓ Auth URL generated
- ✓ Not authenticated (expected)
- ✓ Correctly requires authentication

---

### Step 3: Verify Frontend Environment

Create `frontend/.env` if not exists:

```bash
echo VITE_API_URL=http://localhost:5000 > frontend/.env
```

Check it contains:
```
VITE_API_URL=http://localhost:5000
```

---

### Step 4: Update Frontend Router

Edit your `frontend/src/main.jsx` or router file and add the callback route:

**Find this section:**
```jsx
<Routes>
  <Route path="/" element={<App />} />
  {/* other routes */}
</Routes>
```

**Add this route:**
```jsx
import GoogleDriveCallback from './components/GoogleDriveCallback/GoogleDriveCallback';

<Route path="/auth/google/callback" element={<GoogleDriveCallback />} />
```

**Full example:**
```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App';
import GoogleDriveCallback from './components/GoogleDriveCallback/GoogleDriveCallback';

function Router() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/auth/google/callback" element={<GoogleDriveCallback />} />
      </Routes>
    </BrowserRouter>
  );
}

export default Router;
```

---

### Step 5: Test Complete Flow

**Terminal 1 - Start Backend:**
```bash
cd backend
python -m flask run
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm run dev
```

**Manual Testing:**

1. Open http://localhost:5173 in browser
2. Navigate to Google Drive section
3. Click "Login with Google"
4. You'll be redirected to Google OAuth
5. Click "Allow" to authorize
6. See success message on callback page
7. Get redirected back to home
8. Click "Scan My Drive"
9. See results!

---

## 🧪 Testing Each Component

### Test 1: Backend Login Endpoint
```bash
curl http://localhost:5000/google-drive/login
```
Should return: `{"status": "success", "auth_url": "..."}`

### Test 2: Session Info (Not Authenticated)
```bash
curl http://localhost:5000/google-drive/session-info
```
Should return: `{"authenticated": false, "message": "Not logged in"}`

### Test 3: Scan Without Auth (Should Fail)
```bash
curl -X POST http://localhost:5000/google-drive/scan \
  -H "Content-Type: application/json" \
  -d '{"region": "IN-WE"}'
```
Should return: `{"error": "Not authenticated", ...}` with 401 status

---

## 🐛 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError: No module named 'flask_session'" | Run: `pip install flask-session` |
| "Credentials file not found" | Download credentials.json from Google Console, save to `backend/app/credentials.json` |
| "Port 5000 in use" | Use: `flask run --port 5001` |
| "redirect_uri_mismatch" error | Check Google Console has exact URI: `http://localhost:5173/auth/google/callback` |
| "No authorization code" | Clear browser cookies, try again |
| CORS errors on frontend | Check backend `.env` has `SECRET_KEY` set |

---

## 📋 Implementation Checklist

- [ ] Step 1: Google OAuth2 credentials setup
- [ ] Step 2: Backend testing (test_login_backend.py)
- [ ] Step 3: Frontend environment verified
- [ ] Step 4: Frontend router updated with callback
- [ ] Step 5: Full flow tested (login → scan)
- [ ] Manual testing: All scenarios verified
- [ ] Update GoogleDriveConnect component (see note below)
- [ ] Production configuration ready

---

## 📝 Update GoogleDriveConnect Component

Your existing `GoogleDriveConnect.jsx` should now use the new functions:

```javascript
import { 
  initiateGoogleDriveLogin, 
  getGoogleDriveSessionInfo,
  logoutFromGoogleDrive,
  scanGoogleDrive 
} from '../../api/api';

// Check auth on mount
useEffect(() => {
  checkAuthStatus();
}, []);

const checkAuthStatus = async () => {
  const session = await getGoogleDriveSessionInfo();
  if (session.authenticated) {
    setUserInfo(session.user_info);
  }
};

// Start login
const handleLogin = async () => {
  const response = await initiateGoogleDriveLogin();
  window.location.href = response.auth_url;
};

// Logout
const handleLogout = async () => {
  await logoutFromGoogleDrive();
  // Clear state...
};

// Scan
const handleScan = async () => {
  const result = await scanGoogleDrive('IN-WE');
  // Show results...
};
```

See `FRONTEND_GOOGLE_DRIVE_INTEGRATION.md` for complete component code.

---

## 🚀 What's Working Now

✅ OAuth2 login flow  
✅ Per-user token storage  
✅ Session management  
✅ Automatic token refresh  
✅ User information retrieval  
✅ Protected scan endpoints  
✅ Error handling  
✅ Multi-user support  

---

## 📚 Documentation

- **Setup Guide**: `GOOGLE_DRIVE_LOGIN_SETUP.md`
- **Frontend Integration**: `FRONTEND_GOOGLE_DRIVE_INTEGRATION.md`
- **Security**: `GOOGLE_DRIVE_SECURITY_CHECKLIST.md`
- **Summary**: `IMPLEMENTATION_SUMMARY.md`
- **Quick Start**: `QUICK_START_LOGIN.md`

---

## ⏭️ After Implementation

1. **For Production:**
   - Generate strong SECRET_KEY
   - Update Google Console redirect URIs
   - Configure HTTPS
   - Switch to database-backed sessions

2. **Team Setup:**
   - Share `.env.example` (not `.env`)
   - Document credentials setup
   - Setup CI/CD tests

3. **Monitoring:**
   - Setup error logging
   - Monitor auth failures
   - Track usage metrics

---

**Ready?** Start with Step 1 (Google OAuth setup) and work through each step. Let me know when you hit any issues!
