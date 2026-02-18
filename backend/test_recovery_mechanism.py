"""
Test suite for safe deletion recovery mechanism

Validates:
1. Files are moved to recovery (not deleted)
2. Metadata is created and readable
3. Recovery bin can be listed
4. Expired files are cleaned up
5. Error handling is robust
"""

import os
import sys
import json
import tempfile
import shutil
from datetime import datetime, timedelta

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from wasteDetect import (
    delete_duplicate_files,
    get_recovery_files,
    _clean_expired_recovery_files,
    RECOVERY_DIR,
    RECOVERY_METADATA_DIR,
    RECOVERY_RETENTION_DAYS
)


def cleanup_test_recovery():
    """Clean up recovery directories for testing."""
    try:
        if os.path.exists(RECOVERY_DIR):
            shutil.rmtree(RECOVERY_DIR)
    except Exception:
        pass


def test_basic_recovery():
    """Test that files are moved to recovery instead of deleted."""
    print("\n" + "="*70)
    print("TEST 1: Basic File Recovery")
    print("="*70)
    
    cleanup_test_recovery()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        test_files = []
        for i in range(2):
            file_path = os.path.join(tmpdir, f"test_file_{i}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Test file {i} content\n" * 100)
            test_files.append(file_path)
        
        print(f"\nCreated test files:")
        for f in test_files:
            print(f"  {f}")
        
        # Verify files exist
        for f in test_files:
            assert os.path.exists(f), f"File not created: {f}"
        
        # Delete/recover files
        result = delete_duplicate_files(test_files)
        
        print(f"\nRecovery Results:")
        print(f"  Status: {result['status']}")
        print(f"  Recovered: {result['recoveredCount']}")
        print(f"  Failed: {result['failedCount']}")
        
        # Verify original files NO LONGER EXIST
        for f in test_files:
            assert not os.path.exists(f), f"File still exists (should be recovered): {f}"
        
        # Verify files are in recovery bin
        recovery_files = get_recovery_files()
        assert len(recovery_files) == 2, f"Expected 2 files in recovery, got {len(recovery_files)}"
        
        print(f"\nRecovery Bin Contents:")
        print(f"  Files: {len(recovery_files)}")
        for rf in recovery_files:
            print(f"    - {rf['original_path']}")
            print(f"      Recovered as: {os.path.basename(rf['recovery_path'])}")
            print(f"      Size: {rf['file_size_bytes']} bytes")
        
        print(f"\n[PASS] Files successfully moved to recovery")
        print(f"   Original files removed: {result['recoveredCount']}")
        print(f"   Recovery bin active: {len(recovery_files)} files")


def test_metadata_creation():
    """Test that metadata files are created and readable."""
    print("\n" + "="*70)
    print("TEST 2: Metadata Creation & Auditability")
    print("="*70)
    
    cleanup_test_recovery()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create and recover a file
        test_file = os.path.join(tmpdir, "metadata_test.txt")
        with open(test_file, 'w') as f:
            f.write("Test content for metadata" * 100)
        
        file_size = os.path.getsize(test_file)
        
        result = delete_duplicate_files([test_file])
        
        # Verify metadata directory exists
        assert os.path.exists(RECOVERY_METADATA_DIR), \
            "Metadata directory not created"
        
        # Verify metadata files exist
        metadata_files = [f for f in os.listdir(RECOVERY_METADATA_DIR) if f.endswith('.json')]
        assert len(metadata_files) == 1, \
            f"Expected 1 metadata file, found {len(metadata_files)}"
        
        # Read and validate metadata
        metadata_path = os.path.join(RECOVERY_METADATA_DIR, metadata_files[0])
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        print(f"\nMetadata Contents:")
        print(f"  Original Path: {metadata['original_path']}")
        print(f"  Recovery Path: {metadata['recovery_path']}")
        print(f"  Recovered At: {metadata['recovered_at']}")
        print(f"  Expires At: {metadata['expires_at']}")
        print(f"  File Size: {metadata['file_size_bytes']} bytes")
        
        # Verify metadata fields
        assert 'original_path' in metadata, "Missing original_path"
        assert 'recovery_path' in metadata, "Missing recovery_path"
        assert 'recovered_at' in metadata, "Missing recovered_at"
        assert 'expires_at' in metadata, "Missing expires_at"
        assert 'file_size_bytes' in metadata, "Missing file_size_bytes"
        
        # Verify timestamps are ISO format
        recovered_dt = datetime.fromisoformat(metadata['recovered_at'])
        expires_dt = datetime.fromisoformat(metadata['expires_at'])
        
        # Verify expiry is ~7 days from now
        days_until_expiry = (expires_dt - recovered_dt).days
        assert days_until_expiry >= 6 and days_until_expiry <= 8, \
            f"Expiry should be ~7 days, got {days_until_expiry}"
        
        print(f"\n[PASS] Metadata created and auditable")
        print(f"   Expiry window: {days_until_expiry} days")


def test_recovery_listing():
    """Test that recovery bin can be listed."""
    print("\n" + "="*70)
    print("TEST 3: Recovery Bin Listing")
    print("="*70)
    
    cleanup_test_recovery()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create multiple files
        test_files = []
        for i in range(3):
            file_path = os.path.join(tmpdir, f"file_{i}.txt")
            with open(file_path, 'w') as f:
                size = (i + 1) * 1024 * 1024  # 1MB, 2MB, 3MB
                f.write("x" * size)
            test_files.append(file_path)
        
        # Recover all files
        delete_duplicate_files(test_files)
        
        # List recovery bin
        recovery_files = get_recovery_files()
        
        print(f"\nRecovery Bin Summary:")
        print(f"  Total Files: {len(recovery_files)}")
        
        total_size = sum(f['file_size_bytes'] for f in recovery_files)
        print(f"  Total Size: {total_size} bytes")
        
        active_files = [f for f in recovery_files if not f.get('is_expired', False)]
        print(f"  Active Files: {len(active_files)}")
        
        # List each file
        print(f"\nRecovered Files:")
        for rf in recovery_files:
            status = "ACTIVE" if not rf.get('is_expired') else "EXPIRED"
            print(f"  - {os.path.basename(rf.get('original_path', 'unknown'))}")
            print(f"    Size: {rf['file_size_bytes']} bytes")
            print(f"    Status: {status}")
        
        assert len(recovery_files) == 3, \
            f"Expected 3 files in recovery, got {len(recovery_files)}"
        
        print(f"\n[PASS] Recovery bin listing works")
        print(f"   Retrieved {len(recovery_files)} files from recovery")


def test_cleanup():
    """Test that expired files are cleaned up."""
    print("\n" + "="*70)
    print("TEST 4: Expired File Cleanup")
    print("="*70)
    
    cleanup_test_recovery()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create and recover a file
        test_file = os.path.join(tmpdir, "expire_test.txt")
        with open(test_file, 'w') as f:
            f.write("Test file for expiry\n" * 100)
        
        delete_duplicate_files([test_file])
        
        # Verify file is in recovery
        recovery_files = get_recovery_files()
        assert len(recovery_files) == 1, "File should be in recovery"
        
        # Manually set expiry to past date
        metadata_path = None
        for f in os.listdir(RECOVERY_METADATA_DIR):
            if f.endswith('.json'):
                metadata_path = os.path.join(RECOVERY_METADATA_DIR, f)
                break
        
        if metadata_path:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Move expiry to past
            past_date = (datetime.now() - timedelta(days=8)).isoformat()
            metadata['expires_at'] = past_date
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)
        
        # Cleanup should remove expired file
        cleaned = _clean_expired_recovery_files()
        
        print(f"\nCleanup Results:")
        print(f"  Files cleaned: {cleaned}")
        
        # Verify file was removed
        recovery_files = get_recovery_files()
        assert len(recovery_files) == 0, \
            "Expired file should be cleaned up"
        
        print(f"\n[PASS] Expired files cleaned up")
        print(f"   Cleaned {cleaned} expired file(s)")


def test_error_handling():
    """Test error handling for various failure scenarios."""
    print("\n" + "="*70)
    print("TEST 5: Error Handling")
    print("="*70)
    
    cleanup_test_recovery()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test 1: Non-existent file
        result = delete_duplicate_files(["/nonexistent/file.txt"])
        
        print(f"\nNon-existent File Test:")
        print(f"  Status: {result['status']}")
        print(f"  Failed: {result['failedCount']}")
        
        assert result['failedCount'] > 0, "Should count non-existent as failure"
        
        # Test 2: Empty list
        result = delete_duplicate_files([])
        
        print(f"\nEmpty List Test:")
        print(f"  Status: {result['status']}")
        print(f"  Message: {result.get('message', 'N/A')}")
        
        assert result['status'] == 'warning', "Empty list should be warning"
        
        # Test 3: Symlink rejection
        try:
            symlink_path = os.path.join(tmpdir, "test_symlink")
            target = os.path.join(tmpdir, "target.txt")
            with open(target, 'w') as f:
                f.write("target")
            
            os.symlink(target, symlink_path)
            
            result = delete_duplicate_files([symlink_path])
            
            print(f"\nSymlink Test:")
            print(f"  Status: {result['status']}")
            print(f"  Blocked: {result.get('failedCount', 0) > 0}")
            
            assert result['failedCount'] > 0, "Symlink should be blocked"
        except (OSError, NotImplementedError):
            print(f"\nSymlink Test: SKIPPED (symlinks not supported on this system)")
        
        print(f"\n[PASS] Error handling is robust")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SAFE DELETION RECOVERY MECHANISM TEST SUITE")
    print("="*70)
    
    try:
        test_basic_recovery()
        test_metadata_creation()
        test_recovery_listing()
        test_cleanup()
        test_error_handling()
        
        cleanup_test_recovery()
        
        print("\n" + "="*70)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("="*70)
        print("\nRecovery mechanism validation complete:")
        print("  [OK] Files moved to recovery (not deleted)")
        print("  [OK] Metadata created and auditable")
        print("  [OK] Recovery bin can be listed")
        print("  [OK] Expired files cleaned up")
        print("  [OK] Error handling is robust")
        print("="*70 + "\n")
        
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {str(e)}")
        cleanup_test_recovery()
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        cleanup_test_recovery()
        sys.exit(1)
