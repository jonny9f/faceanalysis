import time
import traceback
import cv2
from deepface import DeepFace

# Load the pre-trained emotion detection model
model = DeepFace.build_model("Emotion")

# Define emotion labels
emotion_labels = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

# Load face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Start capturing video
cap = cv2.VideoCapture(1)

last_face_coordinates = None
last_emotions_text = ""
last_emotion = None
emotion_labels = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if not ret:
        print("Unable to capture video")
        time.sleep(0.5)
        continue

    # Convert frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(128, 128))

    face_detected = False

    for (x, y, w, h) in faces:
        face_detected = True
        last_face_coordinates = (x, y, w, h)

        # Extract the face ROI (Region of Interest)
        face_roi = gray_frame[y:y + h, x:x + w]
        resized_face = cv2.resize(face_roi, (48, 48), interpolation=cv2.INTER_AREA)
        normalized_face = resized_face / 255.0
        reshaped_face = normalized_face.reshape(1, 48, 48, 1)

        preds = model.predict(reshaped_face)
        emotion = emotion_labels[preds.argmax()]
        last_emotion = emotion

        # Create a string to display all emotions with their probabilities
        last_emotions_text = ""
        for i, prob in enumerate(preds[0]):
            last_emotions_text += f"{emotion_labels[i]}: {prob * 100:.2f}%\n"

    # Use the last detected face and emotions if no face is detected in the current frame
    if last_face_coordinates is not None:
        (x, y, w, h) = last_face_coordinates
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(frame, last_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        for idx, line in enumerate(last_emotions_text.split('\n')):
            cv2.putText(frame, line, (x, y + h + 20 + (idx * 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # Display the resulting frame
    cv2.imshow('Real-time Emotion Detection', frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()