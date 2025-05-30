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

        if process.returncode == 0:
            return jsonify({
                "success": True,
                "output": process.stdout or "✅ Update bot completed."
            }), 200
        else:
            return jsonify({
                "success": False,
                "output": process.stderr or "❌ Update failed."
            }), 500

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