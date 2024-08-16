import grp
import os
import hashlib
import pwd
import subprocess
import json
import requests
import stat

HASH_STORAGE_PATH = "./image_hashes.json"

API_KEY = "40eb2e1f5d6627cb234fad0f7960b9e05140f7e3ad4fbffcc92577e8f27aa4b7"
SERVER_URL = "http://localhost:8080"

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
    """이미지 레이어의 해시값을 매우 세밀하게 계산하는 함수"""
    path = get_image_layer_path(image_name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path not found: {path}")

    sha256_hash = hashlib.sha256()
    
    for root, dirs, files in os.walk(path):
        # 디렉토리 정보 해시에 추가
        dir_stat = os.stat(root)
        sha256_hash.update(f"DIR:{root}".encode())
        sha256_hash.update(f"MODE:{stat.S_IMODE(dir_stat.st_mode)}".encode())
        sha256_hash.update(f"UID:{dir_stat.st_uid}".encode())
        sha256_hash.update(f"GID:{dir_stat.st_gid}".encode())
        sha256_hash.update(f"MTIME:{dir_stat.st_mtime}".encode())
        
        # 파일 목록을 정렬하여 일관된 순서 보장
        for file in sorted(files):
            filepath = os.path.join(root, file)
            file_stat = os.stat(filepath)
            
            # 파일 메타데이터를 해시에 추가
            sha256_hash.update(f"FILE:{filepath}".encode())
            sha256_hash.update(f"MODE:{stat.S_IMODE(file_stat.st_mode)}".encode())
            sha256_hash.update(f"UID:{file_stat.st_uid}".encode())
            sha256_hash.update(f"GID:{file_stat.st_gid}".encode())
            sha256_hash.update(f"SIZE:{file_stat.st_size}".encode())
            sha256_hash.update(f"MTIME:{file_stat.st_mtime}".encode())
            sha256_hash.update(f"CTIME:{file_stat.st_ctime}".encode())
            
            # 소유자와 그룹 이름 추가 (UID/GID가 변경되지 않아도 이름이 변경될 수 있음)
            try:
                owner = pwd.getpwuid(file_stat.st_uid).pw_name
                group = grp.getgrgid(file_stat.st_gid).gr_name
                sha256_hash.update(f"OWNER:{owner}".encode())
                sha256_hash.update(f"GROUP:{group}".encode())
            except KeyError:
                # UID/GID에 해당하는 사용자/그룹이 없는 경우
                pass
            
            # 파일 내용을 해시에 추가
            try:
                with open(filepath, "rb") as f:
                    content = f.read()
                    if content:
                        sha256_hash.update(content)
                    else:
                        sha256_hash.update(b"empty_file")
            except PermissionError:
                # 읽기 권한이 없는 경우
                sha256_hash.update(b"no_read_permission")
            except IOError as e:
                # 기타 IO 오류
                sha256_hash.update(f"io_error:{str(e)}".encode())

    return sha256_hash.hexdigest()

def register_hash(image_name):
    """해시값을 계산하고 서버에 등록하는 함수"""
    try:
        if ':' not in image_name:
            image_name += ':latest'

        image_hash = calculate_hash(image_name)
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "apikey": API_KEY,
            "docker_image_name": image_name,
            "docker_image_hash": image_hash
        }
        response = requests.post(f"{SERVER_URL}/api/register-docker-hash", headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            return True
        else:
            return False

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

def check_integrity(image_name):
    """해시값을 계산하고 서버에 검증 요청을 보내는 함수"""
    try:
        if ':' not in image_name:
            image_name += ':latest'

        image_hash = calculate_hash(image_name)
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "apikey": API_KEY,
            "docker_image_name": image_name,
            "docker_image_hash": image_hash
        }
        response = requests.post(f"{SERVER_URL}/api/verify-docker-hash", headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            return result["match"]
        elif response.status_code == 404:
            return False
        else:
            return False

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False