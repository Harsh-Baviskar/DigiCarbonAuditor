import styles from './EnergyBreakdown.module.css';
import InfoTooltip from '../InfoTooltip/InfoTooltip';

/**
 * EnergyBreakdown - Visualizes energy consumption breakdown
 * Shows how storage translates to energy and carbon
 */
export default function EnergyBreakdown({ result }) {
  if (!result) return null;

  console.log('EnergyBreakdown - Full result object:', result);
  console.log('EnergyBreakdown - Carbon values:', {
    energyKwhPerYear: result.energyKwhPerYear,
    carbonKgPerYear: result.carbonKgPerYear,
    carbonCostEstimate: result.carbonCostEstimate,
  });

  const storageTb = result.summary?.totalStorageBytes ? (result.summary.totalStorageBytes / (1024 ** 4)).toFixed(2) : 0;
  const energyKwh = result.energyKwhPerYear ?? 0;
  const carbonKg = result.carbonKgPerYear ?? 0;
  const costEstimate = result.carbonCostEstimate ?? 0;

  // Calculate efficiency metrics
  const energyPerTb = storageTb > 0 ? (energyKwh / storageTb).toFixed(2) : 0;
  const carbonPerTb = storageTb > 0 ? (carbonKg / storageTb).toFixed(2) : 0;
  const costPerTb = storageTb > 0 ? (costEstimate / storageTb).toFixed(2) : 0;

  // Severity indicators
  const getSeverity = (value, carbonPerTb) => {
    if (carbonPerTb < 5) return 'low';
    if (carbonPerTb < 15) return 'medium';
    return 'high';
  };

  const severity = getSeverity(carbonKg, carbonPerTb);

  return (
    <section className={styles.section} aria-labelledby="energy-heading">
      <h2 id="energy-heading" className={styles.heading}>
        Energy & Efficiency Metrics
        <InfoTooltip
          content="Understanding energy usage helps you make informed decisions about data storage and optimization strategies."
          label="Energy metrics explained"
        />
      </h2>

      {/* Efficiency Metrics */}
      <div className={styles.metricsGrid}>
        <div className={styles.metricCard}>
          <h3 className={styles.metricLabel}>Energy per TB</h3>
          <div className={styles.metricValue}>{energyPerTb} kWh/TB</div>
          <p className={styles.metricInfo}>Annual energy per terabyte of storage</p>
        </div>

        <div className={styles.metricCard}>
          <h3 className={styles.metricLabel}>Carbon per TB</h3>
          <div className={styles.metricValue}>{carbonPerTb} kg CO2/TB</div>
          <p className={styles.metricInfo}>Annual carbon emissions per terabyte</p>
        </div>

        <div className={styles.metricCard}>
          <h3 className={styles.metricLabel}>Cost per TB</h3>
          <div className={styles.metricValue}>${costPerTb}</div>
          <p className={styles.metricInfo}>Annual carbon cost per terabyte</p>
        </div>
      </div>

      {/* Impact Severity */}
      <div className={`${styles.severityCard} ${styles[`severity-${severity}`]}`}>
        <h3 className={styles.severityTitle}>
          {severity === 'low' && ' Low Carbon Footprint'}
          {severity === 'medium' && ' Medium Carbon Footprint'}
          {severity === 'high' && ' High Carbon Footprint'}
        </h3>
        <p className={styles.severityText}>
          {severity === 'low' && 'Your data storage has a relatively low environmental impact. Consider these optional optimizations:'}
          {severity === 'medium' && 'Your data storage has a moderate environmental impact. Consider optimizing your storage:'}
          {severity === 'high' && 'Your data storage has a significant environmental impact. Optimization is recommended:'}
        </p>

        <ul className={styles.actionList}>
          <li>Audit storage regularly to identify and remove unnecessary files</li>
          <li>Implement data lifecycle policies to archive old data</li>
          <li>Consider moving to renewable-energy-powered data centers</li>
          <li>Enable compression where possible to reduce storage needs</li>
        </ul>
      </div>

      {/* Carbon Intensity Info */}
      <div className={styles.infoBox}>
        <h3 className={styles.infoTitle}>About Your Region's Carbon Intensity</h3>
        <p className={styles.infoText}>
          The carbon footprint is calculated based on your selected region's electricity carbon intensity. 
          Different regions have different energy mixes - some powered more by renewables (lower carbon) 
          and others by fossil fuels (higher carbon). Moving to a region with cleaner energy 
          can significantly reduce your carbon footprint without changing storage habits.
        </p>
      </div>
    </section>
  );
}
