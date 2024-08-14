import sys
from image_utils_test import calculate_hash, get_stored_hash

def check_integrity(image_name):
    """이미지의 무결성을 검사하는 함수"""
    try:
        # ':' 태그가 없으면 ':latest' 추가
        if ':' not in image_name:
            image_name += ':latest'

        current_hash = calculate_hash(image_name)
        stored_hash = get_stored_hash(image_name)
        
        if stored_hash is None:
            print(f"No hash found for image: {image_name}")
            return False
        
        if current_hash == stored_hash:
            print(f"Integrity check passed for image: {image_name}")
            print(f"Current hash: {current_hash}")
            print(f"Stored hash:  {stored_hash}")
            return True
        else:
            print(f"Integrity check failed for image: {image_name}")
            print(f"Current hash: {current_hash}")
            print(f"Stored hash:  {stored_hash}")
            return False

    except Exception as e:
        print(f"Error during integrity check: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python integrity_checker_test.py <image_name>")
        sys.exit(1)

    image_name = sys.argv[1]
    if check_integrity(image_name):
        sys.exit(0)
    else:
        sys.exit(1)

# TODO:
# 1. 상세한 로깅 추가
# 2. 무결성 검사 실패 시 추가 조치 구현 (예: 관리자 알림)
# 3. 성능 메트릭 수집 (예: 검사 소요 시간)
# 4. 병렬 처리를 통한 성능 개선 (대규모 이미지 처리 시)