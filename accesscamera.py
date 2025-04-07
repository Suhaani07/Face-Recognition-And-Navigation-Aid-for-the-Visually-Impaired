import cv2
import threading
from flask import Flask, Response
import time

# Flask app to serve the video stream
app = Flask(__name__)

# IP camera URL
camera_url = "http://192.168.41.103:4747/video"

# Global variable to store the latest frame
frame = None

def capture_frames():
    global frame
    while True:
        cap = cv2.VideoCapture(camera_url)
        if not cap.isOpened():
            print("Failed to connect to camera. Retrying...")
            time.sleep(2)
            continue
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Lost connection to camera. Reconnecting...")
                break  # Break the loop to attempt reconnection
        
        cap.release()
        time.sleep(2)  # Wait before retrying

def generate():
    """Generate frames for the HTTP stream"""
    global frame
    while True:
        if frame is not None:
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Start frame capture in a separate thread
threading.Thread(target=capture_frames, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)