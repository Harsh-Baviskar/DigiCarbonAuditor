import styles from './CarbonImpact.module.css';
import InfoTooltip from '../InfoTooltip/InfoTooltip';

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

  console.log('CarbonImpact - Parsed values:', { carbonKg, energyKwh, costEstimate, storageTb });

  // Calculate equivalent comparisons
  const carEmissions = (carbonKg / 4.6).toFixed(1); // Average car emits 4.6 kg CO2/gallon
  const treesNeeded = (carbonKg / 21).toFixed(1); // Average tree absorbs 21 kg CO2/year
  const homeEquivalent = (energyKwh / 10500 * 100).toFixed(1); // Average US home uses 10,500 kWh/year

  return (
    <section className={styles.section} aria-labelledby="carbon-heading">
      <h2 id="carbon-heading" className={styles.heading}>
        Carbon Impact
        <InfoTooltip
          content="Estimated annual CO2 emissions from storing your data based on regional electricity carbon intensity and data center efficiency."
          label="How carbon impact is calculated"
        />
      </h2>

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
              <span className={styles.comparisonValue}>{carEmissions} gallons of gas</span>
            </div>
            <div className={styles.comparison}>
              <span className={styles.comparisonLabel}>Offset by:</span>
              <span className={styles.comparisonValue}>{treesNeeded} trees/year</span>
            </div>
          </div>
        </div>

        {/* Energy Consumption Card */}
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <h3 className={styles.cardTitle}>Energy Consumption</h3>
            <span className={styles.icon}>⚡</span>
          </div>
          <div className={styles.value}>{energyKwh.toLocaleString('en-US', { maximumFractionDigits: 1 })} kWh</div>
          <div className={styles.subtext}>per year</div>
          
          <div className={styles.comparisons}>
            <div className={styles.comparison}>
              <span className={styles.comparisonLabel}>Storage size:</span>
              <span className={styles.comparisonValue}>{storageTb} TB</span>
            </div>
            <div className={styles.comparison}>
              <span className={styles.comparisonLabel}>Home equivalent:</span>
              <span className={styles.comparisonValue}>{homeEquivalent}% of avg US home</span>
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
              <span className={styles.comparisonLabel}>Cost per TB:</span>
              <span className={styles.comparisonValue}>${(costEstimate / storageTb || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
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
