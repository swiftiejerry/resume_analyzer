import redis
import json
from typing import Optional

class RedisService:
    def __init__(self, host: str, port: int, db: int, password: Optional[str] = None):
        self.memory_cache = {}
        self.client = None
        try:
            self.client = redis.Redis(
                host=host, port=port, db=db, password=password,
                decode_responses=True, socket_connect_timeout=2
            )
            # Test the connection once at startup
            self.client.ping()
            print("Redis connected successfully.")
        except Exception as e:
            print(f"Redis connection failed at startup, using in-memory cache: {e}")
            self.client = None

    def _is_available(self) -> bool:
        """Check if Redis client is available without pinging every time."""
        return self.client is not None

    def cache_resume_data(self, resume_id: str, data: dict, expire_seconds: int = 86400):
        """Cache the parsed resume basic info JSON."""
        key = f"resume_data:{resume_id}"
        data_str = json.dumps(data, ensure_ascii=False)
        if self._is_available():
            try:
                self.client.setex(key, expire_seconds, data_str)
                return
            except (redis.ConnectionError, redis.TimeoutError) as e:
                print(f"Redis write failed, falling back to memory: {e}")
                self.client = None  # Mark as unavailable
        self.memory_cache[key] = data_str

    def get_resume_data(self, resume_id: str) -> Optional[dict]:
        """Get cached resume data."""
        key = f"resume_data:{resume_id}"
        data_str = None
        if self._is_available():
            try:
                data_str = self.client.get(key)
            except (redis.ConnectionError, redis.TimeoutError) as e:
                print(f"Redis read failed, falling back to memory: {e}")
                self.client = None  # Mark as unavailable
        if not data_str:
            data_str = self.memory_cache.get(key)
            
        if data_str:
            return json.loads(data_str)
        return None

    def cache_match_result(self, resume_id: str, job_hash: str, match_result: dict, expire_seconds: int = 86400):
        """Cache match result for a specific resume and job description pair."""
        key = f"match:{resume_id}:{job_hash}"
        data_str = json.dumps(match_result, ensure_ascii=False)
        if self._is_available():
            try:
                self.client.setex(key, expire_seconds, data_str)
                return
            except (redis.ConnectionError, redis.TimeoutError) as e:
                print(f"Redis write failed, falling back to memory: {e}")
                self.client = None
        self.memory_cache[key] = data_str
        
    def get_match_result(self, resume_id: str, job_hash: str) -> Optional[dict]:
        key = f"match:{resume_id}:{job_hash}"
        data_str = None
        if self._is_available():
            try:
                data_str = self.client.get(key)
            except (redis.ConnectionError, redis.TimeoutError) as e:
                print(f"Redis read failed, falling back to memory: {e}")
                self.client = None
        if not data_str:
            data_str = self.memory_cache.get(key)
        if data_str:
            return json.loads(data_str)
        return None
