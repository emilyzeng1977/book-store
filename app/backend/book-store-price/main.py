from app import app
import logging

def get_version() -> str:
    try:
        with open("version.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"

if __name__ == '__main__':
    version = get_version()
    logging.info(f"Starting Book Store Price version: {version}")
    app.run(debug=True, host='0.0.0.0', port=5000)
