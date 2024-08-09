import sys
from image_utils import calculate_hash, get_stored_hash

def check_integrity(image_id):
    """이미지의 무결성을 검사하는 함수"""
    try:
        current_hash = calculate_hash(image_id)
        stored_hash = get_stored_hash(image_id)
        
        if stored_hash is None:
            print(f"No hash found for image: {image_id}")
            return False
        
        return current_hash == stored_hash
    except Exception as e:
        print(f"Error during integrity check: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python integrity_checker.py <image_id>")
        sys.exit(1)

    image_id = sys.argv[1]
    if check_integrity(image_id):
        print("Integrity check passed")
        sys.exit(0)
    else:
        print("Integrity check failed")
        sys.exit(1)

# TODO:
# 1. 상세한 로깅 추가
# 2. 무결성 검사 실패 시 추가 조치 구현 (예: 관리자 알림)
# 3. 성능 메트릭 수집 (예: 검사 소요 시간)
# 4. 병렬 처리를 통한 성능 개선 (대규모 이미지 처리 시)