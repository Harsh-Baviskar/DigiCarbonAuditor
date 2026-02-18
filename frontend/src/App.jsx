import { useState } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import Layout from './components/Layout/Layout';
import CarbonFootprintPage from './components/CarbonFootprintPage/CarbonFootprintPage';
import SegregatorPage from './components/SegregatorPage/SegregatorPage';
import WastefulFilesPage from './components/WastefulFilesPage/WastefulFilesPage';
import GoogleDrivePage from './components/GoogleDrivePage/GoogleDrivePage';
import './App.css';

/**
 * App - Main application with navigation between different carbon auditing tools
 *
 * Features:
 * - Carbon Footprint Estimator: Calculate storage carbon emissions
 * - Segregator: Organize files by type
 * - Wasteful Files Detector: Find duplicate and wasteful files
 */
export default function App() {
  const [activeSection, setActiveSection] = useState('carbon-footprint');

  const renderPage = () => {
    switch (activeSection) {
      case 'carbon-footprint':
        return <CarbonFootprintPage />;
      case 'segregator':
        return <SegregatorPage />;
      case 'wasteful-files':
        return <WastefulFilesPage />;
      case 'google-drive':
        return <GoogleDrivePage />;
      default:
        return <CarbonFootprintPage />;
    }
  };

  return (
    <ThemeProvider>
      <Layout activeSection={activeSection} onSectionChange={setActiveSection}>
        {renderPage()}
      </Layout>
    </ThemeProvider>
  );
}


