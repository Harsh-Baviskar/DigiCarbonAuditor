/**
 * Mock API for Digital Carbon Auditor
 * Replace with real backend calls (e.g., fetch('/api/scan', {...})) when backend is ready.
 */

const MOCK_SCAN_DELAY_MS = 2500;

const mockScanResult = {
  summary: {
    totalFiles: 1247,
    totalStorageBytes: 15842971648,
    duplicateFilesCount: 89,
    wastedStorageBytes: 2147483648,
  },
  /** Top contributors to storage and duplication — for insight-oriented UI. */
  topContributors: {
    byFileType: [
      { type: '.xlsx', count: 342, sizeBytes: 5368709120, percentOfTotal: 33.9 },
      { type: '.pdf', count: 289, sizeBytes: 4284481536, percentOfTotal: 27.1 },
      { type: '.mp4', count: 45, sizeBytes: 2147483648, percentOfTotal: 13.6 },
      { type: '.zip', count: 78, sizeBytes: 1610612736, percentOfTotal: 10.2 },
      { type: '.png', count: 312, sizeBytes: 1073741824, percentOfTotal: 6.8 },
      { type: '.ini', count: 156, sizeBytes: 524288000, percentOfTotal: 3.3 },
    ],
    byFolderDuplication: [
      { folder: 'E:\\Archive\\2023', duplicateCount: 28, wastedBytes: 734003200 },
      { folder: 'F:\\Shared', duplicateCount: 18, wastedBytes: 524288000 },
      { folder: 'C:\\Temp', duplicateCount: 24, wastedBytes: 314572800 },
      { folder: 'D:\\Backup', duplicateCount: 12, wastedBytes: 262144000 },
      { folder: 'C:\\Downloads', duplicateCount: 7, wastedBytes: 314572800 },
    ],
  },
  /** Suggested actions ranked by impact — for decision support. */
  suggestedActions: [
    {
      id: '1',
      action: 'Remove duplicate Excel files in Downloads and Desktop',
      impactBytes: 52428800,
      impactLabel: '50 MB',
      type: 'safe',
      reason: 'Exact duplicates (hash match). Safe to remove one copy.',
    },
    {
      id: '2',
      action: 'Deduplicate config.ini across E:\\Archive\\2023',
      impactBytes: 11534336,
      impactLabel: '11 MB',
      type: 'safe',
      reason: '12 identical config files. Keep one, remove 11.',
    },
    {
      id: '3',
      action: 'Review PDF reports in C:\\Projects\\archive vs D:\\Shared',
      impactBytes: 1048576,
      impactLabel: '1 MB',
      type: 'safe',
      reason: 'Exact duplicates. Consolidate to single location.',
    },
    {
      id: '4',
      action: 'Archive or delete old backups in D:\\Backup',
      impactBytes: 262144000,
      impactLabel: '250 MB',
      type: 'review_needed',
      reason: 'Potential redundant backups. Verify retention policy.',
    },
  ],
  duplicateGroups: [
    {
      hash: 'sha256:a1b2c3d4e5f6...',
      fileSizeBytes: 1048576,
      duplicateCount: 3,
      paths: [
        'C:\\Users\\Public\\Documents\\backup\\report_2024.pdf',
        'C:\\Projects\\archive\\report_2024.pdf',
        'D:\\Shared\\reports\\report_2024.pdf',
      ],
    },
    {
      hash: 'sha256:f6e5d4c3b2a1...',
      fileSizeBytes: 52428800,
      duplicateCount: 2,
      paths: [
        'C:\\Downloads\\dataset.xlsx',
        'C:\\Users\\Admin\\Desktop\\dataset_copy.xlsx',
      ],
    },
    {
      hash: 'sha256:9f8e7d6c5b4a...',
      fileSizeBytes: 1024,
      duplicateCount: 12,
      paths: [
        'C:\\Temp\\config.ini',
        'C:\\Temp\\old\\config.ini',
        'D:\\Backup\\config.ini',
        'E:\\Archive\\2023\\config.ini',
        'E:\\Archive\\2023\\Q1\\config.ini',
        'E:\\Archive\\2023\\Q2\\config.ini',
        'E:\\Archive\\2023\\Q3\\config.ini',
        'E:\\Archive\\2023\\Q4\\config.ini',
        'F:\\Shared\\config.ini',
        'F:\\Shared\\dev\\config.ini',
        'F:\\Shared\\prod\\config.ini',
        'F:\\Shared\\staging\\config.ini',
      ],
    },
  ],
};

/**
 * Simulates scanning a directory. Returns mock scan result after delay.
 * @param {string} path - Directory path to scan
 * @returns {Promise<object>} Scan result
 */
export async function startScan(path) {
  await new Promise((resolve) => setTimeout(resolve, MOCK_SCAN_DELAY_MS));
  return {
    success: true,
    scannedPath: path,
    ...mockScanResult,
  };
}
