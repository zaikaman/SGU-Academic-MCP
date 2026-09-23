# ==============================================================================
# SGU Academic MCP Server - Production Dockerfile
# Multi-stage optimized, non-root user, built-in health check
# ==============================================================================

FROM python:3.12-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt curl phục vụ container healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Tạo user không đặc quyền (non-root) để tăng cường bảo mật
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Cài đặt dependencies Python trước để tận dụng Docker build cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn dự án (đã lọc qua .dockerignore)
COPY --chown=appuser:appuser . .

# Khởi tạo thư mục chứa SQLite cache và cấp quyền cho appuser
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Chuyển quyền thực thi sang user appuser
USER appuser

# Thiết lập các biến môi trường mặc định
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SGU_DB_PATH=/app/data/sgu_cache.db \
    MCP_SERVER_HOST=0.0.0.0 \
    MCP_SERVER_PORT=8000

# Mở cổng giao tiếp SSE
EXPOSE 8000

# Kiểm tra sức khỏe container định kỳ qua endpoint /health
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${MCP_SERVER_PORT:-8000}/health || exit 1

# Khởi chạy MCP Server ở chế độ SSE (host và port tự động nạp từ ENV)
CMD ["python", "-m", "sgu_mcp.server", "--transport", "sse"]
