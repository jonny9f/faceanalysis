import streamlit as st
import requests
import cv2
import base64
import threading
import time
from streamlit_webrtc import webrtc_streamer, VideoHTMLAttributes
import json

# Function to analyze the face using a remote service
def analyze_face(img):
    url = 'http://localhost:5000/api/v1/analyse'
    headers = {'Content-Type': 'application/json'}
    data = {"image": img }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

# Callback function for the webcam stream
lock = threading.Lock()
img_container = {"img": None}

def callback(frame):
    try:
        img = frame.to_ndarray(format="bgr24")
        with lock:
            img_container["img"] = img
        return frame
    except Exception as e:
        print(e)
        return frame

# Webcam streamer setup
ctx = webrtc_streamer(key="sample", video_frame_callback=callback, media_stream_constraints={"video": True})

# Main loop for capturing and analyzing images
placeholder = st.empty()

while ctx.state.playing:
    with lock:
        img = img_container["img"]
    if img is None:
        continue
    
    base64_img = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
    response = analyze_face(base64_img)
    time.sleep(0.2)
    with placeholder.container():
        st.write(response)
