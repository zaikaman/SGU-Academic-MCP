"""
Cấu hình hệ thống SGU MCP Server
Sử dụng pydantic-settings để đọc biến môi trường từ .env
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Cổng thông tin đào tạo SGU
    portal_url: str = Field(default="https://thongtindaotao.sgu.edu.vn", alias="SGU_PORTAL_URL")

    # Tài khoản sinh viên SGU (dùng để gọi API thật)
    student_id: str | None = Field(default=None, alias="SGU_STUDENT_ID")
    password: str | None = Field(default=None, alias="SGU_PASSWORD")
    bearer_token: str | None = Field(default=None, alias="SGU_BEARER_TOKEN")

    # Cấu hình Caching SQLite
    db_path: str = Field(default="./data/sgu_cache.db", alias="SGU_DB_PATH")
    cache_ttl_seconds: int = Field(default=3600, alias="SGU_CACHE_TTL")  # 1 giờ

    # Cấu hình MCP Server
    mcp_host: str = Field(default="0.0.0.0", alias="MCP_SERVER_HOST")  # nosec B104
    mcp_port: int = Field(default=8000, alias="MCP_SERVER_PORT")


# Singleton instance
settings = Settings()

# [toansiuuu commit 5: fix typo in config timeout setting]
