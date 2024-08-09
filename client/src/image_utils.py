import os
import hashlib
import requests
import json
from pathlib import Path

# 설정 파일 로드
config_path = Path("/opt/fish-hash-bowl/config/config.json")
with config_path.open() as f:
    config = json.load(f)

CENTRAL_SERVER_URL = config['central_server_url']
API_KEY = config['api_key']
OVERLAY2_PATH = "/var/lib/docker/overlay2/"

def calculate_hash(image_id):
    """이미지 레이어의 해시값을 계산하는 함수"""
    path = os.path.join(OVERLAY2_PATH, image_id)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path not found: {path}")

    sha256_hash = hashlib.sha256()
    for root, _, files in os.walk(path):
        for file in files:
            filepath = os.path.join(root, file)
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_stored_hash(image_id):
    """중앙 서버에서 저장된 이미지 해시값을 가져오는 함수"""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"{CENTRAL_SERVER_URL}/images/{image_id}", headers=headers)
    if response.status_code == 200:
        return response.json()["hash"]
    return None

def register_hash(image_name, image_hash):
    """중앙 서버에 이미지 해시값을 등록하는 함수"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "image_name": image_name,
        "hash": image_hash
    }
    response = requests.post(f"{CENTRAL_SERVER_URL}/images", json=data, headers=headers)
    if response.status_code == 201:
        print(f"Hash for {image_name} registered successfully.")
    else:
        print(f"Failed to register hash for {image_name}. Status code: {response.status_code}")
        print(response.text)

# TODO:
# 1. 에러 처리 개선 (예: 네트워크 오류, 서버 응답 오류 등)
# 2. 로깅 기능 추가
# 3. 해시 계산 성능 최적화 (예: 병렬 처리)
# 4. API 요청에 대한 재시도 메커니즘 구현
# 5. 캐싱 메커니즘 도입하여 반복적인 해시 계산 및 API 요청 최소화