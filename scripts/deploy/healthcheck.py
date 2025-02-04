import requests
import sys

HEALTHCHECK_PORT = 8080  # Match your bot's healthcheck port

def check_health():
    try:
        response = requests.get(f"http://localhost:{HEALTHCHECK_PORT}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

if __name__ == "__main__":
    if check_health():
        print("✅ Service healthy")
        sys.exit(0)
    else:
        print("❌ Service unavailable")
        sys.exit(1)