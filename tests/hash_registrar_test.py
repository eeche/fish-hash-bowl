import sys
import docker
from image_utils_test import calculate_hash, register_hash

def main(image_name):
    """메인 함수: 이미지 해시 계산 및 등록 과정을 관리"""
    try:
        # ':' 태그가 없으면 ':latest' 추가
        if ':' not in image_name:
            image_name += ':latest'

        # 이미지 존재 여부 확인
        client = docker.from_env()
        try:
            client.images.get(image_name)
        except docker.errors.ImageNotFound:
            print(f"Error: Image '{image_name}' not found.")
            return

        # 해시 계산 및 등록
        calculated_hash = calculate_hash(image_name)
        print(f"Calculated hash for {image_name}: {calculated_hash}")

        register_hash(image_name)
        print(f"Hash for {image_name} registered successfully.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python hash_registrar_test.py <image_name>")
        sys.exit(1)
    
    image_name = sys.argv[1]
    main(image_name)

# TODO:
# 1. 대량의 이미지 처리를 위한 배치 처리 기능 구현
# 2. 이미지 메타데이터 추가 저장 (예: 생성 시간, 크기 등)
# 3. 해시 등록 실패 시 재시도 로직 구현
# 4. 로깅 기능 강화
# 5. 성능 최적화 (예: 병렬 처리)