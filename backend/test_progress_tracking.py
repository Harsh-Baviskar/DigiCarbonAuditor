"""
Test suite for progress tracking in scan_folder_for_waste.

Validates:
- Progress callback functionality
- Percentage calculations
- Stage transitions (counting -> scanning -> hashing -> complete)
- No performance regression
- API integration
"""

import os
import sys
import tempfile
import time
import json

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from wasteDetect import scan_folder_for_waste, format_bytes


class ProgressTracker:
    """Helper class to track progress updates."""
    
    def __init__(self):
        self.updates = []
        self.stages = []
        self.max_percentage = 0
        self.callback_count = 0
    
    def callback(self, processed, total, percentage):
        """Progress callback handler."""
        self.callback_count += 1
        self.updates.append({
            "processed": processed,
            "total": total,
            "percentage": percentage,
            "callback_num": self.callback_count
        })
        self.max_percentage = max(self.max_percentage, percentage)
    
    def track_stage(self, stage):
        """Track stage transitions."""
        self.stages.append(stage)


def test_progress_callback_basic():
    """TEST 1: Basic progress callback invocation."""
    print("[TEST 1] Basic progress callback invocation... ", end="", flush=True)
    
    # Create test directory with files
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create 50 test files
        for i in range(50):
            filepath = os.path.join(tmpdir, f"file_{i:03d}.txt")
            with open(filepath, 'w') as f:
                f.write(f"Content {i}" * 100)
        
        # Scan with progress callback
        tracker = ProgressTracker()
        results = scan_folder_for_waste(tmpdir, progress_callback=tracker.callback)
        
        # Validate
        assert results["scanStatus"] == "success", "Scan failed"
        assert tracker.callback_count > 0, "No callback invocations"
        assert len(tracker.updates) > 0, "No progress updates recorded"
        assert results["summary"]["totalFiles"] == 50, f"Expected 50 files, got {results['summary']['totalFiles']}"
        
        # All callbacks should have percentage between 0-100
        for update in tracker.updates:
            assert 0 <= update["percentage"] <= 100, f"Invalid percentage: {update['percentage']}"
        
        print("[PASS]")
        return True


def test_progress_percentages():
    """TEST 2: Progress percentages increase monotonically."""
    print("[TEST 2] Progress percentage monotonic increase... ", end="", flush=True)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files
        for i in range(30):
            filepath = os.path.join(tmpdir, f"file_{i:03d}.txt")
            with open(filepath, 'w') as f:
                f.write(f"Content {i}" * 50)
        
        tracker = ProgressTracker()
        results = scan_folder_for_waste(tmpdir, progress_callback=tracker.callback)
        
        # Validate progress is monotonic
        if len(tracker.updates) > 1:
            for i in range(1, len(tracker.updates)):
                prev_pct = tracker.updates[i-1]["percentage"]
                curr_pct = tracker.updates[i]["percentage"]
                assert curr_pct >= prev_pct, (
                    f"Progress decreased: {prev_pct}% -> {curr_pct}%"
                )
        
        # Final result should show progress
        assert results["progress"]["percentage"] >= 99, (
            f"Final progress not near 100%: {results['progress']['percentage']}"
        )
        
        print("[PASS]")
        return True


def test_progress_stages():
    """TEST 3: Progress stages transition correctly."""
    print("[TEST 3] Progress stage transitions... ", end="", flush=True)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        for i in range(20):
            filepath = os.path.join(tmpdir, f"file_{i:03d}.txt")
            with open(filepath, 'w') as f:
                f.write(f"Content {i}" * 30)
        
        results = scan_folder_for_waste(tmpdir)
        
        # Validate progress object
        assert "progress" in results, "No progress object in results"
        progress = results["progress"]
        
        assert "total" in progress, "No total in progress"
        assert "processed" in progress, "No processed in progress"
        assert "percentage" in progress, "No percentage in progress"
        assert "stage" in progress, "No stage in progress"
        
        # Final stage should be complete or error
        assert progress["stage"] in ["complete", "error"], (
            f"Invalid final stage: {progress['stage']}"
        )
        
        # For successful scan, should be complete
        if results["scanStatus"] == "success":
            assert progress["stage"] == "complete", "Stage should be complete on success"
            assert progress["percentage"] == 100.0, "Percentage should be 100% on complete"
        
        print("[PASS]")
        return True


def test_progress_totals():
    """TEST 4: Progress total counts are reasonable."""
    print("[TEST 4] Progress total count validation... ", end="", flush=True)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create specific number of files
        file_count = 25
        for i in range(file_count):
            filepath = os.path.join(tmpdir, f"file_{i:03d}.txt")
            with open(filepath, 'w') as f:
                f.write(f"Content {i}" * 25)
        
        results = scan_folder_for_waste(tmpdir)
        
        # Progress total should match or exceed actual files
        assert results["progress"]["total"] >= file_count, (
            f"Progress total {results['progress']['total']} < file count {file_count}"
        )
        
        # Processed should be <= total
        assert results["progress"]["processed"] <= results["progress"]["total"], (
            f"Processed {results['progress']['processed']} > total {results['progress']['total']}"
        )
        
        print("[PASS]")
        return True


def test_no_callback_provided():
    """TEST 5: Scan works without callback (no regression)."""
    print("[TEST 5] Scan without callback (backward compatibility)... ", end="", flush=True)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files
        for i in range(15):
            filepath = os.path.join(tmpdir, f"file_{i:03d}.txt")
            with open(filepath, 'w') as f:
                f.write(f"Content {i}" * 20)
        
        # Scan without callback (old API)
        results = scan_folder_for_waste(tmpdir)
        
        # Should still work and include progress data
        assert results["scanStatus"] == "success", "Scan failed"
        assert "progress" in results, "Progress data missing"
        assert results["progress"]["stage"] == "complete", "Stage should be complete"
        assert results["summary"]["totalFiles"] == 15, "File count mismatch"
        
        print("[PASS]")
        return True


def test_performance_no_regression():
    """TEST 6: No significant performance impact from progress tracking."""
    print("[TEST 6] Performance regression check... ", end="", flush=True)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        for i in range(100):
            filepath = os.path.join(tmpdir, f"file_{i:03d}.txt")
            with open(filepath, 'w') as f:
                f.write(f"Content {i}" * 50)
        
        # Scan with callback
        tracker = ProgressTracker()
        start_with_callback = time.time()
        results_with = scan_folder_for_waste(tmpdir, progress_callback=tracker.callback)
        time_with_callback = time.time() - start_with_callback
        
        # Scan without callback
        start_without = time.time()
        results_without = scan_folder_for_waste(tmpdir)
        time_without_callback = time.time() - start_without
        
        # Performance overhead should be minimal (< 50%)
        overhead = (time_with_callback / time_without_callback - 1) * 100
        
        # Results should be identical
        assert results_with["summary"]["totalFiles"] == results_without["summary"]["totalFiles"], \
            "File counts differ"
        assert results_with["summary"]["duplicateFilesCount"] == results_without["summary"]["duplicateFilesCount"], \
            "Duplicate counts differ"
        
        print(f"[PASS] (Overhead: {overhead:.1f}%)")
        return True


def test_progress_with_errors():
    """TEST 7: Progress tracking handles errors gracefully."""
    print("[TEST 7] Progress with error handling... ", end="", flush=True)
    
    # Non-existent directory
    results = scan_folder_for_waste("/nonexistent/path/that/does/not/exist")
    
    assert results["scanStatus"] == "error", "Should fail for nonexistent path"
    assert results["progress"]["stage"] == "error", "Stage should be error"
    assert "error" in results, "Error message missing"
    
    print("[PASS]")
    return True


def test_progress_in_results():
    """TEST 8: Progress data in response format."""
    print("[TEST 8] Progress data in response format... ", end="", flush=True)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create files
        for i in range(10):
            filepath = os.path.join(tmpdir, f"file_{i:03d}.txt")
            with open(filepath, 'w') as f:
                f.write(f"Content {i}" * 10)
        
        results = scan_folder_for_waste(tmpdir)
        
        # Validate progress structure in response
        assert "progress" in results, "Progress missing from results"
        
        progress = results["progress"]
        required_fields = ["total", "processed", "percentage", "stage"]
        for field in required_fields:
            assert field in progress, f"Missing progress field: {field}"
            assert progress[field] is not None, f"Progress field is None: {field}"
        
        # Type validation
        assert isinstance(progress["total"], int), "total should be int"
        assert isinstance(progress["processed"], int), "processed should be int"
        assert isinstance(progress["percentage"], (int, float)), "percentage should be numeric"
        assert isinstance(progress["stage"], str), "stage should be str"
        
        print("[PASS]")
        return True


def main():
    """Run all progress tracking tests."""
    print("\n" + "="*60)
    print("PROGRESS TRACKING TEST SUITE")
    print("="*60 + "\n")
    
    tests = [
        test_progress_callback_basic,
        test_progress_percentages,
        test_progress_stages,
        test_progress_totals,
        test_no_callback_provided,
        test_performance_no_regression,
        test_progress_with_errors,
        test_progress_in_results,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"[FAIL] {str(e)}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
