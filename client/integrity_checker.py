import sys
from image_utils import check_integrity

def main(image_name):
    try: 
        match = check_integrity(image_name)
        if match:
            print(f"Integrity check passed for image: '{image_name}'")
            return True
        else:
            print(f"Integrity check failed for image: '{image_name}'")
            return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python integrity_checker.py <image_name>")
        sys.exit(1)

    image_name = sys.argv[1]
    if main(image_name):
        sys.exit(0)
    else:
        sys.exit(1)