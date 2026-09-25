import time
import os

class SimpleCache:
    def __init__(self, default_ttl: int = 300):
        self._cache = {}
        self.default_ttl = int(os.getenv("CACHE_TTL", default_ttl))

    def get(self, key: str):
        if key in self._cache:
            entry = self._cache[key]
            if time.time() < entry["expires_at"]:
                return entry["data"]
            else:
                del self._cache[key]
        return None

    def set(self, key: str, data: any, ttl: int = None):
        if ttl is None:
            ttl = self.default_ttl
        self._cache[key] = {
            "data": data,
            "expires_at": time.time() + ttl
        }

    def clear(self):
        self._cache.clear()

cache = SimpleCache()
