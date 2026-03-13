#!/bin/bash
# 1. Tạo thư mục .ssh thực sự của root
mkdir -p /root/.ssh

# 2. Copy chìa khóa từ thư mục mount tạm vào thư mục chuẩn
if [ -d "/mnt/.ssh" ]; then
    cp -r /mnt/.ssh/* /root/.ssh/
fi

# 3. Sửa quyền sở hữu và quyền truy cập (Bắt buộc để SSH chạy)
chown -R root:root /root/.ssh
chmod 700 /root/.ssh
chmod 600 /root/.ssh/*

# 4. Chạy lệnh chính (Bot)
exec "$@"