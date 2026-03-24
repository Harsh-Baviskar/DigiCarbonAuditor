import { useState } from 'react';
import { formatBytes } from '../../utils/formatters';
import InfoTooltip from '../InfoTooltip/InfoTooltip';
import styles from './WastefulFilesStatistics.module.css';

/**
 * OldFileItem - Display single old/unused file
 */
function OldFileItem({ file }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className={styles.fileItem}>
      <div className={styles.fileHeader} onClick={() => setExpanded(!expanded)}>
        <div className={styles.fileInfo}>
          <span className={styles.fileName}>{file.path.split(/[\\/]/).pop()}</span>
          <span className={styles.fileSize}>{file.sizeFormatted}</span>
          <span className={styles.fileAge}>{file.ageDays} days old</span>
        </div>
        <button className={styles.expandBtn} aria-expanded={expanded}>
          {expanded ? '▼' : '▶'}
        </button>
      </div>
      {expanded && (
        <div className={styles.fileDetails}>
          <p><strong>Full Path:</strong> <code>{file.path}</code></p>
          <p><strong>Last Modified:</strong> {new Date(file.lastModified).toLocaleDateString()}</p>
        </div>
      )}
    </div>
  );
}

/**
 * DuplicateGroupItem - Display duplicate file group with multi-select delete option
 */
function DuplicateGroupItem({ group, onDelete }) {
  const [expanded, setExpanded] = useState(false);
  const [selectedIndices, setSelectedIndices] = useState(new Set());
  const [deleting, setDeleting] = useState(false);

  const toggleSelection = (index) => {
    const newSelection = new Set(selectedIndices);
    if (newSelection.has(index)) {
      newSelection.delete(index);
    } else {
      newSelection.add(index);
    }
    setSelectedIndices(newSelection);
  };

  const selectAll = () => {
    if (selectedIndices.size === group.paths.length) {
      setSelectedIndices(new Set());
    } else {
      setSelectedIndices(new Set(group.paths.map((_, idx) => idx)));
    }
  };

  const handleDelete = async () => {
    if (selectedIndices.size === 0) {
      alert('Please select at least one file to delete');
      return;
    }

    if (selectedIndices.size === group.duplicateCount) {
      alert('You must keep at least one copy of the file');
      return;
    }

    const selectedPaths = Array.from(selectedIndices).map(idx => group.paths[idx]);
    const confirmMsg = `Delete ${selectedIndices.size} file(s) (${group.duplicateCount - selectedIndices.size} will be kept)?`;
    
    if (!window.confirm(confirmMsg)) {
      return;
    }

    setDeleting(true);
    try {
      await onDelete(selectedPaths, group.paths);
      // Reset selection after successful deletion
      setSelectedIndices(new Set());
      setDeleting(false);
    } catch (error) {
      console.error('Delete failed:', error);
      setDeleting(false);
    }
  };

  const selectedCount = selectedIndices.size;
  const keptCount = group.duplicateCount - selectedCount;

  return (
    <div className={styles.duplicateGroup}>
      <div className={styles.groupHeader} onClick={() => setExpanded(!expanded)}>
        <div className={styles.groupInfo}>
          <span className={styles.groupHash}>{group.hash.substring(0, 12)}...</span>
          <span className={styles.fileSize}>{group.sizeFormatted}</span>
          <span className={styles.duplicateCount}>
            {group.duplicateCount} copies (waste: {group.totalWasteFormatted})
          </span>
        </div>
        <button className={styles.expandBtn} aria-expanded={expanded}>
          {expanded ? '▼' : '▶'}
        </button>
      </div>

      {expanded && (
        <div className={styles.groupDetails}>
          <div className={styles.selectionHeader}>
            <button
              className={styles.selectAllBtn}
              onClick={selectAll}
              title={selectedIndices.size === group.paths.length ? 'Deselect all' : 'Select all'}
            >
              {selectedIndices.size === group.paths.length ? 'Deselect All' : 'Select All'}
            </button>
            <span className={styles.selectionInfo}>
              {selectedCount > 0 ? `${selectedCount} selected · ${keptCount} will be kept` : 'No files selected'}
            </span>
          </div>

          <div className={styles.pathsList}>
            {group.paths.map((path, idx) => (
              <label key={idx} className={styles.pathItem}>
                <input
                  type="checkbox"
                  checked={selectedIndices.has(idx)}
                  onChange={() => toggleSelection(idx)}
                  disabled={deleting}
                />
                <span className={styles.pathText}>{path}</span>
              </label>
            ))}
          </div>
          <button
            className={styles.deleteBtn}
            onClick={handleDelete}
            disabled={deleting || selectedCount === 0}
          >
            {deleting ? 'Deleting...' : `Delete ${selectedCount > 0 ? `(${selectedCount})` : ''}`}
          </button>
        </div>
      )}
    </div>
  );
}

/**
 * WastefulFilesStatistics - Show comprehensive waste analysis
 */
export default function WastefulFilesStatistics({ scanData }) {
  const [deletingGroup, setDeletingGroup] = useState(null);

  if (!scanData) {
    return <div className={styles.noData}>No scan data available</div>;
  }

  const {
    summary = {},
    duplicateGroups = [],
    oldFiles = [],
    systemFiles = [],
    statistics = {}
  } = scanData;

  const handleDeleteDuplicates = async (filesToDelete, allPaths) => {
    try {
      const response = await fetch('/waste-detect/delete-duplicates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          files: filesToDelete,
          allPaths: allPaths
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Delete failed');
      }

      const result = await response.json();
      
      // Show detailed deletion results
      if (result.deletedCount > 0) {
        alert(`Successfully deleted ${result.deletedCount} file(s), freeing ${formatBytes(result.deletedSizeBytes)}\n\nDelete operation completed with ${result.failedCount > 0 ? result.failedCount + ' failures' : 'no failures'}`);
      } else if (result.failedCount > 0) {
        alert(`Failed to delete ${result.failedCount} file(s). Check file permissions and try again.`);
      }
    } catch (error) {
      alert(`Error deleting files: ${error.message}`);
      console.error('Delete error details:', error);
    }
  };

  return (
    <div className={styles.container}>
      {/* Summary Cards */}
      <section className={styles.summarySection}>
        <h3>Waste Summary</h3>
        <div className={styles.statsGrid}>
          <div className={styles.statCard}>
            <div className={styles.statLabel}>Total Storage</div>
            <div className={styles.statValue}>{formatBytes(summary.totalSizeBytes)}</div>
            <div className={styles.statSubtext}>{summary.totalFiles} files</div>
          </div>

          <div className={styles.statCard + ' ' + styles.warning}>
            <div className={styles.statLabel}>Potential Waste</div>
            <div className={styles.statValue}>{formatBytes(summary.potentialWasteSizeBytes)}</div>
            <div className={styles.statSubtext}>{statistics.wastePercentage}% of total</div>
          </div>

          <div className={styles.statCard}>
            <div className={styles.statLabel}>Carbon Savings</div>
            <div className={styles.statValue}>{statistics.carbonSaveKgPerYear} kg CO2/yr</div>
            <div className={styles.statSubtext}>If cleaned up</div>
          </div>

          <div className={styles.statCard}>
            <div className={styles.statLabel}>Duplicate Waste</div>
            <div className={styles.statValue}>{formatBytes(summary.duplicateSizeBytes)}</div>
            <div className={styles.statSubtext}>{summary.duplicateFilesCount} extra copies</div>
          </div>

          <div className={styles.statCard}>
            <div className={styles.statLabel}>Old Files</div>
            <div className={styles.statValue}>{formatBytes(summary.oldFilesSizeBytes)}</div>
            <div className={styles.statSubtext}>{summary.oldFilesCount} (&gt;180 days)</div>
          </div>

          <div className={styles.statCard}>
            <div className={styles.statLabel}>System Files</div>
            <div className={styles.statValue}>{formatBytes(summary.systemFilesSizeBytes)}</div>
            <div className={styles.statSubtext}>{summary.systemFilesCount} files</div>
          </div>
        </div>
      </section>

      {/* Duplicate Groups */}
      {duplicateGroups.length > 0 && (
        <section className={styles.section}>
          <h3 className={styles.sectionTitle}>
            Duplicate Files
            <InfoTooltip
              content="Same files with identical content detected. Delete duplicates to keep only 1 copy."
              label="Duplicate detection"
            />
          </h3>
          <div className={styles.sectionContent}>
            {duplicateGroups.map((group, idx) => (
              <DuplicateGroupItem
                key={group.hash}
                group={group}
                onDelete={handleDeleteDuplicates}
              />
            ))}
          </div>
        </section>
      )}

      {/* Old Files */}
      {oldFiles.length > 0 && (
        <section className={styles.section}>
          <h3 className={styles.sectionTitle}>
            Old/Unused Files (&gt;180 days)
            <InfoTooltip
              content="Files not modified or accessed for more than 180 days. Safe to archive or delete."
              label="Old files"
            />
          </h3>
          <div className={styles.sectionContent}>
            <div className={styles.filesList}>
              {oldFiles.slice(0, 50).map((file, idx) => (
                <OldFileItem key={idx} file={file} />
              ))}
            </div>
            {oldFiles.length > 50 && (
              <p className={styles.more}>{oldFiles.length - 50} more old files...</p>
            )}
          </div>
        </section>
      )}

      {/* System Files */}
      {systemFiles.length > 0 && (
        <section className={styles.section}>
          <h3 className={styles.sectionTitle}>
            System Files
            <InfoTooltip
              content="System, cache, and temporary files. Generally safe to ignore or clean via system tools."
              label="System files"
            />
          </h3>
          <div className={styles.sectionContent}>
            <div className={styles.filesList}>
              {systemFiles.slice(0, 50).map((file, idx) => (
                <OldFileItem key={idx} file={file} />
              ))}
            </div>
            {systemFiles.length > 50 && (
              <p className={styles.more}>{systemFiles.length - 50} more system files...</p>
            )}
          </div>
        </section>
      )}
    </div>
  );
}
