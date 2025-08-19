import os
import subprocess
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()

CLAMSCAN_CMD = "clamscan"  # works if clamav is installed

def scan_bytes(file_bytes: bytes) -> bool:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [CLAMSCAN_CMD, tmp_path],
            capture_output=True,
            text=True,
            check=False
        )
        if "Infected files: 1" in result.stdout:
            return False
        return True
    finally:
        os.remove(tmp_path)

@app.post("/scan")
async def scan_endpoint(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        is_clean = scan_bytes(file_bytes)
        return {
            "filename": file.filename,
            "clean": is_clean
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)