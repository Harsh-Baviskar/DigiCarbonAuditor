"""
Test the wasteDetect module to ensure it works properly
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.wasteDetect import scan_folder_for_waste, format_bytes

def test_waste_detection():
    """Test the waste detector with the current directory"""
    print("Testing Waste Detection Module")
    print("=" * 50)
    
    # Test with current script directory (small test)
    test_path = os.path.dirname(os.path.abspath(__file__))
    print(f"\nScanning test folder: {test_path}")
    print("-" * 50)
    
    result = scan_folder_for_waste(test_path)
    
    print(f"Scan Status: {result['scanStatus']}")
    if result['scanStatus'] == 'error':
        print(f"ERROR: {result.get('error', 'Unknown error')}")
        return False
    
    summary = result['summary']
    print(f"Total Files: {summary['totalFiles']}")
    print(f"Total Storage: {format_bytes(summary['totalSizeBytes'])}")
    print(f"Duplicates Found: {summary['duplicateFilesCount']}")
    print(f"Duplicate Waste: {format_bytes(summary['duplicateSizeBytes'])}")
    print(f"Old Files (>180 days): {summary['oldFilesCount']}")
    print(f"Old Files Waste: {format_bytes(summary['oldFilesSizeBytes'])}")
    print(f"System Files: {summary['systemFilesCount']}")
    print(f"System Files Size: {format_bytes(summary['systemFilesSizeBytes'])}")
    print(f"Errors During Scan: {summary['errorCount']}")
    print(f"\nPotential Waste: {format_bytes(summary['potentialWasteSizeBytes'])}")
    print(f"Waste Percentage: {result['statistics']['wastePercentage']}%")
    print(f"CO2 Savings Potential: {result['statistics']['carbonSaveKgPerYear']} kg/year")
    
    print(f"\nDuplicate Groups: {len(result['duplicateGroups'])}")
    for i, group in enumerate(result['duplicateGroups'][:3], 1):
        print(f"  {i}. {group['hash'][:12]}... - {group['duplicateCount']} copies ({group['totalWasteFormatted']} waste)")
    
    return True

if __name__ == '__main__':
    success = test_waste_detection()
    sys.exit(0 if success else 1)
