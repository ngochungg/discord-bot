import time
import psutil
from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route("/update", methods=["POST"])
def update():
    try:
        result = subprocess.Popen(["bash", "./update_bot.sh"])
        # return "Update triggered successfully", 200
        return jsonify({
            "success": True,
            "output": result.stdout or "✅ Update bot completed."
        }), 200
    except subprocess.CalledProcessError as e:
        return jsonify({
            "success": False,
            "output": e.stderr or e.stdout or str(e)
        }), 500

@app.route('/network-speed')
def network_speed():
    net1 = psutil.net_io_counters()
    time.sleep(1)
    net2 = psutil.net_io_counters()

    upload_kb = (net2.bytes_sent - net1.bytes_sent) / 1024
    download_kb = (net2.bytes_recv - net1.bytes_recv) / 1024

    return jsonify({
        "upload_kb": round(upload_kb, 1),
        "download_kb": round(download_kb, 1)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=20000)