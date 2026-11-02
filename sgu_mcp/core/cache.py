"""
Module lưu trữ Cache dữ liệu SGU bằng SQLite
Giúp giảm tải gọi lặp lại lên server trường SGU và đảm bảo hoạt động khi mạng chập chờn.
"""

import json
import os
import sqlite3
import time
from typing import Any

from sgu_mcp.config import settings


class SguCache:
    """
    Quản lý bộ nhớ đệm SQLite cho các phản hồi API từ SGU.
    Bảng lưu trữ chuẩn: api_cache (cache_key, data_json, updated_at, ttl_seconds).
    Cơ chế fallback: Thử mở DB tại db_path (mặc định ./data/sgu_cache.db). Nếu gặp lỗi quyền ghi
    (như trong Docker không mount volume có quyền), tự động fallback sang tempdir (/tmp).
    Nếu toàn bộ hệ thống file bị khóa, chuyển sang chế độ vô hiệu hóa (_disabled = True) an toàn.
    """

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.db_path
        self._disabled = False
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
            self._init_db()
        except (sqlite3.OperationalError, PermissionError, OSError):
            try:
                import tempfile

                self.db_path = os.path.join(tempfile.gettempdir(), "sgu_cache.db")
                os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
                self._init_db()
            except Exception:
                # Nếu toàn bộ hệ thống file bị khóa quyền ghi, chuyển sang chế độ vô hiệu hóa cache
                # để server vẫn khởi động và hoạt động 100% bình thường (gọi API trực tiếp)
                self._disabled = True

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
        """Lấy dữ liệu từ cache nếu chưa hết hạn. TTL <= 0 được tính là tắt cache hoặc đã hết hạn tức thì."""
        if getattr(self, "_disabled", False):
            return None
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
                # Quy tắc TTL: ttl_seconds <= 0 nghĩa là cache bị tắt/hết hạn ngay
                if ttl_seconds <= 0 or (time.time() - updated_at) > ttl_seconds:
                    return None

                return json.loads(data_json)
        except Exception:
            return None

    def set(self, key: str, data: Any, ttl_seconds: int | None = None):
        """Lưu dữ liệu vào cache. Nếu ttl_seconds <= 0, bỏ qua không lưu vì cache bị tắt."""
        if getattr(self, "_disabled", False):
            return
        ttl = ttl_seconds if ttl_seconds is not None else settings.cache_ttl_seconds
        if ttl <= 0:
            # TTL=0 nghĩa là tắt cache; xóa key cũ nếu có để tránh stale data
            self.clear(key)
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO api_cache (cache_key, data_json, updated_at, ttl_seconds)
                    VALUES (?, ?, ?, ?)
                """,
                    (key, json.dumps(data, ensure_ascii=False), time.time(), ttl),
                )
                conn.commit()
        except Exception:
            pass

    def clear(self, key: str | None = None):
        """Xóa một key hoặc xóa toàn bộ cache"""
        if getattr(self, "_disabled", False):
            return
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
