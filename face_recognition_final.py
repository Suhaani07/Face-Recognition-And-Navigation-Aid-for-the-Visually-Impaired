import cv2
import numpy as np
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from sklearn.preprocessing import Normalizer
from deepface import DeepFace
from collections import Counter, defaultdict
import pyttsx3

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Load FaceNet model
model_name = "Facenet"
model = DeepFace.build_model(model_name)

# Load face cascade for detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Thread lock for synchronization
lock = threading.Lock()

# Dictionary to track the count of detected names
name_counter = defaultdict(int)

def get_embedding(face):
    """Extracts face embedding using DeepFace."""
    try:
        face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)  # Convert to RGB
        embedding = DeepFace.represent(face_rgb, model_name=model_name, enforce_detection=False)

        if not embedding:
            return None

        return embedding[0]['embedding']
    except Exception as e:
        print(f"Error in get_embedding: {e}")
        return None

def load_saved_faces(directory):
    """Loads saved face embeddings for known people."""
    known_face_embeddings = []
    known_face_names = []

    for person_name in os.listdir(directory):
        person_folder = os.path.join(directory, person_name)
        if os.path.isdir(person_folder):
            for filename in os.listdir(person_folder):
                if filename.endswith((".jpg", ".png", ".jpeg")):
                    image_path = os.path.join(person_folder, filename)
                    img = cv2.imread(image_path)
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                    for (x, y, w, h) in faces:
                        face = img[y:y+h, x:x+w]
                        embedding = get_embedding(face)
                        if embedding is not None:
                            known_face_embeddings.append(embedding)
                            known_face_names.append(person_name)

    return np.array(known_face_embeddings) if known_face_embeddings else np.empty((0, 128)), known_face_names

def decide_name(detected_names, threshold=0.4):
    """Determines the most frequently detected name."""
    if not detected_names:
        return "Unknown"

    name_counts = Counter(detected_names)
    for name, count in name_counts.items():
        if name != "Unknown" and count / len(detected_names) > threshold:
            return name
    
    return "Unknown"

# Load known faces
known_face_embeddings, known_face_names = load_saved_faces('C:/Users/Suhaani Aggarwal/Desktop/Major Project/Final Work/Saved_faces')

# Normalize embeddings if available
if known_face_embeddings.size > 0:
    normalizer = Normalizer(norm='l2')
    known_face_embeddings = normalizer.fit_transform(known_face_embeddings)
else:
    raise ValueError("No face embeddings were found in the saved faces directory.")

# Initialize camera
video_capture = cv2.VideoCapture("http://localhost:5000/video_feed")

# Track last dominant name
last_dominant_name = ""

def process_face(face, detected_names):
    """Processes a face, extracts embeddings, and determines identity."""
    global known_face_embeddings, known_face_names

    if face is None or face.size == 0:
        return "Unknown"

    embedding = get_embedding(face)
    if embedding is None:
        return "Unknown"

    embedding = np.expand_dims(embedding, axis=0)
    embedding = normalizer.transform(embedding)

    distances = np.linalg.norm(known_face_embeddings - embedding, axis=1)
    min_index = np.argmin(distances)

    name = known_face_names[min_index] if distances[min_index] < 0.6 else "Unknown"

    with lock:
        detected_names.append(name)

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("Failed to capture frame.")
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    detected_names = []
    face_regions = [(x, y, w, h) for (x, y, w, h) in faces if w * h > 30000]  # Filter small faces

    with ThreadPoolExecutor(max_workers=4) as executor:
        for (x, y, w, h) in face_regions:
            face = frame[y:y+h, x:x+w]
            executor.submit(process_face, face, detected_names)

    dominant_name = decide_name(detected_names, threshold=0.4)

    name_counter[dominant_name] += 1

    

    for (x, y, w, h) in face_regions:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, dominant_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        if name_counter[dominant_name] >= 10 and dominant_name != last_dominant_name:
            print(f"Detected person: {dominant_name}")
            engine.say(f"The person standing in front of you is {dominant_name}")
            engine.runAndWait()
            last_dominant_name = dominant_name
            name_counter.clear()

    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
