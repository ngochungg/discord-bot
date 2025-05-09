FROM python:3.11-slim

# Cài git và các gói cần thiết
RUN apt-get update && apt-get install -y git docker.io docker-compose && apt-get clean

# Tạo thư mục làm việc
WORKDIR /app/update-manager

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY update_bot.sh .
RUN chmod +x update_bot.sh

COPY . .

# Mở cổng Flask
EXPOSE 8000

CMD ["python", "main.py"]
