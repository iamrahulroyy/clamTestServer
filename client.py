import requests
import sys
from pathlib import Path

API_URL = "http://127.0.0.1:8000/scan" 

def scan_file(filepath: str):
    path = Path(filepath)
    if not path.exists():
        print(f"❌ File not found: {filepath}")
        return

    with open(filepath, "rb") as f:
        files = {"file": (path.name, f, "application/octet-stream")}
        try:
            response = requests.post(API_URL, files=files)
            response.raise_for_status()
            print("✅ Server Response:", response.json())
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Request failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <file_path>")
        sys.exit(1)

    scan_file(sys.argv[1])
