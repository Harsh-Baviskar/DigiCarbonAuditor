import styles from './CarbonImpact.module.css';
import InfoTooltip from '../InfoTooltip/InfoTooltip';
import { getCarbonStory } from '../../utils/carbonStorytelling';

/**
 * CarbonImpact - Displays CO2 emissions, energy consumption, and cost
 * Shows the environmental impact of data storage with clear metrics
 */
export default function CarbonImpact({ result }) {
  if (!result) return null;

  console.log('CarbonImpact - Full result object:', result);
  console.log('CarbonImpact - Result keys:', Object.keys(result || {}));
  console.log('CarbonImpact - Direct access:', {
    carbonKgPerYear: result.carbonKgPerYear,
    energyKwhPerYear: result.energyKwhPerYear,
    carbonCostEstimate: result.carbonCostEstimate,
    types: {
      carbonKgPerYear: typeof result.carbonKgPerYear,
      energyKwhPerYear: typeof result.energyKwhPerYear,
      carbonCostEstimate: typeof result.carbonCostEstimate,
    }
  });

  const carbonKg = result.carbonKgPerYear ?? 0;
  const energyKwh = result.energyKwhPerYear ?? 0;
  const costEstimate = result.carbonCostEstimate ?? 0;
  const storageTb = result.summary?.totalStorageBytes ? (result.summary.totalStorageBytes / (1024 ** 4)).toFixed(2) : 0;
  const region = result.region || 'Unknown';
  const carbonIntensity = result.carbonIntensity ?? 'N/A';

  console.log('CarbonImpact - Parsed values:', { carbonKg, energyKwh, costEstimate, storageTb, region, carbonIntensity });

  // Get comprehensive carbon storytelling data
  const story = getCarbonStory(carbonKg, 'storage');

  return (
    <section className={styles.section} aria-labelledby="carbon-heading">
      <h2 id="carbon-heading" className={styles.heading}>
        Carbon Impact
        <InfoTooltip
          content="Estimated annual CO2 emissions from storing your data based on regional electricity carbon intensity and data center efficiency."
          label="How carbon impact is calculated"
        />
      </h2>

      <div className={styles.regionInfo}>
        <span className={styles.regionLabel}>Region:</span>
        <span className={styles.regionValue}>{region}</span>
        <span className={styles.separator}>•</span>
        <span className={styles.regionLabel}>Carbon Intensity:</span>
        <span className={styles.regionValue}>{typeof carbonIntensity === 'number' ? `${carbonIntensity} gCO2/kWh` : carbonIntensity}</span>
        <InfoTooltip
          content="Real-time carbon intensity data from ElectricityMap API based on your selected region's electricity grid composition."
          label="Data source"
        />
      </div>

      {/* Contextual narrative message */}
      <div className={styles.narrativeBox}>
        <p className={styles.narrativeText}>{story.narrative}</p>
      </div>

      <div className={styles.grid}>
        {/* CO2 Emissions Card */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <h3 className={styles.cardTitle}>CO2 Emissions</h3>
            <span className={styles.icon}>🏭</span>
          </div>
          <div className={styles.value}>{carbonKg.toLocaleString('en-US', { maximumFractionDigits: 1 })} kg</div>
          <div className={styles.subtext}>per year</div>
          
          <div className={styles.comparisons}>
            <div className={styles.comparison}>
              <span className={styles.comparisonLabel}>Equivalent to:</span>
              <div className={styles.equivalenceGroup}>
                <div className={styles.equivalenceItem}>
                  <span className={styles.equivalenceValue}>{story.cars.distance}</span>
                  <span className={styles.equivalenceNote}>{story.cars.description}</span>
                </div>
                <div className={styles.equivalenceItem}>
                  <span className={styles.equivalenceValue}>{story.flight.distance}</span>
                  <span className={styles.equivalenceNote}>round-trip flight</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Energy Consumption Card */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <h3 className={styles.cardTitle}>Energy Offset</h3>
            <span className={styles.icon}>🌱</span>
          </div>
          <div className={styles.value}>{story.trees.count}</div>
          <div className={styles.subtext}>to offset annual emissions</div>
          
          <div className={styles.comparisons}>
            <div className={styles.comparison}>
              <span className={styles.comparisonLabel}>Impact:</span>
              <span className={styles.comparisonValue}>{story.trees.description}</span>
            </div>
            <div className={styles.comparison}>
              <span className={styles.comparisonLabel}>Storage size:</span>
              <span className={styles.comparisonValue}>{storageTb} TB</span>
            </div>
          </div>
        </div>

        {/* Cost Estimate Card */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <h3 className={styles.cardTitle}>Carbon Cost</h3>
            <span className={styles.icon}>💲</span>
          </div>
          <div className={styles.value}>${costEstimate.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
          <div className={styles.subtext}>per year (estimated)</div>
          
          <div className={styles.comparisons}>
            <div className={styles.comparison}>
              <span className={styles.comparisonLabel}>Energy usage:</span>
              <span className={styles.comparisonValue}>{energyKwh.toLocaleString('en-US', { maximumFractionDigits: 0 })} kWh/year</span>
            </div>
            <div className={styles.comparison}>
              <span className={styles.comparisonLabel}>Monthly cost:</span>
              <span className={styles.comparisonValue}>${(costEstimate / 12).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className={styles.recommendations}>
        <h3 className={styles.recTitle}>Recommendations to Reduce Impact</h3>
        <ul className={styles.recList}>
          <li> Delete unnecessary files: Reducing storage by 10% saves ~{(carbonKg * 0.1).toFixed(1)} kg CO2/year</li>
          <li>Archive old data: Move infrequently accessed data to cold storage</li>
          <li> Use renewable energy provider: Some cloud providers offer 100% renewable options</li>
          <li> Monitor regularly: Track storage growth to prevent unnecessary expansion</li>
        </ul>
      </div>
    </section>
  );
}
