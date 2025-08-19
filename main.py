import subprocess
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()

CLAMSCAN_CMD = "clamscan"  # works if clamav is installed

def scan_bytes(file_bytes: bytes) -> bool:
    """
    Scan raw file bytes with ClamAV and return True if clean, False if infected.
    """
    try:
        # Run clamscan with "-" so it reads from stdin
        result = subprocess.run(
            [CLAMSCAN_CMD, "-"],   # "-" means read from stdin
            input=file_bytes,
            capture_output=True,
            text=True,
            check=False
        )

        # Debug: you can inspect result.stdout if needed
        if "Infected files: 1" in result.stdout:
            return False  # malware detected
        return True       # clean

    except Exception as e:
        raise RuntimeError(f"Scan failed: {e}")

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
    uvicorn.run(app, host="0.0.0.0", port=8000)