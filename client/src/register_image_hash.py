import docker
import requests
import json
import sys
from pathlib import Path

# 설정 파일 로드
config_path = Path("/opt/company-security-solution/client/config/config.json")
with config_path.open() as f:
    config = json.load(f)

CENTRAL_SERVER_URL = config['central_server_url']
API_KEY = config['api_key']

def get_image_hash(image_id):
    response = requests.get(f"http://localhost:5000/hash/{image_id}")
    if response.status_code == 200:
        return response.json()['hash']
    else:
        raise Exception(f"Failed to calculate hash: {response.text}")

def register_hash(image_name, image_hash):
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

def main(image_name):
    try:
        client = docker.from_env()
        image = client.images.get(image_name)
        image_id = image.id.split(':')[1]
        image_hash = get_image_hash(image_id)
        register_hash(image_name, image_hash)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python register_image_hash.py <image_name>")
        sys.exit(1)
    
    image_name = sys.argv[1]
    main(image_name)