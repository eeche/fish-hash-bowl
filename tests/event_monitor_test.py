# import docker
# import logging
# from hash_registrar_test import main as register_hash
# from integrity_checker_test import check_integrity
# from image_utils_test import get_image_layer_path

# # 로깅 설정
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# client = docker.from_env()

# def handle_image_create(image_name):
#     try:
#         logger.info(f"Handling image create event for: {image_name}")
#         get_image_layer_path(image_name)
#         register_hash(image_name)
#         logger.info(f"Hash registration process completed for image: {image_name}")
#     except Exception as e:
#         logger.error(f"Error handling image create event for {image_name}: {str(e)}")

# def handle_container_event(image_name):
#     try:
#         logger.info(f"Handling container event for image: {image_name}")
#         if check_integrity(image_name):
#             logger.info(f"Integrity check passed for image: {image_name}")
#             return True
#         else:
#             logger.warning(f"Integrity check failed for image: {image_name}")
#             # TODO: 여기에 실패 시 수행할 작업 추가 (예: 컨테이너 중지, 알림 발송 등)
#             return False
#     except Exception as e:
#         logger.error(f"Error handling container event for {image_name}: {str(e)}")
#         return False

# def main():
#     logger.info("Starting Docker event monitor")
#     try:
#         for event in client.events(decode=True):
#             logger.info(f"Received event: {event}")
            
#             if event['Type'] == 'image' and event['Action'] in ['build', 'pull']:
#                 handle_image_create(event['id'])
#             elif event['Type'] == 'container' and event['Action'] in ['run', 'start', 'create', 'restart']:
#                 image_name = event['Actor']['Attributes'].get('image')
#                 if image_name:
#                     handle_container_event(image_name)
#                 else:
#                     logger.warning(f"No image name found for container event: {event}")
#     except KeyboardInterrupt:
#         logger.info("Stopping Docker event monitor")
#     except Exception as e:
#         logger.error(f"Unexpected error in event monitor: {str(e)}")

# if __name__ == "__main__":
#     main()

# # TODO:
# # 1. 이벤트 처리 중 예외 발생 시 복구 메커니즘 구현
# # 2. 다양한 Docker 이벤트에 대한 처리 확장 (예: 이미지 삭제, 컨테이너 중지 등)
# # 3. 성능 모니터링 및 최적화 (예: 이벤트 처리 지연 시간 측정)
# # 4. 중앙 서버와의 연결 끊김 시 로컬 캐시 사용 및 재연결 로직 구현
# # 5. 무결성 검사 실패 시 자동 대응 정책 구현 (예: 컨테이너 자동 중지, 관리자 알림 등)





import docker
import logging
from hash_registrar_test import main as register_hash
from integrity_checker_test import check_integrity
from image_utils_test import get_image_layer_path

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = docker.from_env()

def remove_container(container_id):
    """컨테이너를 삭제하는 함수"""
    try:
        container = client.containers.get(container_id)
        container.remove(force=True)
        logger.info(f"Container {container_id} removed successfully")
    except Exception as e:
        logger.error(f"Failed to remove container {container_id}: {str(e)}")

def handle_image_create(image_name):
    try:
        logger.info(f"Handling image create event for: {image_name}")
        get_image_layer_path(image_name)
        register_hash(image_name)
        logger.info(f"Hash registration process completed for image: {image_name}")
    except Exception as e:
        logger.error(f"Error handling image create event for {image_name}: {str(e)}")

def handle_container_event(image_name, container_id, action):
    try:
        logger.info(f"Handling container event for image: {image_name}, action: {action}")
        if check_integrity(image_name):
            logger.info(f"Integrity check passed for image: {image_name}")
            return True
        else:
            logger.warning(f"Integrity check failed for image: {image_name}")
            remove_container(container_id)
            return False
    except Exception as e:
        logger.error(f"Error handling container event for {image_name}: {str(e)}")
        return False

def main():
    logger.info("Starting Docker event monitor")
    recent_containers = {}  # 최근에 처리한 컨테이너 추적
    try:
        for event in client.events(decode=True):
            logger.debug(f"Received event: {event}")
            
            if event['Type'] == 'image' and event['Action'] in ['build', 'pull']:
                handle_image_create(event['id'])
            elif event['Type'] == 'container' and event['Action'] in ['create', 'start']:
                image_name = event['Actor']['Attributes'].get('image')
                container_id = event['Actor']['ID']
                if image_name:
                    if event['Action'] == 'create':
                        integrity_result = handle_container_event(image_name, container_id, event['Action'])
                        recent_containers[container_id] = integrity_result
                        if not integrity_result:
                            remove_container(container_id)
                    elif event['Action'] == 'start':
                        if container_id in recent_containers:
                            if not recent_containers[container_id]:
                                remove_container(container_id)
                            del recent_containers[container_id]  # 처리 후 딕셔너리에서 제거
                        else:
                            # 'create' 이벤트를 놓친 경우 여기서 처리
                            integrity_result = handle_container_event(image_name, container_id, event['Action'])
                            if not integrity_result:
                                remove_container(container_id)
                else:
                    logger.warning(f"No image name found for container event: {event}")
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