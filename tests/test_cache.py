"""
Unit tests cho module SguCache (SQLite Caching)
"""

import time

from sgu_mcp.core.cache import SguCache


def test_cache_set_and_get(tmp_path):
    db_file = tmp_path / "test_cache.db"
    cache = SguCache(db_path=str(db_file))

    sample_data = {"user": "3122410001", "name": "Nguyen Van A"}
    cache.set("test_key", sample_data, ttl_seconds=60)

    cached = cache.get("test_key")
    assert cached == sample_data


def test_cache_ttl_expiration(tmp_path):
    db_file = tmp_path / "test_cache_exp.db"
    cache = SguCache(db_path=str(db_file))

    cache.set("expire_key", {"msg": "hello"}, ttl_seconds=1)
    # Lấy ngay lập tức -> có dữ liệu
    assert cache.get("expire_key") is not None

    # Đợi hết TTL
    time.sleep(1.2)
    assert cache.get("expire_key") is None


def test_cache_clear(tmp_path):
    db_file = tmp_path / "test_cache_clear.db"
    cache = SguCache(db_path=str(db_file))

    cache.set("k1", "data1")
    cache.set("k2", "data2")

    cache.clear("k1")
    assert cache.get("k1") is None
    assert cache.get("k2") == "data2"

    cache.clear()
    assert cache.get("k2") is None


def test_cache_exceptions(tmp_path, monkeypatch):
    db_file = tmp_path / "test_cache_err.db"
    cache = SguCache(db_path=str(db_file))

    import sqlite3

    def mock_connect(*args, **kwargs):
        raise sqlite3.OperationalError("Simulated DB error")

    monkeypatch.setattr(sqlite3, "connect", mock_connect)

    # get should catch exception and return None
    assert cache.get("any_key") is None

    # set should catch exception and pass
    cache.set("any_key", {"data": 123})

    # clear with key should catch exception and pass
    cache.clear("any_key")

    # clear all should catch exception and pass
    cache.clear()


def test_cache_init_fallback(monkeypatch, tmp_path):
    import sqlite3

    call_count = 0
    original_connect = sqlite3.connect

    def faulty_connect(database, *args, **kwargs):
        nonlocal call_count
        call_count += 1
        # Lần đầu tiên connect vào path chỉ định thì giả lập lỗi permission
        if call_count == 1:
            raise sqlite3.OperationalError("unable to open database file")
        return original_connect(database, *args, **kwargs)

    monkeypatch.setattr(sqlite3, "connect", faulty_connect)

    bad_path = str(tmp_path / "bad" / "cache.db")
    cache = SguCache(db_path=bad_path)

    # Đảm bảo cache đã tự động fallback và vẫn hoạt động bình thường
    assert cache._disabled is False
    assert cache.db_path != bad_path
    cache.set("test_fallback", {"ok": True})
    assert cache.get("test_fallback") == {"ok": True}


def test_cache_init_all_fail_graceful(monkeypatch):
    import sqlite3

    def fail_connect(*args, **kwargs):
        raise sqlite3.OperationalError("Total FS failure")

    monkeypatch.setattr(sqlite3, "connect", fail_connect)

    cache = SguCache(db_path="/invalid/nonexistent/db.db")
    # Phải kích hoạt chế độ _disabled thay vì crash
    assert cache._disabled is True
    assert cache.get("any") is None
    cache.set("any", 123)
    cache.clear()
