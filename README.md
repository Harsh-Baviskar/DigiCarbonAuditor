# DigitalCarbonAuditor
# Vercel deployment

Deploy the `frontend` directory as a Vite project in Vercel:

1. Import this repository in Vercel and set the project root to `frontend`.
2. Keep the build command as `npm run build` and the output directory as `dist`.
3. Add `VITE_API_URL` with the public URL of the Flask backend.
4. Deploy the backend separately on a service that supports persistent Python filesystem access. Vercel Functions are not suitable for the current folder scanning, duplicate deletion, and recovery-bin features.
5. Configure the backend CORS policy to allow the Vercel deployment URL.

The frontend uses `frontend/vercel.json` for SPA fallback routing. Local development still uses the Vite proxy and `http://localhost:5000` by default.