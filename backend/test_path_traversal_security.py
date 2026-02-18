"""
Test suite for path traversal vulnerability fixes in wasteDetect.py

Validates security protections:
1. Symlinks are rejected during scanning
2. Directory traversal attempts are blocked
3. Files cannot escape the base scan directory
4. errorCount is incremented for unsafe paths
"""

import os
import tempfile
import shutil
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from wasteDetect import scan_folder_for_waste, is_safe_path


def test_symlink_file_protection():
    """
    Test that symlinks to files are rejected during scanning.
    
    Setup:
    - Create a test directory with a regular file
    - Create a symlink pointing to that file
    - Scan the directory
    
    Expected:
    - Regular file is scanned normally
    - Symlink is skipped (errorCount incremented)
    """
    print("\n" + "="*70)
    print("TEST 1: Symlink File Protection")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a real file
        real_file = os.path.join(tmpdir, "real_file.txt")
        with open(real_file, 'w') as f:
            f.write("This is a real file" * 100)
        
        # Create a symlink to the file
        symlink_file = os.path.join(tmpdir, "symlink_file.txt")
        try:
            os.symlink(real_file, symlink_file)
            symlink_supported = True
        except (OSError, NotImplementedError):
            print("⚠️  Symlinks not supported on this system (likely Windows)")
            print("   Run elevated/admin command prompt to enable symlink support")
            return
        
        # Scan the directory
        result = scan_folder_for_waste(tmpdir)
        
        # Verify results
        print(f"\nScan Results:")
        print(f"  Status: {result['scanStatus']}")
        print(f"  Total Files Scanned: {result['summary']['totalFiles']}")
        print(f"  Errors (includes symlinks): {result['summary']['errorCount']}")
        
        # The real file should be counted, symlink should increment errorCount
        assert result['summary']['totalFiles'] == 1, \
            f"Expected 1 real file, got {result['summary']['totalFiles']}"
        assert result['summary']['errorCount'] >= 1, \
            f"Expected errorCount >= 1 (for symlink), got {result['summary']['errorCount']}"
        
        print(f"\n✅ PASSED: Symlink was properly rejected")
        print(f"   Real file counted: {result['summary']['totalFiles']}")
        print(f"   Symlink rejected (errorCount++): {result['summary']['errorCount']}")


def test_symlink_directory_protection():
    """
    Test that symlink directories are not traversed.
    
    Setup:
    - Create a directory structure with normal files
    - Create another directory with a file
    - Create a symlink pointing to that directory
    - Scan the first directory
    
    Expected:
    - Only real files in base directory are scanned
    - Symlink directory is skipped (not traversed)
    """
    print("\n" + "="*70)
    print("TEST 2: Symlink Directory Protection")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create main directory with a file
        main_dir = os.path.join(tmpdir, "main_dir")
        os.makedirs(main_dir)
        
        real_file = os.path.join(main_dir, "real_file.txt")
        with open(real_file, 'w') as f:
            f.write("Real file in main directory" * 100)
        
        # Create another directory with a file
        external_dir = os.path.join(tmpdir, "external_dir")
        os.makedirs(external_dir)
        
        external_file = os.path.join(external_dir, "external_file.txt")
        with open(external_file, 'w') as f:
            f.write("This is an external file" * 100)
        
        # Create symlink directory pointing to external_dir
        symlink_dir = os.path.join(main_dir, "symlink_dir")
        try:
            os.symlink(external_dir, symlink_dir)
            symlink_supported = True
        except (OSError, NotImplementedError):
            print("⚠️  Symlinks not supported on this system")
            return
        
        # Scan main_dir
        result = scan_folder_for_waste(main_dir)
        
        print(f"\nScan Results:")
        print(f"  Status: {result['scanStatus']}")
        print(f"  Total Files Scanned: {result['summary']['totalFiles']}")
        print(f"  Errors: {result['summary']['errorCount']}")
        
        # Should only scan the real file, not the external file via symlink
        assert result['summary']['totalFiles'] == 1, \
            f"Expected 1 file (real_file.txt only), got {result['summary']['totalFiles']}"
        
        print(f"\n✅ PASSED: Symlink directory was not traversed")
        print(f"   Only scanned real files: {result['summary']['totalFiles']}")
        print(f"   External files via symlink were properly blocked")


def test_path_traversal_protection():
    """
    Test that directory traversal attempts are blocked.
    
    Setup:
    - Create nested directory structure
    - Create a file outside the scan directory
    - Attempt to scan with ../ path traversal
    
    Expected:
    - Cannot traverse outside base directory
    - Path validation rejects attempts to escape
    """
    print("\n" + "="*70)
    print("TEST 3: Path Traversal Protection (../ escape attempts)")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test structure
        scan_dir = os.path.join(tmpdir, "scan_me")
        os.makedirs(scan_dir)
        
        outside_dir = os.path.join(tmpdir, "outside")
        os.makedirs(outside_dir)
        
        # Files
        scan_file = os.path.join(scan_dir, "scan_file.txt")
        with open(scan_file, 'w') as f:
            f.write("File in scan directory" * 100)
        
        outside_file = os.path.join(outside_dir, "outside_file.txt")
        with open(outside_file, 'w') as f:
            f.write("Outside file" * 100)
        
        # Test is_safe_path function directly
        base_real = os.path.realpath(scan_dir)
        
        # Safe path: inside directory
        assert is_safe_path(scan_file, base_real), \
            "Real file inside directory should be safe"
        
        # Unsafe path: outside directory
        assert not is_safe_path(outside_file, base_real), \
            "File outside directory should be blocked"
        
        # Unsafe path: ../ traversal
        traversal_attempt = os.path.join(scan_dir, "..", "outside", "file.txt")
        assert not is_safe_path(os.path.realpath(traversal_attempt), base_real), \
            "Directory traversal should be blocked"
        
        print(f"\n✅ PASSED: Path traversal attempts blocked")
        print(f"   Safe path (inside): ALLOWED ✓")
        print(f"   Unsafe path (outside): BLOCKED ✓")
        print(f"   Traversal attempt (../): BLOCKED ✓")


def test_error_counting():
    """
    Test that unsafe paths increment errorCount.
    
    Setup:
    - Create directory with mix of real files and symlinks
    - Scan the directory
    
    Expected:
    - Real files are scanned successfully
    - Symlinks increment errorCount
    - Results show proper count
    """
    print("\n" + "="*70)
    print("TEST 4: Error Counting for Unsafe Paths")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create real files
        for i in range(3):
            with open(os.path.join(tmpdir, f"real_{i}.txt"), 'w') as f:
                f.write(f"Real file {i}" * 100)
        
        # Create symlinks
        target_file = os.path.join(tmpdir, "target.txt")
        with open(target_file, 'w') as f:
            f.write("Target for symlinks" * 100)
        
        try:
            for i in range(2):
                symlink_path = os.path.join(tmpdir, f"symlink_{i}.txt")
                os.symlink(target_file, symlink_path)
            symlink_supported = True
        except (OSError, NotImplementedError):
            print("⚠️  Symlinks not supported on this system")
            return
        
        # Scan
        result = scan_folder_for_waste(tmpdir)
        
        print(f"\nScan Results:")
        print(f"  Total Files: {result['summary']['totalFiles']}")
        print(f"  Error Count: {result['summary']['errorCount']}")
        
        # 4 real files (3 + target), errors = 2 symlinks
        # 5 total files (4 real + 1 target)
        expected_real = 4
        expected_errors = 2
        
        assert result['summary']['totalFiles'] == expected_real, \
            f"Expected {expected_real} real files, got {result['summary']['totalFiles']}"
        assert result['summary']['errorCount'] >= expected_errors, \
            f"Expected errorCount >= {expected_errors}, got {result['summary']['errorCount']}"
        
        print(f"\n✅ PASSED: Unsafe paths properly counted in errorCount")
        print(f"   Real files scanned: {result['summary']['totalFiles']}")
        print(f"   Unsafe paths rejected: {result['summary']['errorCount']}")


def test_performance_maintained():
    """
    Test that security checks don't significantly impact performance.
    
    Setup:
    - Create many small files in a directory
    - Scan the directory
    - Time the scan
    
    Expected:
    - Scan completes successfully
    - Performance is reasonable (< 5 seconds for 100 files)
    """
    print("\n" + "="*70)
    print("TEST 5: Performance Not Degraded")
    print("="*70)
    
    import time
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create 100 small files
        print("\n  Creating test files...")
        for i in range(100):
            with open(os.path.join(tmpdir, f"file_{i:03d}.txt"), 'w') as f:
                f.write(f"Test file {i}" * 10)
        
        # Time the scan
        print("  Scanning directory...")
        start = time.time()
        result = scan_folder_for_waste(tmpdir)
        duration = time.time() - start
        
        print(f"\nScan Results:")
        print(f"  Files scanned: {result['summary']['totalFiles']}")
        print(f"  Duration: {duration:.3f} seconds")
        print(f"  Files per second: {result['summary']['totalFiles'] / duration:.0f}")
        
        assert result['summary']['totalFiles'] == 100, \
            f"Expected 100 files, got {result['summary']['totalFiles']}"
        assert duration < 5.0, \
            f"Scan too slow: {duration:.3f}s (should be < 5s)"
        
        print(f"\n✅ PASSED: Performance is acceptable")
        print(f"   100 files scanned in {duration:.3f}s")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PATH TRAVERSAL SECURITY TEST SUITE")
    print("Testing: wasteDetect.py security hardening")
    print("="*70)
    
    try:
        test_path_traversal_protection()
        test_error_counting()
        test_symlink_file_protection()
        test_symlink_directory_protection()
        test_performance_maintained()
        
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED!")
        print("="*70)
        print("\nSecurity improvements verified:")
        print("  ✅ Path traversal attempts blocked")
        print("  ✅ Symlinks properly rejected")
        print("  ✅ Error counting works correctly")
        print("  ✅ Performance maintained")
        print("="*70 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
