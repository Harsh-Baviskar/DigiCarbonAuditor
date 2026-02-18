# Quick Test Case - Path Traversal Protection

Run this simple test to validate the security hardening:

## 1. Basic Symlink Rejection Test (30 seconds)

```bash
# From repository root
cd backend

# Run the security test suite
python test_path_traversal_security.py
```

**Expected Output:**
```
========================== Path Traversal Security Test Suite ==========================
...
🎉 ALL TESTS PASSED!
========================================================================================

Security improvements verified:
  ✅ Path traversal attempts blocked
  ✅ Symlinks properly rejected
  ✅ Error counting works correctly
  ✅ Performance maintained
========================================================================================
```

---

## 2. Manual Test - Symlink Rejection

If you want to manually verify, create this test structure:

```bash
# Create test directory
mkdir test_security
cd test_security

# Create a real file
echo "Real content" > real_file.txt

# Create an external directory (outside scan scope)
mkdir ../external_dir
echo "External content" > ../external_dir/secret.txt

# Create a symlink pointing to external directory
ln -s ../external_dir dangerous_symlink

# Now scan this directory with the app
# File real_file.txt should be scanned
# The symlink should be rejected and counted in errorCount
```

**Expected Behavior:**
- `real_file.txt` is scanned normally
- `dangerous_symlink` is rejected (security validation)
- Result: `errorCount` includes the rejected symlink

---

## 3. Test in Python (Directly)

```python
from app.wasteDetect import scan_folder_for_waste

# Scan a directory containing symlinks
result = scan_folder_for_waste("/path/to/directory")

# Check results
print(f"Files scanned: {result['summary']['totalFiles']}")
print(f"Errors (includes rejected symlinks): {result['summary']['errorCount']}")

# Symlinks will NOT be in totalFiles count
# Symlinks WILL increment errorCount
```

---

## 4. Performance Validation

```python
import time
from app.wasteDetect import scan_folder_for_waste

# Create 100 test files
import tempfile
import os

with tempfile.TemporaryDirectory() as tmpdir:
    for i in range(100):
        with open(os.path.join(tmpdir, f"file_{i}.txt"), 'w') as f:
            f.write(f"Test file {i}\n" * 10)
    
    # Measure scan time
    start = time.time()
    result = scan_folder_for_waste(tmpdir)
    duration = time.time() - start
    
    print(f"Scanned {result['summary']['totalFiles']} files in {duration:.3f}s")
    print(f"Throughput: {result['summary']['totalFiles'] / duration:.0f} files/sec")
    
# Expected: < 1 second for 100 files
```

**Expected Output:**
```
Scanned 100 files in 0.032s
Throughput: 3125 files/sec
```

---

## 5. What's Protected Against

### ✅ Symlink File Escape
```
Before attack: /scan_dir/malicious.lnk -> /windows/system32/critical.sys
After patch: symlink.lnk rejected, not scanned
```

### ✅ Directory Traversal (../)
```
Before attack: /scan_dir/../../etc/passwd accessible
After patch: Traversal blocked by realpath validation  
```

### ✅ Symlink Directory Traversal
```
Before attack: /scan_dir/link_to_etc -> /etc (traversed by os.walk)
After patch: Symlink directory not traversed
```

---

## Key Validation Points

| Check | Command | Expected |
|-------|---------|----------|
| **Code compiles** | `python -m py_compile app/wasteDetect.py` | No errors |
| **Tests pass** | `python test_path_traversal_security.py` | 5/5 tests ✅ |
| **Performance** | Scan 100 files | < 1 second |
| **Error tracking** | Run with symlinks present | errorCount > 0 |

---

## Verification Checklist

- [ ] Code compiles without syntax errors
- [ ] All 5 security tests pass
- [ ] `errorCount` increments when symlinks detected
- [ ] Real files are still scanned normally
- [ ] Performance is reasonable (< 5 seconds per 100 files)
- [ ] Frontend still works (no API changes)
- [ ] Existing functionality unchanged (duplicates, old files still detected)

✅ **All points checked = SECURITY FIX VALIDATED**

---

## Where to Find the Implementation

**Main changes:**
- `backend/app/wasteDetect.py`
  - Lines 31-57: New `is_safe_path()` function
  - Line 155: Base path resolution
  - Lines 167-171: Symlink directory filtering
  - Lines 172-175: Per-file validation
  - Lines 289-294: Deletion safety

**Tests:**
- `backend/test_path_traversal_security.py` (comprehensive test suite)

**Documentation:**
- `SECURITY_HARDENING_SUMMARY.md` (detailed explanation)

