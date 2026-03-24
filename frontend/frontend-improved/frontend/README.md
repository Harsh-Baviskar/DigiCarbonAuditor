# Digital Carbon Auditor – Frontend

Enterprise-grade React dashboard for estimating digital carbon footprint and identifying duplicate storage.

## Setup

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Build

```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── api/           # API layer (mockApi.js – replace with real backend)
│   ├── components/    # React components
│   │   ├── Layout/
│   │   ├── ScanInputSection/
│   │   ├── SummaryMetrics/
│   │   ├── DuplicateFilesView/
│   │   └── StatusFeedback/
│   ├── utils/         # Formatters (bytes, hash truncation)
│   ├── App.jsx
│   └── main.jsx
├── index.html
└── package.json
```

## Backend Integration

Replace `startScan(path)` in `src/api/mockApi.js` with:

```js
const response = await fetch('/api/scan', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ path }),
});
const data = await response.json();
if (!response.ok) throw new Error(data.message || 'Scan failed');
return data;
```

The API proxy in `vite.config.js` forwards `/api/*` to the backend (default: `http://localhost:8000`).
