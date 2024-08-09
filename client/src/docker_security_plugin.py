from fastapi import FastAPI, HTTPException
import uvicorn
import os
import hashlib

app = FastAPI()

OVERLAY2_PATH = "/var/lib/docker/overlay2/"

def calculate_hash(path):
    sha256_hash = hashlib.sha256()
    for root, _, files in os.walk(path):
        for file in files:
            filepath = os.path.join(root, file)
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

@app.get("/hash/{image_id}")
async def get_hash(image_id: str):
    path = os.path.join(OVERLAY2_PATH, image_id)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Path not found: {path}")
    
    hash_value = calculate_hash(path)
    return {"image_id": image_id, "hash": hash_value}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)