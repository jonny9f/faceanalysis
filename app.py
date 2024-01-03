# File: app.py (Flask Backend)
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from deepface import DeepFace
import cv2
import numpy as np
import os
import base64
from cv2 import CascadeClassifier

app = Flask(__name__, static_folder="frontend/build/static", template_folder="frontend/build")


logger = logging.getLogger(__name__)

model = DeepFace.build_model("Emotion")

# @app.route("/")
# def hello():
#     return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        encoded_data = data['image'].split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)


        # Convert to grayscale
        face_cascade = CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect faces and analyze
        # Note: You might need to adapt this part based on your face detection and emotion analysis implementation
        faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(128, 128))
        emotion = "Unknown"
        response = {}
        for (x, y, w, h) in faces:
            face_roi = gray_img[y:y+h, x:x+w]
            resized_face = cv2.resize(face_roi, (48, 48), interpolation=cv2.INTER_AREA)
            normalized_face = resized_face / 255.0
            reshaped_face = normalized_face.reshape(1, 48, 48, 1)
            preds = model.predict(reshaped_face)
            emotion = emotion_labels[preds.argmax()]

            # Convert predictions to a readable format
            predictions = {emotion_labels[i]: float(preds[0][i]) for i in range(len(emotion_labels))}

            # Add face coordinates and predictions to the response
            response = {
                "face_coordinates": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                "predictions": predictions,
                "emotion": emotion
            }
    except Exception as e:
        logger.error(e)
        response = {"error": str(e)}

    return response



if __name__ == "__main__":
    app.run(host='localhost', debug=True, threaded=False)
