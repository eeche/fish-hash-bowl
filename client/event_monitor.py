import docker
import logging
from hash_registrar import main as register_hash
from integrity_checker import main as check_integrity

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = docker.from_env()

def remove_container(container_id):
    try:
        container = client.containers.get(container_id)
        container.remove(force=True)
        return True
    except Exception:
        return False

def handle_image_event(image_name):
    try:
        return register_hash(image_name)
    except Exception:
        return False

def check_container_integrity(image_name):
    try:
        return check_integrity(image_name)
    except Exception:
        return False

def main():
    try:
        for event in client.events(decode=True):
            
            if event['Type'] == 'image' and event['Action'] in ['pull', 'build']:
                handle_image_event(event['id'])
            
            elif event['Type'] == 'container' and event['Action'] in ['create', 'start']:
                image_name = event['Actor']['Attributes'].get('image')
                container_id = event['Actor']['ID']
                
                integrity_result = check_container_integrity(image_name)
                if not integrity_result:
                    remove = remove_container(container_id)
                    if remove:
                        print(f"Container {container_id} removed due to integrity check failure")

    except KeyboardInterrupt:
        logger.info("Stopping Docker event monitor")
    except Exception as e:
        logger.error(f"Unexpected error in event monitor: {str(e)}")

if __name__ == "__main__":
    main()