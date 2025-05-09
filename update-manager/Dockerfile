FROM python:3.11-slim

# Cập nhật kho và cài đặt các gói cần thiết
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    docker.io && \
    apt-get clean

# Thêm Docker Compose
RUN curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# Tạo thư mục làm việc
WORKDIR /app/update-manager

# Copy phần còn lại của source code vào container
COPY . .

EXPOSE 20000

# Cài đặt các thư viện Python yêu cầu (nếu có)
RUN pip install -r requirements.txt

# Thiết lập entrypoint (nếu cần, ví dụ chạy script main.py)
CMD ["python", "main.py"]
