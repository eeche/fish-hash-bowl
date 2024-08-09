#!/bin/bash

# 필요한 패키지 설치
sudo apt-get update
sudo apt-get install -y python3 python3-pip
sudo pip3 install docker requests

# 디렉토리 생성
sudo mkdir -p /opt/fish-hash-bowl/{src,config}
sudo mkdir -p /var/log/fish-hash-bowl

# 파일 복사
sudo cp src/image_utils.py /opt/fish-hash-bowl/src/
sudo cp src/integrity_checker.py /opt/fish-hash-bowl/src/
sudo cp src/hash_registrar.py /opt/fish-hash-bowl/src/
sudo cp src/event_monitor.py /opt/fish-hash-bowl/src/

# 권한 설정
sudo chmod +x /opt/fish-hash-bowl/src/integrity_checker.py
sudo chmod +x /opt/fish-hash-bowl/src/hash_registrar.py
sudo chmod +x /opt/fish-hash-bowl/src/event_monitor.py

# 로그 디렉토리 권한 설정
sudo chown -R root:root /var/log/fish-hash-bowl
sudo chmod 755 /var/log/fish-hash-bowl

# API 키 설정
echo "Enter your API key:"
read API_KEY

# config.json 생성
cat > /opt/fish-hash-bowl/config/config.json << EOF
{
    "central_server_url": "https://www.check-docker.com/api/v1",
    "api_key": "$API_KEY"
}
EOF

# config.json 권한 설정
sudo chmod 600 /opt/fish-hash-bowl/config/config.json

# Docker 이벤트 모니터 서비스 파일 생성
sudo tee /etc/systemd/system/docker-event-monitor.service > /dev/null <<EOF
[Unit]
Description=Docker Event Monitor
After=docker.service

[Service]
ExecStart=/usr/bin/python3 /opt/fish-hash-bowl/src/event_monitor.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 서비스 활성화 및 시작
sudo systemctl daemon-reload
sudo systemctl enable docker-event-monitor.service
sudo systemctl start docker-event-monitor.service

echo "Company security solution installed successfully."

# TODO:
# 1. 설치 과정 로깅 추가
# 2. 설치 실패 시 롤백 메커니즘 구현
# 3. 사용자 입력 검증 (예: API 키 형식 확인)
# 4. 의존성 검사 (예: Docker 설치 여부, Python 버전 확인)
# 5. 설치 완료 후 시스템 상태 확인 및 보고
# 6. 업그레이드 메커니즘 구현
# 7. 설치 옵션 추가 (예: 사용자 정의 설치 경로, 로그 레벨 설정 등)