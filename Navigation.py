import cv2
from ultralytics import YOLO
import pyttsx3
import cv2
import tempfile
import pyttsx3
from ultralytics import YOLO
from concurrent.futures import ThreadPoolExecutor
import os
import base64
import easyocr
import threading
import queue
import time



# Load EasyOCR Model
is_speaking = False  # Global flag to track speech status
speech_lock = threading.Lock()  # Lock to synchronize access
easyocr_reader = easyocr.Reader(['en'])
didreach=False
# API_KEY = ""
# os.environ['TOGETHER_API_KEY'] = API_KEY
import google.generativeai as genai

genai.configure(api_key='')

speech_queue = queue.Queue()

def speak_worker():
    global is_speaking
    while True:
        text = speech_queue.get()
        if text is None:  # Stop thread if None is received
            break
        with speech_lock:
            is_speaking = True  # Mark speaking as active
        
        engine.say(text)
        engine.runAndWait()
        with speech_lock:
            is_speaking = False  # Mark speaking as done
            print("Updated is_speaking:", is_speaking)  # Debugging output
        
        speech_queue.task_done()
# Start the speech synthesis thread
speech_thread = threading.Thread(target=speak_worker, daemon=True)
speech_thread.start()

# client = Together()
text = "Just reply with 1 word. What obstacle is blocking the path?"
text1 = "Just reply with Yes or No. Is there any object/obstacle blocking the path or is there anything kept on the floor? "



# Initialize the model from the .pt file
model = YOLO("C:/Users/Suhaani Aggarwal/Desktop/Major Project/Final Work/model.pt")

# Initialize text-to-speech engine
engine = pyttsx3.init()


def speak(text):
    speech_queue.put(text)  # Add text to the queue
# Route data: Each element describes action (e.g., "6 straight", "turn left")

locations = [
    "In front of Ladies Washroom",
    "Girls Exit",
    "In Front of Girls Conference Room",
    "Girls Side Lift",
    "AX 512",
    "Girls Corridor Center",
    "Room 508",
    "Room 510",
    "Room 506",
    "Boys Exit",
    "Boys Corridor Center",
    "Boys Side Lift",
    "Room 504",
    "In front of Boys washroom",
    "Boys Conference Room",
]


navigation_paths = {
    (0, 1): ["1","1","1","1","turn left", "1","1","1","reached"],
    (0, 2): ["1", "1", "1", "reached"],
    (0, 3): ["1","1","1","1", "1","1","1","reached"],
    (0, 4): ["1","1","1","1","turn right", "1","1","reached"],
    (0, 5):["1","1","1","1","reached"],
    (0, 6): ["1","1","1","1","turn left", "1","1","1","1","1","1","1","1","1","reached"],
    (0, 7): ["1","1","1","1","turn left", "1","1","1","1","1","1","reached"],
    (0, 8): ["1","1","1","1","turn left", "1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (0, 9): ["1","1","1","1","turn left", "1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (0, 10): ["1","1","1","1","turn left", "1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (0, 11): ["1","1","1","1","turn left", "1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn right","1","1","1","reached"],
    (0, 12): ["1","1","1","1","turn left", "1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (0, 13): ["1","1","1","1","turn left", "1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn left","1","1","1","reached"],
    (0, 14): ["1","1","1","1","turn left", "1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn left","1","1","1","1","1","1","reached"],

    (1, 0): ["1","1","1","turn right", "1","1","1","1","reached"],
    (1, 2): ["1","1","1","turn right", "1","1","1","1","1","1","1","reached"],
    (1, 3): ["1","1","1","turn left", "1","1","1","reached"],
    (1, 4): ["1","1","1","1","1","reached"],
    (1, 5):["1","1","1","reached"],
    (1, 6): ["1","1","1","1","1","1","reached"],
    (1, 7): ["1","1","1","reached"],
    (1, 8): ["1","1","1","1","1","1","1","1","1","reached"],
    (1, 9): ["1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (1, 10): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (1, 11): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn right","1","1","1","reached"],
    (1, 12): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (1, 13): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn left","1","1","1","reached"],
    (1, 14): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn left","1","1","1","1","1","1","reached"],

    (2, 0): ["1", "1", "1", "reached"],
    (2, 1): ["1","1","1","1","1","1","1","turn left", "1","1","1","reached"],
    (2, 3): ["1","1","1","1","1","1", "1","1","1","1","reached"],
    (2, 4): ["1","1","1","1","1","1","1","turn right", "1","1","reached"],
    (2, 5):["1","1","1","1","1","1","1","reached"],
    (2, 6): ["1","1","1","1","1","1","1","turn left", "1","1","1","1","1","1","1","1","1","reached"],
    (2, 7): ["1","1","1","1","1","1","1","turn left", "1","1","1","1","1","1","reached"],
    (2, 8): ["1","1","1","1","1","1","1","turn left", "1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (2, 9): ["1","1","1","1","1","1","1","turn left", "1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (2, 10):["1","1","1","1","1","1","1","turn left", "1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (2, 11):["1","1","1","1","1","1","1","turn left", "1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn right","1","1","1","reached"],
    (2, 12):["1","1","1","1","1","1","1","turn left", "1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (2, 13):["1","1","1","1","1","1","1","turn left", "1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn left","1","1","1","reached"],
    (2, 14):["1","1","1","1","1","1","1","turn left", "1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn left","1","1","1","1","1","1","reached"],

    (3, 0): ["1","1","1","1", "1","1","1","reached"],
    (3, 1): ["1", "1", "1", "turn right","1","1","1","reached"],
    (3, 2):  ["1","1","1","1","1","1","1", "1","1","1","reached"],
    (3, 4): ["1", "1", "1", "turn left","1","1","reached"],
    (3, 5):["1","1","1","reached"],
    (3, 6): ["1", "1", "1", "turn right","1","1","1","1","1","1","1","1","1","reached"],
    (3, 7): ["1", "1", "1", "turn right","1","1","1","1","1","1","reached"],
    (3, 8): ["1", "1", "1", "turn right","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (3, 9): ["1", "1", "1", "turn right","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (3, 10): ["1", "1", "1", "turn right","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (3, 11): ["1", "1", "1", "turn right","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn right","1","1","reached"],
    (3, 12): ["1", "1", "1", "turn right","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (3, 13): ["1", "1", "1", "turn right","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn left","1","1","1","1","reached"],
    (3, 14): ["1", "1", "1", "turn right","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn left","1","1","1","1","1","1","1","reached"],

    (4, 0): ["1","1","turn left", "1","1","1","1","reached"],
    (4, 1): ["1", "1", "1","1", "1", "reached"],
    (4, 2): ["1","1","turn left", "1","1","1","1","1","1","1","reached"],
    (4, 3): ["1","1","turn right", "1","1","1","reached"],
    (4, 5):["1","1","reached"],
    (4, 6): ["1", "1", "1","1", "1","1","1", "1","1","1", "1", "reached"],
    (4, 7): ["1", "1", "1","1", "1","1","1", "1", "reached"],
    (4, 8): ["1", "1", "1","1", "1","1","1", "1","1","1", "1","1","1", "1", "reached"],
    (4, 9): ["1", "1", "1","1", "1","1","1", "1","1","1", "1","1","1", "1", "1","1","1","reached"],
    (4, 10): ["1", "1", "1","1", "1","1","1", "1","1","1", "1","1","1", "1", "1","1","1","1","1","1","reached"],
    (4, 11): ["1", "1", "1","1", "1","1","1", "1","1","1", "1","1","1", "1", "1","1","1","1","1","1","turn right","1","1","1","reached"],
    (4, 12): ["1", "1", "1","1", "1","1","1", "1","1","1", "1","1","1", "1", "1","1","1","1","1","1","1","1","reached"],
    (4, 13):["1", "1", "1","1", "1","1","1", "1","1","1", "1","1","1", "1", "1","1","1","1","1","1","turn left","1","1","1","1","reached"],
    (4, 14): ["1", "1", "1","1", "1","1","1", "1","1","1", "1","1","1", "1", "1","1","1","1","1","1","turn left","1","1","1","1","1","1","1","reached"],

    (5, 0): ["1","1","1","1","reached"],
    (5, 1): ["1", "1", "1", "reached"],
    (5, 2): ["1","1","1","1", "1","1","1","reached"],
    (5, 3): ["1","1","1","reached"],
    (5, 4):["1","1","1","reached"],
    (5, 6): [ "1","1","1","1","1","1","1","1","1","reached"],
    (5, 7): [ "1","1","1","1","1","1","reached"],
    (5, 8): ["1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (5, 9): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (5, 10): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (5, 11): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn right","1","1","1","reached"],
    (5, 12): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (5, 13): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn left","1","1","1","reached"],
    (5, 14): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn left","1","1","1","1","1","1","reached"],

    (6, 0): ["1","1","1","1","1","1","1","1","1","turn right", "1","1","1","1","reached"],
    (6, 1): ["1","1","1","1","1","1","reached"],
    (6, 2): ["1","1","1","1","1","1","1","1","1","turn right", "1","1","1","1","1","1","1","reached"],
    (6, 3): ["1","1","1","1","1","1","1","1","1","turn left", "1","1","1","reached"],
    (6, 4):["1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (6, 5): ["1","1","1","1","1","1","1","1","1","reached"],
    (6, 7): ["1","1","1","reached"],
    (6, 8): ["1","1","1","reached"],
    (6, 9): ["1","1","1","1","1","1","reached"],
    (6, 10): ["1","1","1","1","1","1","1","1","1","1","reached"],
    (6, 11): ["1","1","1","1","1","1","1","1","1","1","turn right","1","1","1","reached"],
    (6, 12): ["1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (6, 13): ["1","1","1","1","1","1","1","1","1","1","turn left","1","1","1","1","reached"],
    (6, 14): ["1","1","1","1","1","1","1","1","1","1","turn left","1","1","1","1","1","1","1","reached"],

    (7, 0): ["1","1","1","1","1","1","turn right", "1","1","1","1","reached"],
    (7, 1): ["1","1","1","reached"],
    (7, 2): ["1","1","1","1","1","1","turn right", "1","1","1","1","1","1","1","reached"],
    (7, 3): ["1","1","1","1","1","1","turn left", "1","1","1","reached"],
    (7, 4):["1","1","1","1","1","1","1","1","1","reached"],
    (7, 5): ["1","1","1","1","1","1","reached"],
    (7, 6): ["1","1","1","reached"],
    (7, 8): ["1","1","1","1","1","1","reached"],
    (7, 9): ["1","1","1","1","1","1","1","1","1","reached"],
    (7, 10): ["1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (7, 11): ["1","1","1","1","1","1","1","1","1","1","1","1","1","turn right","1","1","1","reached"],
    (7, 12): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (7, 13): ["1","1","1","1","1","1","1","1","1","1","1","1","1","turn left","1","1","1","1","reached"],
    (7, 14): ["1","1","1","1","1","1","1","1","1","1","1","1","1","turn left","1","1","1","1","1","1","1","reached"],

    (8, 0): ["1","1","1","1","1","1","1","1","1","1","1","1","turn right", "1","1","1","1","reached"],
    (8, 1): ["1","1","1","1","1","1","1","1","1","reached"],
    (8, 2): ["1","1","1","1","1","1","1","1","1","1","1","1","turn right", "1","1","1","1","1","1","1","reached"],
    (8, 3): ["1","1","1","1","1","1","1","1","1","1","1","1","turn left", "1","1","1","reached"],
    (8, 4):["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (8, 5): ["1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (8, 6): ["1","1","1","reached"],
    (8, 7): ["1","1","1","1","1","1","reached"],
    (8, 9): ["1","1","1","reached"],
    (8, 10): ["1","1","1","1","1","1","1","reached"],
    (8, 11): ["1","1","1","1","1","1","1","turn right","1","1","1","reached"],
    (8, 12): ["1","1","1","1","1","1","1","1","1","reached"],
    (8, 13): ["1","1","1","1","1","1","1","turn left","1","1","1","1","reached"],
    (8, 14): ["1","1","1","1","1","1","1","turn left","1","1","1","1","1","1","1","reached"],

    (9, 0): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn right", "1","1","1","1","reached"],
    (9, 1): ["1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (9, 2): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn right", "1","1","1","1","1","1","1","reached"],
    (9, 3): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn left", "1","1","1","reached"],
    (9, 4): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (9, 5): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (9, 6): ["1","1","1","1","1","1","reached"],
    (9, 7): ["1","1","1","1","1","1","1","1","1","reached"],
    (9, 8): ["1","1","1","reached"],
    (9, 10): ["1","1","1","reached"],
    (9, 11): ["1","1","1","1","turn right","1","1","1","reached"],
    (9, 12): ["1","1","1","1","1","1","reached"],
    (9, 13): ["1","1","1","1","turn left","1","1","1","1","reached"],
    (9, 14): ["1","1","1","1","turn left","1","1","1","1","1","1","1","reached"],

    (10, 0): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn right", "1","1","1","1","reached"],
    (10, 1): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (10, 2): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn right", "1","1","1","1","1","1","1","reached"],
    (10, 3): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn left", "1","1","1","reached"],
    (10, 4): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (10, 5): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (10, 6): ["1","1","1","1","1","1","1","1","1","reached"],
    (10, 7): ["1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (10, 8): ["1","1","1","1","1","1","reached"],
    (10, 9): ["1","1","1","reached"],
    (10, 11): ["1","1","1","reached"],
    (10, 12): ["1","1","reached"],
    (10, 13): ["1","1","1","1","reached"],
    (10, 14): ["1","1","1","1","1","1","1","reached"],

    (11, 0): ["1","1","1","turn left","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn right", "1","1","1","1","reached"],
    (11, 1): ["1","1","1","turn left","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (11, 2): ["1","1","1","turn left","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn right", "1","1","1","1","1","1","1","reached"],
    (11, 3): ["1","1","1","turn left","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn left", "1","1","1","reached"],
    (11, 4): ["1","1","1","turn left","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (11, 5): ["1","1","1","turn left","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (11, 6): ["1","1","1","turn left","1","1","1","1","1","1","1","1","1","reached"],
    (11, 7): ["1","1","1","turn left","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (11, 8): ["1","1","1","turn left","1","1","1","1","1","1","reached"],
    (11, 9): ["1","1","1","turn left","1","1","1","reached"],
    (11, 10): ["1","1","1","reached"],
    (11, 12): ["1","1","1","turn right","1","1","reached"],
    (11, 13): ["1","1","1","1","1","1","1","reached"],
    (11, 14): ["1","1","1","1","1","1","1","1","1","1","reached"],

    (12, 0): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn right", "1","1","1","1","reached"],
    (12, 1): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (12, 2): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn right", "1","1","1","1","1","1","1","reached"],
    (12, 3): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn left", "1","1","1","reached"],
    (12, 4): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (12, 5): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (12, 6): ["1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (12, 7): ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (12, 8): ["1","1","1","1","1","1","1","1","1","reached"],
    (12, 9): ["1","1","1","1","1","1","reached"],
    (12, 10): ["1","1","1","reached"],
    (12, 11): ["1","1","1","turn left","1","1","reached"],
    (12, 13): ["1","1","1","turn right","1","1","1","1","reached"],
    (12, 14): ["1","1","1","turn right","1","1","1","1","1","1","1","reached"],

    (13, 0): ["1","1","1","turn right","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn right", "1","1","1","1","reached"],
    (13, 1): ["1","1","1","turn right","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (13, 2): ["1","1","1","turn right","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn right", "1","1","1","1","1","1","1","reached"],
    (13, 3): ["1","1","1","turn right","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn left", "1","1","1","reached"],
    (13, 4): ["1","1","1","turn right","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (13, 5): ["1","1","1","turn right","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (13, 6): ["1","1","1","turn right","1","1","1","1","1","1","1","1","1","reached"],
    (13, 7): ["1","1","1","turn right","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (13, 8): ["1","1","1","turn right","1","1","1","1","1","1","reached"],
    (13, 9): ["1","1","1","turn right","1","1","1","reached"],
    (13, 10): ["1","1","1","reached"],
    (13, 11): ["1","1","1","1","1","reached"],
    (13, 12): ["1","1","1","turn left","1","1","reached"],
    (13, 14): ["1","1","1","1","reached"],

    (14, 0): ["1","1","1","1","1","1","turn right","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn right", "1","1","1","1","reached"],
    (14, 1): ["1","1","1","1","1","1","turn right","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (14, 2): ["1","1","1","1","1","1","turn right","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn right", "1","1","1","1","1","1","1","reached"],
    (14, 3): ["1","1","1","1","1","1","turn right","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","turn left", "1","1","1","reached"],
    (14, 4): ["1","1","1","1","1","1","turn right","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (14, 5): ["1","1","1","1","1","1","turn right","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (14, 6): ["1","1","1","1","1","1","turn right","1","1","1","1","1","1","1","1","1","reached"],
    (14, 7): ["1","1","1","1","1","1","turn right","1","1","1","1","1","1","1","1","1","1","1","1","reached"],
    (14, 8): ["1","1","1","1","1","1","turn right","1","1","1","1","1","1","reached"],
    (14, 9): ["1","1","1","1","1","1","turn right","1","1","1","reached"],
    (14, 10): ["1","1","1","1","1","1","reached"],
    (14, 11): ["1","1","1","1","1","1","1","1","reached"],
    (14, 12): ["1","1","1","1","1","1","turn left","1","1","reached"],
    (14, 13): ["1","1","1","1","reached"],
    }

# navigation_steps = ["1","1","1","1","turn left", "1","1","1","reached"]
steps_walked = 0

k=0
start_index = 1  # e.g., index 0 => "In front of Ladies Washroom"
end_index = 1    # e.g., index 1 => "Girls Exit"

start_point = locations[start_index]
destination_point = locations[end_index]
# User input for journey info
# start_point = "In front of Ladies Washroom"
# destination_point = "Girls Exit"
if start_index == end_index:
    print("You are already at your destination.")
    start_index=-1
    navigation_steps = ["1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1","1"]
    total_steps_required = 1000
else:
    navigation_steps = navigation_paths.get((start_index, end_index), [])
    print("Navigation steps:", navigation_steps)
    total_steps_required = navigation_steps.count("1")*3
print("Total steps required:", total_steps_required)
if start_index != -1:
    speak(f"You are starting from {start_point}")


def upload_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            print(f"Raw image data size: {len(image_data)} bytes")  # Check size of image data
            
            if len(image_data) == 0:
                print("Error: The image file is empty.")
                return None
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            print("Image base64 encoded successfully.")
            print(f"Base64 String Length: {len(image_base64)}")  # Check the length of the base64 string
            
            return image_base64
    except Exception as e:
        print(f"Error while uploading the image: {e}")
        return None


# Initialize all three camera feeds (use actual IPs for Camera 2 and Camera 3)
cam1 = cv2.VideoCapture("http://192.168.136.121:4747/video")  # Camera 1 (Processing applied)

last_detection_time = 0

# Check if cameras opened properly
if not cam1.isOpened():
    print("Error: Unable to open Camera 1")
    exit()

frame_counter = 0
path_clear_count = 0
path_not_clear_count = 0
confidence_threshold = 0.2  # Confidence threshold for "path_not_clear"


while True:
    
    while is_speaking:
        print(is_speaking)
        print("Skipping frames because the system is speaking.")

        # 🟢 Clear camera buffer: Read & discard frames
        for _ in range(100):  # Adjust number to clear more frames
            cam1.grab()  # Grabs frames without decoding (faster)

        # time.sleep(5)  # Small delay while speaking

        is_speaking = False  # Mark speaking as done
        print("Updated is_speaking:", is_speaking) 

    print("IM OUTSIDE")
    
    # Read frames from all three cameras (only if they are initialized)
    ret1, frame1 = cam1.read()

    # If any camera fails, skip processing for that camera
    if not ret1:
        print("Error: Unable to read frame from Camera 1")
        break
        

    frame_counter += 1

    # Process only Camera 1
    if frame_counter % 5 == 0:
        
        results = model(frame1)
        frame_resized = frame1  # Resize to a smaller resolution

        height, width, _ = frame_resized.shape
        part_width = width // 3

        parts = [
            frame_resized[:, i * part_width:(i + 1) * part_width] 
            for i in range(3)
        ]
        border_color = (0, 0, 0)  # Black color
        border_width = 5  # Width of the border

        bordered_parts = []
        for part in parts:
            bordered_part = cv2.copyMakeBorder(
                part,
                0, 0, border_width // 2, border_width // 2,
                cv2.BORDER_CONSTANT,
                value=border_color
            )
            bordered_parts.append(bordered_part)

        # Concatenate the bordered parts horizontally for display
        concatenated_parts = cv2.hconcat(bordered_parts)

        # Display the concatenated parts in a single window
        cv2.imshow("Parts with Borders", concatenated_parts)

        for box in results[0].boxes:
            cls = int(box.cls[0])  # Class ID
            conf = float(box.conf[0])  # Confidence score
            label = results[0].names[cls]  # Class name

            print(f"[Camera 1] Prediction: {label}, Confidence: {conf:.2f}")

            if label == "Path Clear" and conf >= confidence_threshold:
                path_clear_count += 1
            elif label == "Path Not Clear" and conf >= confidence_threshold:
                path_not_clear_count += 1

            if path_not_clear_count > 20:
                speak("Path not clear.")
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                    temp_file_path1 = temp_file.name
                    cv2.imwrite(temp_file_path1, frame1)
                    current_url_1 = upload_image(temp_file_path1)
                    model_gemini = genai.GenerativeModel(model_name = "gemini-1.5-flash")
                    prompt = "I'm visually impaired. Describe this object/obstacle blocking the path. in 4 words."
                    response = model_gemini.generate_content([{'mime_type':'image/jpeg', 'data': current_url_1}, prompt])

                    print(response.text)
                        # "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
                    # stream = client.chat.completions.create(
                    #     model="meta-llama/Llama-Vision-Free",
                    #     max_tokens=15,
                    #     temperature=0.7,
                    #     top_p=0.7,
                    #     top_k=50,
                    #     repetition_penalty=1,
                    #     messages=[
                    #         {
                    #             "role": "user",
                    #             "content": [
                    #                 {"type": "text", "text": "Describe this object/obstacle blocking the path. in 4 words."},
                    #                 {
                    #                     "type": "image_url",
                    #                     "image_url": {
                    #                         "url": f"data:image/jpg;base64,{current_url_1}",
                    #                     },
                    #                 },
                    #             ],
                    #         }
                    #     ],
                    #     stream=False,
                    # )
                    # print(stream.choices[0].message.content)
                    speak("The obstacle blocking the path is "+response.text)
                    prompt = "I'm visually impaired. Is there any object/obstacle blocking the path. Just reply with Yes or No. "
                    cv2.imwrite(temp_file_path1, parts[0])
                    current_url_0 = upload_image(temp_file_path1)
                    response1 = model_gemini.generate_content([{'mime_type':'image/jpeg', 'data': current_url_0}, prompt])

                    print(response1.text)
                    cv2.imwrite(temp_file_path1, parts[2])
                    current_url_2 = upload_image(temp_file_path1)
                    response2 = model_gemini.generate_content([{'mime_type':'image/jpeg', 'data': current_url_2}, prompt])

                    print(response2.text)
                    #     stream = client.chat.completions.create(
                    #     model="meta-llama/Llama-Vision-Free",
                    #     max_tokens=15,
                    #     temperature=0.7,
                    #     top_p=0.7,
                    #     top_k=50,
                    #     repetition_penalty=1,
                    #     messages=[
                    #         {
                    #             "role": "user",
                    #             "content": [
                    #                 {"type": "text", "text": "Just reply with Yes or No. Is there any object/obstacle blocking the path or is there anything kept on the floor?"},
                    #                 {
                    #                     "type": "image_url",
                    #                     "image_url": {
                    #                         "url": f"data:image/jpg;base64,{current_url_1}",
                    #                     },
                    #                 },
                    #             ],
                    #         }
                    #     ],
                    #     stream=False,
                    # )
                    # if "No" in stream.choices[0].message.content:
                    #     speak("Step 2 steps to the left")
                    # elif "Yes" in stream.choices[0].message.content:
                    if("Yes" in response1.text and "Yes" in response2.text):
                        speak("Step 2 steps to the left")
                    elif("No" in response1.text and "No" in response2.text):
                        speak("Step 2 steps to the right")
                    elif("Yes" in response1.text and "No" in response2.text):
                        speak("Step 2 steps to the right")
                    elif("No" in response1.text and "Yes" in response2.text):
                        speak("Step 2 steps to the left")
                path_not_clear_count = 0
                path_clear_count = 0

            if path_clear_count > 15 and path_not_clear_count < 10 or path_clear_count > 20:
                speak("Path clear, walk 3 steps ahead.")
                k=k+1
                steps_walked += 3
                if(didreach==False):
                    if(navigation_steps[k]=="turn left" or navigation_steps[k]== "turn right"):
                        speak(navigation_steps[k])
                remaining_steps = total_steps_required - steps_walked
                if remaining_steps <= 5 and remaining_steps > 0 and didreach==False:
                    speak(f"You are just {remaining_steps} steps away from {destination_point}.")
                elif remaining_steps <= 0 and didreach==False:
                    speak(f"You have reached {destination_point}.")
                    time.sleep(1)
                    speak("Sameer Bharambe in Front of you.")
                    didreach=True
                path_clear_count = 0
                path_not_clear_count = 0
            

    # Show all camera feeds (only if available)
    cv2.imshow("Camera 1", frame1)

    # Exit condition
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
speech_queue.put(None)  # Signal the speech thread to stop
speech_thread.join()  # Wait for the speech thread to exit
# Release resources
cam1.release()
cv2.destroyAllWindows()
