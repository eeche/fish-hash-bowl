#!/bin/bash

# 설치 디렉토리 설정
INSTALL_DIR="/opt/fish-hash-client"

# 스크립트의 위치를 기반으로 소스 디렉토리 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SOURCE_DIR="$PROJECT_ROOT/client"

# 필요한 패키지 설치
sudo apt-get update
sudo apt-get install -y python3 python3-pip

# 디렉토리 생성
sudo mkdir -p $INSTALL_DIR
sudo mkdir -p $INSTALL_DIR/config
sudo mkdir -p /var/log/fish-hash-client

# 파일 복사
sudo cp $SOURCE_DIR/image_utils.py $INSTALL_DIR/
sudo cp $SOURCE_DIR/integrity_checker.py $INSTALL_DIR/
sudo cp $SOURCE_DIR/hash_registrar.py $INSTALL_DIR/
sudo cp $SOURCE_DIR/event_monitor.py $INSTALL_DIR/

# requirements.txt 복사 및 패키지 설치
sudo cp $PROJECT_ROOT/requirements.txt $INSTALL_DIR/
sudo pip3 install -r $INSTALL_DIR/requirements.txt

# API 키 및 서버 URL 설정
echo "Enter your API key:"
read API_KEY
echo "Enter the server URL (default: http://localhost:8080):"
read SERVER_URL
SERVER_URL=${SERVER_URL:-http://localhost:8080}

# config.json 생성
sudo tee $INSTALL_DIR/config/config.json > /dev/null <<EOF
{
    "api_key": "$API_KEY",
    "server_url": "$SERVER_URL"
}
EOF

# 권한 설정
sudo chmod 600 $INSTALL_DIR/config/config.json
sudo chmod +x $INSTALL_DIR/*.py

# 로그 디렉토리 권한 설정
sudo chown -R root:root /var/log/fish-hash-client
sudo chmod 755 /var/log/fish-hash-client

# Docker 이벤트 모니터 서비스 파일 생성
sudo tee /etc/systemd/system/docker-event-monitor.service > /dev/null <<EOF
[Unit]
Description=Docker Event Monitor
After=docker.service

[Service]
ExecStart=/usr/bin/python3 $INSTALL_DIR/event_monitor.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

# 서비스 활성화 및 시작
sudo systemctl daemon-reload
sudo systemctl enable docker-event-monitor.service
sudo systemctl start docker-event-monitor.service

echo "Fish Hash Bowl security solution installed successfully."