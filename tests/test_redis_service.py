"""Unit tests for RedisService (in-memory fallback mode)."""
import pytest
from services.redis_service import RedisService


@pytest.fixture
def memory_only_redis():
    """Create a RedisService instance that only uses in-memory cache (no actual Redis)."""
    service = RedisService.__new__(RedisService)
    service.memory_cache = {}
    service.client = None  # Force in-memory mode without connection attempt
    return service


@pytest.fixture
def live_redis():
    """Try to connect to actual local Redis. Skip if unavailable."""
    service = RedisService(host="127.0.0.1", port=6379, db=15)  # Use DB 15 for testing
    if service.client is None:
        pytest.skip("Redis not available")
    yield service
    # Cleanup: flush test DB
    try:
        service.client.flushdb()
    except Exception:
        pass


class TestRedisServiceMemoryFallback:
    """Test RedisService in memory-only mode."""

    def test_cache_and_get_resume_data(self, memory_only_redis):
        """Should store and retrieve resume data in memory."""
        test_data = {"basic_info": {"name": "Test"}, "job_intention": "Engineer"}
        memory_only_redis.cache_resume_data("abc123", test_data)
        
        result = memory_only_redis.get_resume_data("abc123")
        assert result is not None
        assert result["basic_info"]["name"] == "Test"
        assert result["job_intention"] == "Engineer"

    def test_get_nonexistent_resume_data(self, memory_only_redis):
        """Should return None for non-existent resume data."""
        result = memory_only_redis.get_resume_data("nonexistent_id")
        assert result is None

    def test_cache_and_get_match_result(self, memory_only_redis):
        """Should store and retrieve match results in memory."""
        match_data = {"score": 85, "skills_match_rate": "85%", "comment": "Good"}
        memory_only_redis.cache_match_result("abc123", "job_hash_1", match_data)
        
        result = memory_only_redis.get_match_result("abc123", "job_hash_1")
        assert result is not None
        assert result["score"] == 85

    def test_get_nonexistent_match_result(self, memory_only_redis):
        """Should return None for non-existent match result."""
        result = memory_only_redis.get_match_result("abc", "xyz")
        assert result is None

    def test_different_resume_ids_are_independent(self, memory_only_redis):
        """Each resume_id should be stored independently."""
        data1 = {"basic_info": {"name": "User1"}}
        data2 = {"basic_info": {"name": "User2"}}
        memory_only_redis.cache_resume_data("id1", data1)
        memory_only_redis.cache_resume_data("id2", data2)
        
        assert memory_only_redis.get_resume_data("id1")["basic_info"]["name"] == "User1"
        assert memory_only_redis.get_resume_data("id2")["basic_info"]["name"] == "User2"

    def test_different_job_hashes_are_independent(self, memory_only_redis):
        """Different job descriptions for same resume should be independent."""
        match1 = {"score": 80, "comment": "A"}
        match2 = {"score": 60, "comment": "B"}
        memory_only_redis.cache_match_result("resume1", "hash_a", match1)
        memory_only_redis.cache_match_result("resume1", "hash_b", match2)
        
        assert memory_only_redis.get_match_result("resume1", "hash_a")["score"] == 80
        assert memory_only_redis.get_match_result("resume1", "hash_b")["score"] == 60

    def test_overwrite_existing_data(self, memory_only_redis):
        """Caching with same key should overwrite old data."""
        memory_only_redis.cache_resume_data("same_id", {"version": 1})
        memory_only_redis.cache_resume_data("same_id", {"version": 2})
        result = memory_only_redis.get_resume_data("same_id")
        assert result["version"] == 2


class TestRedisServiceLive:
    """Test RedisService with actual Redis (skipped if Redis not available)."""

    def test_redis_cache_and_get_resume(self, live_redis):
        """Should store and retrieve via actual Redis."""
        test_data = {"basic_info": {"name": "Redis Test"}, "job_intention": "DevOps"}
        live_redis.cache_resume_data("redis_test_1", test_data)
        
        result = live_redis.get_resume_data("redis_test_1")
        assert result is not None
        assert result["basic_info"]["name"] == "Redis Test"

    def test_redis_cache_and_get_match(self, live_redis):
        """Should store and retrieve match results via actual Redis."""
        match_data = {"score": 92, "skills_match_rate": "90%", "experience_relevance": "High", "comment": "Great"}
        live_redis.cache_match_result("redis_test_1", "jh_1", match_data)
        
        result = live_redis.get_match_result("redis_test_1", "jh_1")
        assert result is not None
        assert result["score"] == 92

    def test_redis_returns_none_for_missing_key(self, live_redis):
        """Should return None for keys not in Redis."""
        result = live_redis.get_resume_data("totally_nonexistent_key_xxx")
        assert result is None
