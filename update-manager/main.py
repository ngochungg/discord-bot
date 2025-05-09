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
            "output": result or "✅ Update bot completed."
        }), 200
    except subprocess.CalledProcessError as e:
        return jsonify({
            "success": False,
            "output": e.stderr or e.stdout or str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=20000)