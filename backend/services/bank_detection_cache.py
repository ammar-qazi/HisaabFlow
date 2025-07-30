"""
Global bank detection cache service to avoid redundant API calls
"""
import hashlib
import os
from typing import Optional, Dict, Any


class BankDetectionCache:
    """Global cache for bank detection results"""
    
    def __init__(self):
        self._cache = {}
    
    def _generate_cache_key(self, filename: str, file_path: str) -> str:
        """Generate consistent cache key based on filename and file content"""
        try:
            # Use filename and file size for consistent caching
            stat = os.stat(file_path)
            content_hash = hashlib.md5(f"{filename}_{stat.st_size}".encode()).hexdigest()[:8]
            return f"{filename}_{content_hash}"
        except:
            # Fallback to filename-based hash
            return f"{filename}_{hash(filename)}"
    
    def get(self, filename: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Get cached bank detection result"""
        cache_key = self._generate_cache_key(filename, file_path)
        cached_result = self._cache.get(cache_key)
        if cached_result:
            print(f"ℹ [CACHE] Using cached bank detection for {filename}")
            return cached_result
        return None
    
    def set(self, filename: str, file_path: str, detection_result: Dict[str, Any]):
        """Cache bank detection result"""
        cache_key = self._generate_cache_key(filename, file_path)
        self._cache[cache_key] = detection_result
        print(f"ℹ [CACHE] Cached bank detection result for {filename}")
    
    def clear(self):
        """Clear all cached results"""
        self._cache.clear()
        print("ℹ [CACHE] Bank detection cache cleared")
    
    def size(self) -> int:
        """Get cache size"""
        return len(self._cache)


# Global singleton instance
_global_cache = BankDetectionCache()


def get_bank_detection_cache() -> BankDetectionCache:
    """Get the global bank detection cache instance"""
    return _global_cache