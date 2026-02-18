"""
Centralized Configuration System

Consolidates all magic numbers, constants, and configuration parameters
into a single source of truth. Organized by functional area.

Design:
- Single Config class with nested attributes for different domains
- Type hints for clarity and IDE support
- Comments explaining the purpose and source of each constant
- Easy to customize without code changes
"""

import os
from typing import Set, Dict, Tuple


class Config:
    """
    Centralized configuration for the Digital Carbon Auditor backend.
    All magic numbers and constants are defined here.
    """
    
    # ==================== FILE SYSTEM SCANNING ====================
    
    class FileSystem:
        """Configuration for file system operations."""
        
        # Time constants
        SECONDS_PER_DAY: int = 24 * 3600  # 86400 seconds in a day
        
        # Hash calculation parameters
        HASH_CHUNK_SIZE: int = 65536  # 64KB chunks for file hashing (efficient for most SSDs)
        
        # File size thresholds (in bytes)
        LARGE_FILE_THRESHOLD: int = 500 * 1024 * 1024  # 500MB - skip hashing for performance
        
        # File age thresholds (in days)
        OLD_FILE_AGE_DAYS: int = 180  # Files older than 180 days considered "old"
        OLD_FILE_AGE_SECONDS: int = OLD_FILE_AGE_DAYS * SECONDS_PER_DAY
        
        # Progress tracking
        PROGRESS_UPDATE_FREQUENCY: int = 10  # Update progress every 10 files (minimize overhead)
        
        # Duplicate detection threshold
        MIN_DUPLICATES_IN_GROUP: int = 2  # Only consider as duplicates if 2+ files share hash
        
        # Recovery name collision handling
        MAX_RECOVERY_NAME_ATTEMPTS: int = 100  # Max iterations to find unique recovery filename
        
        # System files to exclude from analysis
        SYSTEM_FILE_EXTENSIONS: Set[str] = {
            '.dll', '.exe', '.sys', '.msi', '.app', '.so', '.o',
            '.lock', '.tmp', '.temp', '.cache', '.log', '.bak',
            '.db', '.sqlite', '.ini', '.cfg', '.conf', '.pdb',
            '.ilk', '.obj', '.lib', '.a', '.so', '.dylib'
        }
        
        # System directories to skip
        SYSTEM_DIRECTORIES: Set[str] = {
            'windows', 'system32', 'system64', 'appdata', 'programfiles',
            'node_modules', '__pycache__', '.git', '.venv', 'venv',
            '.next', 'dist', 'build', '.env', 'node_modules', 'packages',
            'system volume information', 'recycler', 'backup', 'cache'
        }
    
    # ==================== RECOVERY AND RETENTION ====================
    
    class Recovery:
        """Configuration for file recovery and retention."""
        
        # Recovery directory paths
        RECOVERY_DIR: str = "backend/app/deleted_files_recovery"
        RECOVERY_METADATA_DIR: str = os.path.join(RECOVERY_DIR, ".metadata")
        
        # Retention policy (in days)
        RETENTION_DAYS: int = 7  # Hold deleted files for 7 days before auto-cleanup
        
        # Metadata file format
        METADATA_FILE_SUFFIX: str = ".json"  # Metadata files are JSON format
        
        # Recovery filename format: TIMESTAMP_COUNTER_ORIGINAL_NAME
        RECOVERY_FILENAME_SEPARATOR: str = "_"
        RECOVERY_TIMESTAMP_FORMAT: str = "%Y%m%d_%H%M%S"  # e.g., 20260218_123515
    
    # ==================== CARBON CALCULATIONS ====================
    
    class Carbon:
        """Configuration for carbon footprint calculations."""
        
        # Carbon intensity factors
        # Base carbon factor: kg CO2e per GB per year
        # Derived from typical data center PUE (Power Usage Effectiveness) and grid carbon intensity
        CARBON_PER_GB_PER_YEAR: float = 0.2  # kg CO2e per GB annually
        
        # Carbon cost estimation (USD per kg CO2e)
        # Based on social cost of carbon (SCC) estimates
        CARBON_COST_PER_KG: float = 0.15  # dollars per kg CO2e
        
        # Carbon offset equivalent
        CARBON_OFFSET_PER_TREE_YEAR: float = 21  # kg CO2e per mature tree per year
        
        # Energy-to-carbon conversion (for cost calculations)
        GRID_CARBON_INTENSITY_DEFAULT: float = 0.4  # kg CO2/kWh (global average)
    
    # ==================== PERFORMANCE AND LIMITS ====================
    
    class Performance:
        """Configuration for performance parameters."""
        
        # Result limiting for large scans
        MAX_RESULTS_PER_CATEGORY: int = 100  # Limit lists to top 100 per category
        MAX_DUPLICATES_DISPLAYED: int = 100  # Limit duplicate groups displayed
        
        # Timeline analysis parameters
        TIMELINE_BUCKET_SIZE_DAYS: int = 30  # Group files by 30-day buckets
        
        # Batch processing
        BATCH_SIZE_FOR_HASHING: int = 1000  # Process 1000 file sizes before hashing
        
        # Cache and memory limits
        MAX_DUPLICATE_GROUPS_IN_MEMORY: int = 1000  # Stop grouping after 1000 groups
    
    # ==================== STORAGE AND ENCODING ====================
    
    class Storage:
        """Configuration for storage calculation and formatting."""
        
        # Byte unit conversions (for display formatting)
        BYTES_PER_KB: int = 1024
        BYTES_PER_MB: int = 1024 * 1024
        BYTES_PER_GB: int = 1024 * 1024 * 1024
        BYTES_PER_TB: int = 1024 * 1024 * 1024 * 1024
        
        # Size display format (number of decimal places)
        SIZE_PRECISION: int = 2
        
        # JSON formatting
        JSON_INDENT: int = 2  # Spaces for JSON indentation
        
        # Timestamp format for responses
        TIMESTAMP_FORMAT: str = "%Y-%m-%dT%H:%M:%S.%f"  # ISO 8601 with microseconds
    
    # ==================== API AND RESPONSE ====================
    
    class API:
        """Configuration for API behavior."""
        
        # Error codes and HTTP status mappings
        HTTP_OK: int = 200
        HTTP_CREATED: int = 201
        HTTP_BAD_REQUEST: int = 400
        HTTP_NOT_FOUND: int = 404
        HTTP_CONFLICT: int = 409
        HTTP_SERVER_ERROR: int = 500
        
        # Response envelope keys
        DEFAULT_STATUS_KEY: str = "status"
        DEFAULT_ERROR_KEY: str = "error"
        DEFAULT_DETAIL_KEY: str = "detail"
        
        # Rate limiting (if implemented)
        MAX_CONCURRENT_SCANS: int = 5
        SCAN_TIMEOUT_SECONDS: int = 3600  # 1 hour max scan time
    
    # ==================== LOGGING AND DEBUGGING ====================
    
    class Logging:
        """Configuration for logging behavior."""
        
        # Log levels
        LOG_LEVEL_DEBUG: str = "DEBUG"
        LOG_LEVEL_INFO: str = "INFO"
        LOG_LEVEL_WARNING: str = "WARNING"
        LOG_LEVEL_ERROR: str = "ERROR"
        
        # Verbose logging flags
        LOG_FILE_OPERATIONS: bool = False  # Set to True for detailed file operation logs
        LOG_HASH_OPERATIONS: bool = False  # Set to True for hash calculation logs
        LOG_RECOVERY_OPERATIONS: bool = True  # Log all recovery operations
    
    # ==================== SECURITY ====================
    
    class Security:
        """Configuration for security parameters."""
        
        # Path traversal protection
        ALLOW_SYMLINKS: bool = False  # Strict: reject all symlinks
        VALIDATE_PATHS: bool = True  # Always validate paths
        
        # File operation security
        VERIFY_DELETION_TARGET: bool = True  # Always verify file exists before deletion
        USE_SAFE_RENAME: bool = True  # Use safe atomic operations
        
        # Maximum path length (filesystem limit on most systems)
        MAX_PATH_LENGTH: int = 260  # Windows MAX_PATH limit
    
    # ==================== CONVENIENCE PROPERTIES ====================
    
    @classmethod
    def get_file_system(cls) -> 'Config.FileSystem':
        """Get file system configuration."""
        return cls.FileSystem
    
    @classmethod
    def get_recovery(cls) -> 'Config.Recovery':
        """Get recovery configuration."""
        return cls.Recovery
    
    @classmethod
    def get_carbon(cls) -> 'Config.Carbon':
        """Get carbon configuration."""
        return cls.Carbon
    
    @classmethod
    def get_performance(cls) -> 'Config.Performance':
        """Get performance configuration."""
        return cls.Performance
    
    @classmethod
    def to_dict(cls) -> Dict:
        """Convert all configuration to a dictionary for inspection/logging."""
        return {
            'FileSystem': {
                'HASH_CHUNK_SIZE': cls.FileSystem.HASH_CHUNK_SIZE,
                'LARGE_FILE_THRESHOLD': cls.FileSystem.LARGE_FILE_THRESHOLD,
                'OLD_FILE_AGE_DAYS': cls.FileSystem.OLD_FILE_AGE_DAYS,
                'PROGRESS_UPDATE_FREQUENCY': cls.FileSystem.PROGRESS_UPDATE_FREQUENCY,
                'MIN_DUPLICATES_IN_GROUP': cls.FileSystem.MIN_DUPLICATES_IN_GROUP,
                'MAX_RECOVERY_NAME_ATTEMPTS': cls.FileSystem.MAX_RECOVERY_NAME_ATTEMPTS,
            },
            'Recovery': {
                'RECOVERY_DIR': cls.Recovery.RECOVERY_DIR,
                'RETENTION_DAYS': cls.Recovery.RETENTION_DAYS,
            },
            'Carbon': {
                'CARBON_PER_GB_PER_YEAR': cls.Carbon.CARBON_PER_GB_PER_YEAR,
                'CARBON_COST_PER_KG': cls.Carbon.CARBON_COST_PER_KG,
                'CARBON_OFFSET_PER_TREE_YEAR': cls.Carbon.CARBON_OFFSET_PER_TREE_YEAR,
            },
            'Performance': {
                'MAX_RESULTS_PER_CATEGORY': cls.Performance.MAX_RESULTS_PER_CATEGORY,
                'BATCH_SIZE_FOR_HASHING': cls.Performance.BATCH_SIZE_FOR_HASHING,
            },
        }


# ==================== EXPORTED DEFAULTS FOR BACKWARD COMPATIBILITY ====================
# These exports ensure existing code continues to work without changes

# File system constants (used in wasteDetect.py)
SYSTEM_FILE_EXTENSIONS = Config.FileSystem.SYSTEM_FILE_EXTENSIONS
SYSTEM_DIRECTORIES = Config.FileSystem.SYSTEM_DIRECTORIES

# Recovery constants (used in wasteDetect.py and app.py)
RECOVERY_DIR = Config.Recovery.RECOVERY_DIR
RECOVERY_METADATA_DIR = Config.Recovery.RECOVERY_METADATA_DIR
RECOVERY_RETENTION_DAYS = Config.Recovery.RETENTION_DAYS


__all__ = [
    'Config',
    # Backward compatibility exports
    'SYSTEM_FILE_EXTENSIONS',
    'SYSTEM_DIRECTORIES',
    'RECOVERY_DIR',
    'RECOVERY_METADATA_DIR',
    'RECOVERY_RETENTION_DAYS',
]
