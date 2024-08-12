import docker
import logging
from hash_registrar_test import main as register_hash
from integrity_checker_test import check_integrity
from image_utils_test import get_image_layer_path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = docker.from_env()

def remove_container(container_id):
    try:
        container = client.containers.get(container_id)
        container.remove(force=True)
        logger.info(f"Container {container_id} removed successfully")
    except Exception as e:
        logger.error(f"Failed to remove container {container_id}: {str(e)}")

def handle_image_event(image_name):
    try:
        logger.info(f"Handling image event for: {image_name}")
        get_image_layer_path(image_name)
        register_hash(image_name)
        logger.info(f"Hash registration process completed for image: {image_name}")
    except Exception as e:
        logger.error(f"Error handling image event for {image_name}: {str(e)}")

def check_container_integrity(image_name, container_id):
    try:
        logger.info(f"Checking integrity for image: {image_name}")
        if check_integrity(image_name):
            logger.info(f"Integrity check passed for image: {image_name}")
            return True
        else:
            logger.warning(f"Integrity check failed for image: {image_name}")
            return False
    except Exception as e:
        logger.error(f"Error checking integrity for {image_name}: {str(e)}")
        return False

def main():
    logger.info("Starting Docker event monitor")
    try:
        for event in client.events(decode=True):
            logger.debug(f"Received event: {event}")
            
            if event['Type'] == 'image' and event['Action'] in ['pull', 'build']:
                handle_image_event(event['id'])
            
            elif event['Type'] == 'container' and event['Action'] in ['create', 'start']:
                image_name = event['Actor']['Attributes'].get('image')
                container_id = event['Actor']['ID']
                
                if not image_name:
                    logger.warning(f"No image name found for container event: {event}")
                    continue
                
                integrity_result = check_container_integrity(image_name, container_id)
                if not integrity_result:
                    remove_container(container_id)

    except KeyboardInterrupt:
        logger.info("Stopping Docker event monitor")
    except Exception as e:
        logger.error(f"Unexpected error in event monitor: {str(e)}")

if __name__ == "__main__":
    main()

# TODO:
# 1. 이벤트 처리 중 예외 발생 시 복구 메커니즘 구현
# 2. 다양한 Docker 이벤트에 대한 처리 확장 (예: 이미지 삭제, 컨테이너 중지 등)
# 3. 성능 모니터링 및 최적화 (예: 이벤트 처리 지연 시간 측정)
# 4. 중앙 서버와의 연결 끊김 시 로컬 캐시 사용 및 재연결 로직 구현