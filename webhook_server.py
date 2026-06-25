import os
import hmac
import hashlib
import threading
from flask import Flask, request, jsonify
from reviewer_agent import run_reviewer_pipeline

app = Flask(__name__)
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "llm")

def verify_signature(data, signature):
    """Validate incoming HMAC-SHA256 GitHub Signatures"""
    key = GITHUB_WEBHOOK_SECRET.encode()
    mac = hmac.new(key, msg=data, digestmod=hashlib.sha256)
    expected = "sha256=" + mac.hexdigest()
    return hmac.compare_digest(expected, signature)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/webhook", methods=["POST"])
def github_webhook():
    #sig = request.headers.get("X-Hub-Signature-256", "")
    #if not verify_signature(request.data, sig):
     #   return jsonify({"error": "Bad signature matching failed"}), 403
        
    payload = request.get_json()
    if not payload or "commits" not in payload:
        return jsonify({"message": "Not a commit event, ignored"}), 200
        
    repo = payload.get("repository", {}).get("full_name", "unknown/repo")
    branch = payload.get("ref", "refs/heads/main").split("/")[-1]
    
    # Filter for target updates
    changed = [f for commit in payload["commits"] for f in commit.get("modified", [])]
    python_files = [f for f in changed if f.endswith(".py")]
    
    if not python_files:
        return jsonify({"message": "No python modifications found"}), 200
        
    # Execute async via background process threads to decouple server time-outs
    thread = threading.Thread(
        target=run_reviewer_pipeline,
        args=(repo, branch, python_files, payload)
    )
    thread.start()
    
    return jsonify({"message": "Review started"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)