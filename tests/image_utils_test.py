import os
import hashlib
import subprocess
import json

import requests

HASH_STORAGE_PATH = "./image_hashes.json"

url = 'http://localhost:8080/'
api = 'default_apikey'

def get_image_layer_path(image_name):
    """Docker inspect 명령어를 사용하여 이미지 레이어 경로를 가져오는 함수"""
    
    # 레이어 수 확인
    layer_cmd = f"docker inspect --format='{{{{json .RootFS.Layers}}}}' {image_name}"
    layer_result = subprocess.run(layer_cmd, shell=True, capture_output=True, text=True)
    if layer_result.returncode != 0:
        raise Exception(f"Failed to get layer information: {layer_result.stderr}")
    
    layers = json.loads(layer_result.stdout)
    
    if len(layers) == 1:
        # 단일 레이어인 경우 UpperDir 사용
        cmd = f"docker inspect --format='{{{{index (split .GraphDriver.Data.UpperDir \":\") 0}}}}' {image_name}"
    else:
        # 여러 레이어인 경우 LowerDir 사용
        cmd = f"docker inspect --format='{{{{index (split .GraphDriver.Data.LowerDir \":\") 0}}}}' {image_name}"
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to get image layer path: {result.stderr}")
    
    return result.stdout.strip()

def calculate_hash(image_name):
    """이미지 레이어의 해시값을 계산하는 함수"""
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

def get_stored_hash(image_name):
    """로컬 JSON 파일에서 저장된 해시값을 가져오는 함수"""
    if not os.path.exists(HASH_STORAGE_PATH):
        return None
    
    with open(HASH_STORAGE_PATH, 'r') as f:
        hashes = json.load(f)
    
    return hashes.get(image_name)

def register_hash(image_name):
    """해시값을 계산하고 로컬에 등록하는 함수"""
    image_hash = calculate_hash(image_name)
    save_hash(image_name, image_hash)
    # TODO: 중앙 서버에 해시값 등록
    headers = {
        "Authorization": f"Bearer {api}",
        "Content-Type": "application/json"
    }
    data = {
        "apikey": api,
        "docker_image_name": image_name,
        "docker_image_hash": image_hash
    }
    response = requests.post(f"{url}/api/register-docker-hash", headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        print(f"Success: {response.json()['message']}")
    else:
        print(f"Failed to register hash for {image_name}. Status code: {response.status_code}")
        print(f"Error message: {response.json().get('detail', 'Unknown error')}")

    return True

# 테스트 및 예시 용도의 메인 함수
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python image_utils_test.py <image_name>")
        sys.exit(1)
    
    image_name = sys.argv[1]
    if ':' not in image_name:
        image_name += ':latest'
    try:
        calculated_hash = calculate_hash(image_name)
        print(f"Hash calculated for image {image_name}: {calculated_hash}")

        if register_hash(image_name):
            # print(f"Hash for {image_name} registered successfully.")
        
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
# 4. 캐싱 메커니즘 도입하여 반복적인 해시 계산 최소화