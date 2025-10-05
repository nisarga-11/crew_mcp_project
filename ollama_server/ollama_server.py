psql -h 127.0.0.1 -U postgres -d postgres
from flask import Flask, request, jsonify
import requests
import os
import subprocess
import time

app = Flask(__name__)

# Load environment variables
MODEL = os.getenv("OLLAMA_MODEL", "llama2")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
OLLAMA_CMD = os.getenv("OLLAMA_CMD", "ollama serve")  # Command to start Ollama
OLLAMA_LOG = os.getenv("OLLAMA_LOG", "ollama.log")    # Optional log file

# -----------------------------
# Start Ollama server if not running
# -----------------------------
def start_ollama():
    try:
        # Check if Ollama is reachable before starting
        response = requests.get(f"{OLLAMA_API_URL}/api/status", timeout=3)
        if response.status_code == 200:
            print("✅ Ollama server already running.")
            return
    except Exception:
        print("ℹ Ollama server not running. Starting it now...")

    # Start Ollama as a background process
    with open(OLLAMA_LOG, "a") as log_file:
        subprocess.Popen(
            OLLAMA_CMD.split(),
            stdout=log_file,
            stderr=log_file,
            start_new_session=True
        )
    print("🚀 Ollama server starting...")

    # Wait for Ollama to be ready
    for _ in range(10):
        try:
            response = requests.get(f"{OLLAMA_API_URL}/api/status", timeout=3)
            if response.status_code == 200:
                print("✅ Ollama server is up!")
                return
        except Exception:
            print("⏳ Waiting for Ollama server to start...")
            time.sleep(2)

    print("❌ Failed to start Ollama server within the expected time.")

# -----------------------------
# Flask routes
# -----------------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    model = data.get("model", MODEL)
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={"model": model, "prompt": prompt}
        )

        if response.status_code != 200:
            return jsonify({"error": "Ollama API error", "details": response.text}), 500

        return jsonify(response.json())

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Ollama server not responding. Please check logs."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Main entry
# -----------------------------
if __name__ == "__main__":
    start_ollama()  # Start Ollama server before launching Flask

    host = os.getenv("OLLAMA_HOST", "127.0.0.1")
    port = int(os.getenv("OLLAMA_PORT", "8000"))
    print(f"📡 Flask server running at http://{host}:{port}")
    app.run(host=host, port=port)
