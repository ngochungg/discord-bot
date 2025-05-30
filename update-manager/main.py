import time
import psutil
from flask import Flask, jsonify
import subprocess
import speedtest

app = Flask(__name__)

@app.route("/update", methods=["POST"])
def update():
    try:
        process = subprocess.Popen(
            ["bash", "./update_bot.sh"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout_bytes, stderr_bytes = process.communicate()
        return_code = process.returncode

        # Decode rõ ràng từ bytes -> string
        stdout = stdout_bytes.decode("utf-8").strip()
        stderr = stderr_bytes.decode("utf-8").strip()

        # ⚠️ Trả kết quả về trước — bot sẽ nhận được tin nhắn
        response = {
            "success": return_code == 0,
            "output": stdout if return_code == 0 else stderr
        }

        # ✅ Sau khi trả lời rồi mới restart
        if return_code == 0 and "Already up to date." not in stdout:
            time.sleep(10)
            subprocess.Popen(["docker", "restart", "the-herta"])

        return jsonify(response), 200 if return_code == 0 else 500

    except Exception as e:
        return jsonify({
            "success": False,
            "output": f"❌ Exception occurred: {str(e)}"
        }), 500

@app.route('/network-speed')
def network_speed():
    st = speedtest.Speedtest()
    st.get_best_server()
    download_bps = st.download()
    upload_bps = st.upload()

    # Chuyển từ bit/s sang Mbit/s
    return jsonify({
        "upload_mbps": round(upload_bps / 1_000_000, 2),
        "download_mbps": round(download_bps / 1_000_000, 2)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=20000)