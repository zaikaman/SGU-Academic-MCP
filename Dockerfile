FROM python:3.12-slim

WORKDIR /app

# Cài đặt các gói hệ thống cần thiết
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt dependencies Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy mã nguồn
COPY . .

# Tạo thư mục lưu trữ cache SQLite
RUN mkdir -p /app/data

# Thiết lập biến môi trường
ENV PYTHONUNBUFFERED=1
ENV SGU_DB_PATH=/app/data/sgu_cache.db

# Mở cổng SSE
EXPOSE 8000

# Chạy MCP Server ở chế độ SSE trên port 8000
CMD ["python", "-m", "sgu_mcp.server", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
