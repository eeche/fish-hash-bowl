import sys
import docker
from image_utils import register_hash

def main(image_name):
    """메인 함수: 이미지 해시 계산 및 등록 과정을 관리"""
    try:
        # 이미지 존재 여부 확인
        client = docker.from_env()
        try:
            client.images.get(image_name)
        except docker.errors.ImageNotFound:
            print(f"Error: Image '{image_name}' not found.")
            return False

        success = register_hash(image_name)
        if success:
            print(f"Hash for image '{image_name}' registered successfully.")
            return True
        else:
            print(f"Failed to register hash for image '{image_name}'")
            return False

    except Exception as e:
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python hash_registrar.py <image_name>")
        sys.exit(1)
    
    image_name = sys.argv[1]
    if main(image_name):
        sys.exit(0)
    else:
        sys.exit(1)