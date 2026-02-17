import React, { useEffect, useState } from 'react';
import styles from './IntelligentUsageReport.module.css';

/**
 * Intelligent Usage Report
 * Displays file categorization + cold data insights from backend.
 * Uses a premium, sustainable UI design with charts and animations.
 */
export default function IntelligentUsageReport({ report }) {
    const [animate, setAnimate] = useState(false);

    useEffect(() => {
        // Trigger animations after mount
        const timer = setTimeout(() => setAnimate(true), 100);
        return () => clearTimeout(timer);
    }, [report]);

    if (!report) {
        return (
            <section className={styles.section} aria-label="Intelligent Usage Report">
                <div className={styles.header}>
                    <LeafIcon className={styles.icon} />
                    <h2 className={styles.heading}>Intelligent Usage Insights</h2>
                </div>
                <div className={styles.loading}>
                    Gathering intelligence on file usage patterns...
                </div>
            </section>
        );
    }

    const {
        totalFiles,
        coldFilesCount,
        coldStorageGB,
        categoryBreakdown,
        recommendations
    } = report;

    // Calculate properties for charts
    const coldRatio = totalFiles > 0 ? (coldFilesCount / totalFiles) * 100 : 0;
    const degrees = (coldRatio / 100) * 360;

    // Storage Efficiency Score (Inverse of cold ratio, simplified)
    const efficiencyScore = Math.max(0, Math.round(100 - coldRatio));
    const gaugeRotation = (efficiencyScore / 100) * 180; // 180deg for semi-circle

    // Find max category count for bar scaling
    const maxCategoryCount = Math.max(...Object.values(categoryBreakdown), 1);

    return (
        <section className={styles.section} aria-label="Intelligent Usage Report">
            <div className={styles.header}>
                <LeafIcon className={styles.icon} />
                <h2 className={styles.heading}>Intelligent Usage & Cold Data Insights</h2>
            </div>

            {/* Metrics Summary Row */}
            <div className={styles.metricsRow}>
                <div className={styles.metricCard}>
                    <div className={styles.metricLabel}>Total Files</div>
                    <div className={styles.metricValue}>{totalFiles.toLocaleString()}</div>
                    <div className={styles.metricSub}>Scanned Documents</div>
                </div>
                <div className={styles.metricCard}>
                    <div className={styles.metricLabel}>Cold Files</div>
                    <div className={styles.metricValue}>{coldFilesCount.toLocaleString()}</div>
                    <div className={styles.metricSub}>{Math.round(coldRatio)}% of Total</div>
                </div>
                <div className={styles.metricCard}>
                    <div className={styles.metricLabel}>Archivable Size</div>
                    <div className={styles.metricValue}>{coldStorageGB} <small>GB</small></div>
                    <div className={styles.metricSub}>Ready for Cold Storage</div>
                </div>
            </div>

            {/* Statistical Visualization Grid */}
            <div className={styles.statsGrid}>

                {/* Circular Chart: Cold Data Ratio */}
                <div className={styles.chartCard} role="button" tabIndex={0}>
                    <h4 className={styles.chartTitle}>Cold Data Ratio</h4>
                    <div
                        className={styles.circularChart}
                        style={{ background: `conic-gradient(var(--color-highlight) ${animate ? degrees : 0}deg, var(--color-surface) 0deg)` }}
                    >
                        <div className={styles.innerCircle}>
                            <span className={styles.percentValue}>{Math.round(coldRatio)}%</span>
                            <span className={styles.percentLabel}>Cold Files</span>
                        </div>
                    </div>
                </div>

                {/* NEW: Storage Health/Efficiency Gauge */}
                <div className={styles.chartCard} role="button" tabIndex={0}>
                    <h4 className={styles.chartTitle}>Storage Efficiency</h4>
                    <div className={styles.efficiencyGauge}>
                        <div
                            className={styles.gaugeFill}
                            style={{ transform: `rotate(${animate ? gaugeRotation : 0}deg)` }}
                        />
                        <div className={styles.gaugeOverlay}>
                            <span className={styles.efficiencyValue}>{efficiencyScore}</span>
                        </div>
                    </div>
                    <div className={styles.statDetail} style={{ border: 'none', marginTop: 0 }}>
                        <span className={styles.percentLabel}>Based on active file usage</span>
                    </div>
                </div>

                {/* Bar Charts: File Categories - Now Full Width */}
                <div className={`${styles.categoryCard} ${styles.fullWidth}`} role="button" tabIndex={0}>
                    <h4 className={styles.chartTitle}>File Categories</h4>
                    <ul className={styles.categoryList}>
                        {Object.entries(categoryBreakdown).map(([cat, count], index) => {
                            const percentage = (count / maxCategoryCount) * 100;
                            return (
                                <li key={cat} className={styles.categoryItem} style={{ transitionDelay: `${index * 100}ms` }}>
                                    <div className={styles.categoryHeader}>
                                        <span>{cat}</span>
                                        <span>{count}</span>
                                    </div>
                                    <div className={styles.progressBarTrack}>
                                        <div
                                            className={styles.progressBarFill}
                                            style={{
                                                width: animate ? `${percentage}%` : '0%',
                                                backgroundColor: `hsl(150, 20%, ${30 + (index * 10)}%)` // Varying shades of green
                                            }}
                                        />
                                    </div>
                                </li>
                            );
                        })}
                    </ul>
                </div>
            </div>

            {/* Actionable Recommendations */}
            <h3 className={styles.recommendationsTitle}>Recommended Actions</h3>
            <div className={styles.recGrid}>
                {recommendations.map((rec, idx) => (
                    <div key={idx} className={styles.recCard} role="button" tabIndex={0}>
                        {/* Split text by newlines or render as single bullet if just one line */}
                        <ul className={styles.recList}>
                            {rec.split('. ').filter(Boolean).map((point, pIdx) => (
                                <li key={pIdx}>{point}{!point.endsWith('.') && '.'}</li>
                            ))}
                        </ul>
                    </div>
                ))}
            </div>
        </section>
    );
}

// Simple internal SVG component to avoid external dependencies
function LeafIcon({ className }) {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
        >
            <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.77 10-10 10Z" />
            <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12" />
        </svg>
    );
}
