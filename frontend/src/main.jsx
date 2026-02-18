import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// Global error handler
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
  document.getElementById('root').innerHTML = `
    <div style="padding: 20px; font-family: monospace; color: red;">
      <h1>Error Loading Application</h1>
      <pre>${event.error?.toString()}</pre>
      <p>Check browser console for details</p>
    </div>
  `;
});

try {
  ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  )
} catch (error) {
  console.error('React render error:', error);
  document.getElementById('root').innerHTML = `
    <div style="padding: 20px; font-family: monospace; color: red;">
      <h1>React Error</h1>
      <pre>${error?.toString()}</pre>
      <p>Check browser console for details</p>
    </div>
  `;
}
