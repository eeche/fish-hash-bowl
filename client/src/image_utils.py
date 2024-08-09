import os
import hashlib
import subprocess
import requests
import json
from pathlib import Path

# 설정 파일 로드
# config_path = Path("/opt/fish-hash-bowl/config/config.json")
# with config_path.open() as f:
#     config = json.load(f)

# CENTRAL_SERVER_URL = config['central_server_url']
# API_KEY = config['api_key']
# OVERLAY2_PATH = "/var/lib/docker/overlay2/"
HASH_STORAGE_PATH = "~/git/python/fish-hash-bowl/image_hashes.json"

def get_image_layer_path(image_name):
    """Docker inspect 명령어를 사용하여 이미지 레이어 경로를 가져오는 함수"""
    cmd = f"docker inspect --format='{{{{index (split .GraphDriver.Data.LowerDir \":\") 0}}}}' {image_name}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to get image layer path: {result.stderr}")
    return result.stdout.strip()

def calculate_hash(image_name):
    """이미지 레이어의 해시값을 계산하는 함수"""
    # path = os.path.join(OVERLAY2_PATH, image_name)
    path = get_image_layer_path(image_name)
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

# def get_stored_hash(image_name):
#     """중앙 서버에서 저장된 이미지 해시값을 가져오는 함수"""
#     headers = {"Authorization": f"Bearer {API_KEY}"}
#     response = requests.get(f"{CENTRAL_SERVER_URL}/images/{image_name}", headers=headers)
#     if response.status_code == 200:
#         return response.json()["hash"]
#     return None

def save_hash(image_name, image_hash):
    """해시값을 로컬 json파일에 저장하는 함수"""
    os.makedirs(os.path.dirname(HASH_STORAGE_PATH), exist_ok=True)
    
    if os.path.exists(HASH_STORAGE_PATH):
        with open(HASH_STORAGE_PATH, 'r') as f:
            hashes = json.load(f)
    else:
        hashes = {}
    
    hashes[image_name] = image_hash
    
    with open(HASH_STORAGE_PATH, 'w') as f:
        json.dump(hashes, f, indent=4)


    # os.makedirs(os.path.dirname(HASH_STORAGE_PATH), exist_ok=True)
    # with open(HASH_STORAGE_PATH, "w") as f:
    #     json.dump({image_name: image_hash}, f)



# def register_hash(image_name, image_hash):
#     """중앙 서버에 이미지 해시값을 등록하는 함수"""
#     headers = {
#         "Authorization": f"Bearer {API_KEY}",
#         "Content-Type": "application/json"
#     }
#     data = {
#         "image_name": image_name,
#         "hash": image_hash
#     }
#     response = requests.post(f"{CENTRAL_SERVER_URL}/images", json=data, headers=headers)
#     if response.status_code == 201:
#         print(f"Hash for {image_name} registered successfully.")
#     else:
#         print(f"Failed to register hash for {image_name}. Status code: {response.status_code}")
#         print(response.text)

def get_stored_hash(image_name):
    """로컬 JSON 파일에서 저장된 해시값을 가져오는 함수"""
    if not os.path.exists(HASH_STORAGE_PATH):
        return None
    
    with open(HASH_STORAGE_PATH, 'r') as f:
        hashes = json.load(f)
    
    return hashes.get(image_name)

def register_hash(image_name):
    """해시값을 로컬에 등록하는 함수"""
    image_hash = calculate_hash(image_name)
    save_hash(image_name, image_hash)
    print(f"Hash for {image_name} registered successfully.")
    return image_hash

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python image_utils.py <image_name>")
        sys.exit(1)
    
    image_name = sys.argv[1]
    try:
        calculated_hash = register_hash(image_name)
        print(f"Hash calculated and saved for image {image_name}: {calculated_hash}")
        
        retrieved_hash = get_stored_hash(image_name)
        print(f"Retrieved hash for image {image_name}: {retrieved_hash}")
        
        if calculated_hash == retrieved_hash:
            print("Hash verification successful!")
        else:
            print("Hash verification failed!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# TODO:
# 1. 에러 처리 개선 (예: 네트워크 오류, 서버 응답 오류 등)
# 2. 로깅 기능 추가
# 3. 해시 계산 성능 최적화 (예: 병렬 처리)
# 4. API 요청에 대한 재시도 메커니즘 구현
# 5. 캐싱 메커니즘 도입하여 반복적인 해시 계산 및 API 요청 최소화