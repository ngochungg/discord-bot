FROM python:3.10-slim

# Cài các dependencies hệ thống cần thiết (build và runtime)
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cài pip packages
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy toàn bộ mã nguồn GPT4All vào container
COPY . /app

WORKDIR /app

# Expose port cho API (nếu có)
EXPOSE 5000

# Command để chạy API ví dụ (bạn chỉnh lại path model cho đúng)
CMD ["python3", "main.py", "--model", "gpt4all/models/ggml-gpt4all-j-v1.3-groovy.bin"]
