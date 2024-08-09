import sys
import docker
from image_utils import calculate_hash, register_hash

def main(image_name):
    """메인 함수: 이미지 해시 계산 및 등록 과정을 관리"""
    try:
        client = docker.from_env()
        image = client.images.get(image_name)
        image_id = image.id.split(':')[1]
        image_hash = calculate_hash(image_id)
        register_hash(image_name, image_hash)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python hash_registrar.py <image_name>")
        sys.exit(1)
    
    image_name = sys.argv[1]
    main(image_name)

# TODO:
# 1. 이미지 태그 처리 개선 (예: 'latest' 태그 처리)
# 2. 대량의 이미지 처리를 위한 배치 처리 기능 구현
# 3. 이미지 메타데이터 추가 저장 (예: 생성 시간, 크기 등)
# 4. 해시 등록 실패 시 재시도 로직 구현
# 5. 로깅 기능 강화