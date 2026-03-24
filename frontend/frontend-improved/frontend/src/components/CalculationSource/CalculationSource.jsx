import styles from './CalculationSource.module.css';
import InfoTooltip from '../InfoTooltip/InfoTooltip';

/**
 * CalculationSource - Displays the data source and calculation method
 * Shows region, carbon intensity, and confirms real-time API usage
 */
export default function CalculationSource({ result }) {
  if (!result) return null;

  const region = result.region || 'Unknown';
  const carbonIntensity = result.carbonIntensity ?? 'N/A';
  const calculationMethod = result.calculationMethod || 'api_based_with_region';
  const energyPerGb = (result.energyKwhPerYear || 0) / ((result.summary?.totalStorageBytes || 1) / (1024 ** 3));
  const energyPerTb = energyPerGb * 1024;

  const getCardColor = (intensity) => {
    if (intensity < 100) return 'very-low';
    if (intensity < 200) return 'low';
    if (intensity < 400) return 'medium';
    if (intensity < 600) return 'high';
    return 'very-high';
  };

  const colorClass = getCardColor(carbonIntensity);

  return (
    <section className={styles.section} aria-labelledby="source-heading">
      <h3 id="source-heading" className={styles.heading}>
        Calculation Details
        <InfoTooltip
          content="These values come directly from ElectricityMap's real-time API based on your region's electricity grid composition."
          label="Data source information"
        />
      </h3>

      <div className={`${styles.card} ${styles[`card-${colorClass}`]}`}>
        <div className={styles.cardContent}>
          <div className={styles.row}>
            <div className={styles.label}>Region</div>
            <div className={styles.value}>{region}</div>
          </div>

          <div className={styles.row}>
            <div className={styles.label}>Carbon Intensity</div>
            <div className={styles.value}>
              {typeof carbonIntensity === 'number' ? `${carbonIntensity} gCO2/kWh` : carbonIntensity}
            </div>
          </div>

          <div className={styles.row}>
            <div className={styles.label}>Energy per TB/Year</div>
            <div className={styles.value}>{energyPerTb.toFixed(1)} kWh</div>
          </div>

          <div className={styles.row}>
            <div className={styles.label}>Data Source</div>
            <div className={styles.value}>
              <span className={styles.badge}>✓ ElectricityMap API</span>
            </div>
          </div>

          <div className={styles.row}>
            <div className={styles.label}>Calculation Method</div>
            <div className={styles.value}>
              <span className={styles.methodText}>
                {calculationMethod === 'api_based_with_region' 
                  ? 'Region-based with real electricity mix'
                  : calculationMethod}
              </span>
            </div>
          </div>
        </div>

        <div className={styles.equation}>
          <div className={styles.formulaRow}>
            <span>Carbon Emissions = Energy × Carbon Intensity ÷ 1000</span>
          </div>
          <div className={styles.formulaRow} style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
            <span>CO₂ kg/year = (Storage GB × 1.5 kWh) × {carbonIntensity} ÷ 1000</span>
          </div>
        </div>
      </div>

      <div className={styles.intensityScale}>
        <h4 className={styles.scaleTitle}>Carbon Intensity Scale</h4>
        <div className={styles.scaleItems}>
          <div className={styles.scaleItem}>
            <span className={`${styles.scaleBadge} ${styles['scale-very-low']}`}>Very Low</span>
            <span className={styles.scaleText}>&lt; 100 gCO2/kWh (Mostly renewables/nuclear)</span>
          </div>
          <div className={styles.scaleItem}>
            <span className={`${styles.scaleBadge} ${styles['scale-low']}`}>Low</span>
            <span className={styles.scaleText}>100-200 gCO2/kWh</span>
          </div>
          <div className={styles.scaleItem}>
            <span className={`${styles.scaleBadge} ${styles['scale-medium']}`}>Medium</span>
            <span className={styles.scaleText}>200-400 gCO2/kWh</span>
          </div>
          <div className={styles.scaleItem}>
            <span className={`${styles.scaleBadge} ${styles['scale-high']}`}>High</span>
            <span className={styles.scaleText}>400-600 gCO2/kWh</span>
          </div>
          <div className={styles.scaleItem}>
            <span className={`${styles.scaleBadge} ${styles['scale-very-high']}`}>Very High</span>
            <span className={styles.scaleText}>&gt; 600 gCO2/kWh (Coal-heavy)</span>
          </div>
        </div>
      </div>
    </section>
  );
}
