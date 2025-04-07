from flask import Flask
import subprocess
import sys

app = Flask(__name__)

def start_scripts():
    try:
        if sys.platform == "win32":
            subprocess.Popen("start cmd /k python accesscamera.py", shell=True)
            subprocess.Popen("start cmd /k python face_recognition_final.py", shell=True)
            subprocess.Popen("start cmd /k python cam12.py", shell=True)  # Renamed file (was 1,2-cam.py)

        print("Scripts started in separate terminals.")
    except Exception as e:
        print(f"Error starting scripts: {e}")

if __name__ == '__main__':
    start_scripts()  # <-- Scripts auto-start here
    app.run(host='0.0.0.0', port=4000)
