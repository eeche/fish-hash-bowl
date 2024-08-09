#!/bin/bash

# 필요한 패키지 설치
sudo apt-get update
sudo apt-get install -y python3 python3-pip
sudo pip3 install docker requests flask

# 디렉토리 생성
sudo mkdir -p /opt/company-security-solution/{bin,lib,config}
sudo mkdir -p /var/log/company-security-solution

# 파일 복사
sudo cp bin/docker-wrapper /opt/company-security-solution/bin/
sudo cp lib/integrity_check.py /opt/company-security-solution/lib/
sudo cp lib/register_image_hash.py /opt/company-security-solution/lib/
sudo cp docker-security-plugin.py /opt/company-security-solution/

# 권한 설정
sudo chmod +x /opt/company-security-solution/bin/docker-wrapper
sudo chmod +x /opt/company-security-solution/lib/integrity_check.py
sudo chmod +x /opt/company-security-solution/lib/register_image_hash.py
sudo chmod +x /opt/company-security-solution/docker-security-plugin.py

# Docker 명령어 대체
sudo mv /usr/bin/docker /usr/bin/docker.original
sudo ln -s /opt/company-security-solution/bin/docker-wrapper /usr/bin/docker

# 로그 디렉토리 권한 설정
sudo chown -R root:root /var/log/company-security-solution
sudo chmod 755 /var/log/company-security-solution

# API 키 설정
echo "Enter your API key:"
read API_KEY

# config.json 생성
cat > /opt/company-security-solution/config/config.json << EOF
{
    "api_endpoint": "https://www.check-docker.com/api/v1",
    "api_key": "$API_KEY"
}
EOF

# config.json 권한 설정
sudo chmod 600 /opt/company-security-solution/config/config.json

# Docker 데몬 설정 수정
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "authorization-plugins": ["docker-security-plugin"]
}
EOF

# Docker 보안 플러그인 서비스 파일 생성
sudo tee /etc/systemd/system/docker-security-plugin.service > /dev/null <<EOF
[Unit]
Description=Docker Security Plugin
After=docker.service

[Service]
ExecStart=/usr/bin/python3 /opt/company-security-solution/docker-security-plugin.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 서비스 활성화 및 시작
sudo systemctl daemon-reload
sudo systemctl enable docker-security-plugin.service
sudo systemctl start docker-security-plugin.service

# Docker 재시작
sudo systemctl restart docker

echo "Company security solution installed successfully."