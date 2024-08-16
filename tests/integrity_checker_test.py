import sys
import requests
from image_utils_test import calculate_hash

API_KEY = "default_apikey"
SERVER_URL = "http://localhost:8080"

def check_integrity(image_name):
    """해시값을 계산하고 서버에 검증 요청을 보내는 함수"""
    try:
        # ':' 태그가 없으면 ':latest' 추가
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
            if result["match"]:
                print(f"Integrity check passed for image: {image_name}")
                print(f"Current hash: {image_hash}")
                print(f"Server message: {result['message']}")
                return True
            else:
                print(f"Integrity check failed for image: {image_name}")
                print(f"Current hash: {image_hash}")
                print(f"Server message: {result['message']}")
                return False
        elif response.status_code == 404:
            print(f"Error: {response.json()['message']}")
            return False
        else:
            print(f"Error: Failed to verify hash for {image_name}. Status code: {response.status_code}")
            print(f"Error message: {response.json().get('detail', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"Error during integrity check: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python integrity_checker.py <image_name>")
        sys.exit(1)

    image_name = sys.argv[1]
    if check_integrity(image_name):
        sys.exit(0)
    else:
        sys.exit(1)