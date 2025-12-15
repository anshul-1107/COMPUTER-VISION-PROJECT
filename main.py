import cv2
import threading
from src.detection.detector import SurveillanceSystem
from flask import Flask, render_template, Response, jsonify
import time

app = Flask(__name__)
system = None

def get_system():
    global system
    if system is None:
        system = SurveillanceSystem()
    return system

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            time.sleep(0.1)

@app.route('/video_feed')
def video_feed():
    try:
        return Response(gen(get_system()),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Camera error: {e}")
        return str(e)

@app.route('/status')
def status():
    sys = get_system()
    # Get latest log if available
    logs = sys.notifier.recent_logs if hasattr(sys, 'notifier') else []
    
    # Determine overall status
    current_status = "Active Monitoring"
    if logs:
        last_log = logs[0]
        # logic to see if recent (e.g. within 10 seconds)
        # simplistic for now
        current_status = f"Last Alert: {last_log['message']}"

    return jsonify({
        "status": current_status, 
        "logs": logs
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
