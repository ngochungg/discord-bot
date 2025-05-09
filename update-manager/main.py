from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route("/update", methods=["POST"])
def update():
    try:
        # Chuyển lên thư mục gốc project
        subprocess.run(["bash", "update_bot.sh"], cwd="/app/update-manager", check=True)
        return jsonify(status="success", message="Update triggered"), 200
    except subprocess.CalledProcessError as e:
        return jsonify(status="error", message=str(e)), 500

if __name__ == "__main__":
    # Chạy trên port 8000, host 0.0.0.0 để bot container có thể gọi
    app.run(host="0.0.0.0", port=8000)
