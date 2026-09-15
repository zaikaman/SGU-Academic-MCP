"""
Module lưu trữ Cache dữ liệu SGU bằng SQLite
Giúp giảm tải gọi lặp lại lên server trường SGU và đảm bảo hoạt động khi mạng chập chờn.
"""

import json
import os
import sqlite3
import time
from typing import Any


class SguCache:
    """
    Quản lý bộ nhớ đệm SQLite cho các phản hồi API từ SGU.
    """

    def __init__(self, db_path: str = "./data/sgu_cache.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_cache (
                    cache_key TEXT PRIMARY KEY,
                    data_json TEXT NOT NULL,
                    updated_at REAL NOT NULL,
                    ttl_seconds INTEGER NOT NULL
                )
            """)
            conn.commit()

    def get(self, key: str) -> Any | None:
        """Lấy dữ liệu từ cache nếu chưa hết hạn"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data_json, updated_at, ttl_seconds FROM api_cache WHERE cache_key = ?",
                    (key,),
                )
                row = cursor.fetchone()
                if not row:
                    return None

                data_json, updated_at, ttl_seconds = row
                # Kiểm tra TTL (nếu ttl_seconds > 0)
                if ttl_seconds > 0 and (time.time() - updated_at) > ttl_seconds:
                    return None

                return json.loads(data_json)
        except Exception:
            return None

    def set(self, key: str, data: Any, ttl_seconds: int = 3600):
        """Lưu dữ liệu vào cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO api_cache (cache_key, data_json, updated_at, ttl_seconds)
                    VALUES (?, ?, ?, ?)
                """,
                    (key, json.dumps(data, ensure_ascii=False), time.time(), ttl_seconds),
                )
                conn.commit()
        except Exception:
            pass

    def clear(self, key: str | None = None):
        """Xóa một key hoặc xóa toàn bộ cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if key:
                    cursor.execute("DELETE FROM api_cache WHERE cache_key = ?", (key,))
                else:
                    cursor.execute("DELETE FROM api_cache")
                conn.commit()
        except Exception:
            pass

# [toansiuuu commit 13: clean up debug print statements]
