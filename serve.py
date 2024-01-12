# File: app.py (FastAPI Backend)
import logging
from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel, Field
from deepface import DeepFace
import cv2
import numpy as np
from cv2 import CascadeClassifier
import base64
from typing import Optional
from typing import Dict

app = FastAPI()

face_cascade = CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
logger = logging.getLogger(__name__)

model = DeepFace.build_model("Emotion")

class ImageData(BaseModel):
    image: str = Field(description="Base64 Encoded Image")
    
class FaceCoordinates(BaseModel):
    x: int
    y: int
    width: int
    height: int

class ResponseModel(BaseModel):
    face_coordinates: Optional[FaceCoordinates] = Field(None, description="Face Coordinates. None if no face detected.")
    predictions: Optional[dict] = Field(None, description="Predictions. None if no face detected.")
    emotion: Optional[str] = Field(None, description="Dominate emotion.  None if no face detected.")


@app.post('/api/v1/analyse', response_model=ResponseModel)
async def analyse_v1(data: ImageData):
    response = ResponseModel( 
        face_coordinates=None,
        predictions=None,
        emotion=None
    )
    try:
        encoded_data = data.image
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

        faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5, minSize=(128, 128))
        emotion = "Unknown"
 
        for (x, y, w, h) in faces:
            response.face_coordinates = FaceCoordinates(x=int(x), y=int(y), width=int(w), height=int(h))
            face_roi = gray_img[y:y+h, x:x+w]
            resized_face = cv2.resize(face_roi, (48, 48), interpolation=cv2.INTER_AREA)
            normalized_face = resized_face / 255.0
            reshaped_face = normalized_face.reshape(1, 48, 48, 1)
            preds = model.predict(reshaped_face)
            emotion = emotion_labels[preds.argmax()]

            predictions = {emotion_labels[i]: float(preds[0][i]) for i in range(len(emotion_labels))}

            response.predictions = predictions
            response.emotion = emotion

    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=f"Internal Server Error, {e}")

    print(response)
    return response



@app.get('/ping')
def ping():
    return {"result": "pong"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)


