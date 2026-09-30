"""
Global bank detection cache service to avoid redundant API calls
"""
import hashlib
from typing import Optional, Dict, Any

from backend.infrastructure.config.unified_config_service import register_config_reload_listener


class BankDetectionCache:
    """Global cache for bank detection results"""
    
    def __init__(self):
        self._cache = {}
    
    def _generate_cache_key(self, filename: str, file_path: str) -> Optional[str]:
        """Key on filename (it affects detection) plus a hash of the file content"""
        try:
            with open(file_path, 'rb') as f:
                content_hash = hashlib.sha256(f.read()).hexdigest()
        except (OSError, TypeError):
            return None
        return f"{filename}_{content_hash}"
    
    def get(self, filename: str, file_path: str) -> Optional[Dict[str, Any]]:
        """Get cached bank detection result"""
        cache_key = self._generate_cache_key(filename, file_path)
        if cache_key is None:
            return None
        
        cached_result = self._cache.get(cache_key)
        if cached_result:
            print(f"ℹ [CACHE] Using cached bank detection for {filename}")
        return cached_result
    
    def set(self, filename: str, file_path: str, detection_result: Dict[str, Any]):
        """Cache bank detection result"""
        cache_key = self._generate_cache_key(filename, file_path)
        if cache_key is None:
            return
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

# Detection results depend on the configs, so drop them when configs reload
register_config_reload_listener(_global_cache.clear)


def get_bank_detection_cache() -> BankDetectionCache:
    """Get the global bank detection cache instance"""
    return _global_cache
