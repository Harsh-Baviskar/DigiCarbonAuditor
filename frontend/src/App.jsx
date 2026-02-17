import { useState } from 'react';
import Layout from './components/Layout/Layout';
import CarbonFootprintPage from './components/CarbonFootprintPage/CarbonFootprintPage';
import DuplicateDetectorPage from './components/DuplicateDetectorPage/DuplicateDetectorPage';
import SegregatorPage from './components/SegregatorPage/SegregatorPage';
import WastefulFilesPage from './components/WastefulFilesPage/WastefulFilesPage';
import './App.css';

/**
 * App - Main application with navigation between different carbon auditing tools
 * 
 * Features:
 * - Carbon Footprint Estimator: Calculate storage carbon emissions
 * - Duplicate Detector: Find and manage duplicate files
 * - Segregator: Organize files by type (coming soon)
 * - Wasteful Files Detector: Identify unused files (coming soon)
 */
export default function App() {
  const [activeSection, setActiveSection] = useState('duplicate-detector');

  const renderPage = () => {
    switch (activeSection) {
      case 'carbon-footprint':
        return <CarbonFootprintPage />;
      case 'duplicate-detector':
        return <DuplicateDetectorPage />;
      case 'segregator':
        return <SegregatorPage />;
      case 'wasteful-files':
        return <WastefulFilesPage />;
      default:
        return <DuplicateDetectorPage />;
    }
  };

  return (
    <Layout activeSection={activeSection} onSectionChange={setActiveSection}>
      {renderPage()}
    </Layout>
  );
}
