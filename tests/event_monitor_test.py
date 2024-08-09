import docker
from image_utils_test import calculate_hash, get_stored_hash, register_hash, get_image_layer_path

client = docker.from_env()

def handle_image_create(image_name):
    get_image_layer_path(image_name)
    register_hash(image_name)

def handle_container_event(image_name):
    current_hash = calculate_hash(image_name)
    stored_hash = get_stored_hash(image_name)
    
    if stored_hash is None:
        print(f"No hash found for image: {image_name}")
        return False
    
    if current_hash == stored_hash:
        print(f"Integrity check passed for image: {image_name}")
        return True
    else:
        print(f"Integrity check failed for image: {image_name}")
        # 여기에 실패 시 수행할 작업 추가 (예: 컨테이너 중지, 알림 발송 등)
        return False

for event in client.events(decode=True):
    print(f"Received event: {event}")
    if event['Type'] == 'image' and event['Action'] in ['build', 'pull']:
        handle_image_create(event['id'])
    elif event['Type'] == 'container' and event['Action'] in ['run', 'start', 'create', 'restart']:
        image_name = event['Actor']['Attributes']['Image']
        handle_container_event(image_name)

# TODO:
# 1. 이벤트 처리 중 예외 발생 시 복구 메커니즘 구현
# 2. 다양한 Docker 이벤트에 대한 처리 확장 (예: 이미지 삭제, 컨테이너 중지 등)
# 3. 이벤트 처리 결과에 대한 상세 로깅 구현
# 4. 성능 모니터링 및 최적화 (예: 이벤트 처리 지연 시간 측정)
# 5. 중앙 서버와의 연결 끊김 시 로컬 캐시 사용 및 재연결 로직 구현
# 6. 무결성 검사 실패 시 자동 대응 정책 구현 (예: 컨테이너 자동 중지, 관리자 알림 등)