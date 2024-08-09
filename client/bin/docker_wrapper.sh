#!/bin/bash

SCRIPT_DIR="/opt/company-security-solution"
LOG_DIR="/var/log/company-security-solution"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_DIR/security-check.log"
}

if [[ "$1" == "run" || "$1" == "create" ]]; then
    log "Performing security check for command: $@"
    image_id=$(docker inspect -f '{{.Id}}' $2 | cut -d: -f2)
    hash_result=$(curl -s "http://localhost:5000/hash/$image_id")
    python3 "$SCRIPT_DIR/lib/integrity_check.py" "$hash_result"
    if [ $? -ne 0 ]; then
        log "Security check failed. Container creation/execution aborted."
        echo "Security check failed. Container creation/execution aborted."
        exit 1
    fi
    log "Security check passed"
fi

/usr/bin/docker.original "$@"