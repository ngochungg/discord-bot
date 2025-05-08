FROM python:3.11-slim

# Cài gói cần thiết cho runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    procps curl ca-certificates unzip jq docker.io && \
    rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /app

# Copy file requirements trước (tối ưu layer cache)
COPY requirements.txt .

# Cài thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy phần còn lại của source code
COPY . .

# Cho phép script shell chạy được
RUN chmod +x entrypoint.sh

# Lệnh chạy chính
CMD ["sh", "entrypoint.sh"]
