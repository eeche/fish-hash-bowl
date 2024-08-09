import sys
import json
import requests
from pathlib import Path

# 설정 파일 로드
config_path = Path("/opt/company-security-solution/client/config/config.json")
with config_path.open() as f:
    config = json.load(f)

CENTRAL_SERVER_URL = config['central_server_url']
API_KEY = config['api_key']

def get_stored_hash(image_id):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(f"{CENTRAL_SERVER_URL}/images/{image_id}", headers=headers)
    if response.status_code == 200:
        return response.json()["hash"]
    return None

def check_integrity(hash_result):
    hash_data = json.loads(hash_result)
    image_id = hash_data['image_id']
    current_hash = hash_data['hash']
    
    stored_hash = get_stored_hash(image_id)
    if stored_hash is None:
        print(f"No hash found for image: {image_id}")
        return False
    
    return current_hash == stored_hash

if __name__ == "__main__":
    hash_result = sys.argv[1]
    if check_integrity(hash_result):
        print("Integrity check passed")
        sys.exit(0)
    else:
        print("Integrity check failed")
        sys.exit(1)