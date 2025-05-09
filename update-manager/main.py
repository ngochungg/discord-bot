from flask import Flask
import subprocess

app = Flask(__name__)

@app.route("/update", methods=["POST"])
def update():
    try:
        subprocess.run(["bash", "./update_bot.sh"], check=True)
        return "Update triggered successfully", 200
    except subprocess.CalledProcessError as e:
        return f"Error: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=20000)