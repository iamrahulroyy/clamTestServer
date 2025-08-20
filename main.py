import os
import subprocess
import tempfile
import time
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()

CLAMSCAN_CMD = "clamscan" 

def scan_bytes(file_bytes: bytes, filename: str) -> dict:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    start_time = time.time()
    try:
        result = subprocess.run(
            [CLAMSCAN_CMD, tmp_path],
            capture_output=True,
            text=True,
            check=False
        )
        end_time = time.time()

        clean = "Infected files: 0" in result.stdout
        infected = not clean
        infection_name = None

        if infected:
            for line in result.stdout.splitlines():
                if tmp_path in line and "FOUND" in line:
                    infection_name = line.split(":")[1].strip().replace(" FOUND", "")
                    break

        return {
            "filename": filename,
            "clean": clean,
            "infected": infected,
            "infection_name": infection_name,
            "scan_time_seconds": round(end_time - start_time, 4),
            "timestamp": datetime.utcnow().isoformat(),
            "raw_output": result.stdout.strip(),
        }
    finally:
        os.remove(tmp_path)


@app.post("/scan")
async def scan_endpoint(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        scan_report = scan_bytes(file_bytes, file.filename)
        return scan_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
