FROM python:3.11-slim

# Cài gói cần thiết cho runtime
RUN apt-get update --allow-releaseinfo-change && apt-get install -y --fix-missing  --no-install-recommends \
    curl ca-certificates unzip jq docker.io docker-compose git build-essential  \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /app

# Copy file requirements trước (tối ưu layer cache)
COPY requirements.txt .

# Cài thư viện Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install yt-dlp

# Copy phần còn lại của source code
COPY . .

# Cho phép script shell chạy được
RUN chmod +x entrypoint.sh

# Lệnh chạy chính
CMD ["sh", "entrypoint.sh"]
