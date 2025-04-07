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
from together import Together
import easyocr
import threading
import queue
import time
from dotenv import load_dotenv

load_dotenv()

# Load EasyOCR Model
is_speaking = False  # Global flag to track speech status
speech_lock = threading.Lock()  # Lock to synchronize access
easyocr_reader = easyocr.Reader(['en'])
# API_KEY = "44697c4f01f5de70baf289465f015ff1a79127d41964f59c423d9146c17a0e44"
os.environ['TOGETHER_API_KEY'] = os.getenv("TOGETHER_API_KEY")

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

client = Together()
text = "Just reply with 1 word. What obstacle is blocking the path?"
text1 = "Just reply with Yes or No. Is there any object/obstacle blocking the path or is there anything kept on the floor? "


# Initialize the model from the .pt file
model = YOLO("model.pt")

# Initialize text-to-speech engine
engine = pyttsx3.init()


def speak(text):
    speech_queue.put(text)  # Add text to the queue

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
CAMERA_2_URL=os.getenv('CAMERA_2_URL')
cam1 = cv2.VideoCapture(CAMERA_2_URL)  # Camera 1 (Processing applied)
cam2 = cv2.VideoCapture("http://localhost:5000/video_feed")  # Camera 2 (No processing yet)

last_detection_time = 0


# Function to process Camera 2
def process_camera2():
    global cam2,last_detection_time
    while True:
        if cam2 is None or not cam2.isOpened():
            print("[Camera 2] Reconnecting...")
            cam2 = cv2.VideoCapture("http://localhost:5000/video_feed")  
            time.sleep(2)  
            continue  # Try again after reconnecting
        
        ret2, frame2 = cam2.read()
        
        if not ret2 or frame2 is None:
            print("[Camera 2] Frame not received, skipping...")
            cam2.release()
            cam2 = None  
            time.sleep(2)  # Wait before reconnecting
            continue  
        
        try:
            gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
            enhanced = cv2.equalizeHist(gray)

            ocr_results = easyocr_reader.readtext(enhanced, detail=1)
            for (bbox, text, prob) in ocr_results:
                if text.lower() == 'x':  
                    current_time = time.time()

                    if current_time - last_detection_time >= 5:
                        print("[Camera 2] X detected!")
                        speak("Room 410 directly in Front.")
                        last_detection_time = current_time  
                    
                    break  

        except cv2.error as e:
            print(f"[Camera 2] OpenCV error: {e}")
            cam2.release()
            cam2 = None  
            time.sleep(2)  

        except Exception as e:
            print(f"[Camera 2] Error processing frame: {e}")


# Check if cameras opened properly
if not cam1.isOpened():
    print("Error: Unable to open Camera 1")
    exit()
if not cam2.isOpened():
    print("Warning: Unable to open Camera 2 (Dummy IP, skipping)")
    cam2 = None  # Assign None if Camera 2 is unavailable

frame_counter = 0
path_clear_count = 0
path_not_clear_count = 0
confidence_threshold = 0.2  # Confidence threshold for "path_not_clear"

if cam2 and cam2.isOpened():
    cam2_thread = threading.Thread(target=process_camera2, daemon=True)
    cam2_thread.start()
else:
    print("Warning: Camera 2 is not available.")

while True:
    
    while is_speaking:
        print(is_speaking)
        print("Skipping frames because the system is speaking.")

        # Clear camera buffer: Read & discard frames
        for _ in range(100):  # Adjust number to clear more frames
            cam1.grab()  # Grabs frames without decoding (faster)

        # time.sleep(5)  # Small delay while speaking

        is_speaking = False  # Mark speaking as done
        print("Updated is_speaking:", is_speaking) 

    
    # Read frames from all three cameras (only if they are initialized)
    ret1, frame1 = cam1.read()
    ret2, frame2 = None, None
    ret3, frame3 = None, None


    # If any camera fails, skip processing for that camera
    if not ret1:
        print("Error: Unable to read frame from Camera 1")
        break
        

    frame_counter += 1

    # Process only Camera 1
    if frame_counter % 5 == 0:
        
        results = model(frame1)
        frame_resized = cv2.resize(frame1, (100, 100))  # Resize to a smaller resolution

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
                    cv2.imwrite(temp_file_path1, parts[1])
                    current_url_1 = upload_image(temp_file_path1)
                        # "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
                    stream = client.chat.completions.create(
                        model="meta-llama/Llama-Vision-Free",
                        max_tokens=15,
                        temperature=0.7,
                        top_p=0.7,
                        top_k=50,
                        repetition_penalty=1,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Describe this object/obstacle blocking the path. in 4 words."},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpg;base64,{current_url_1}",
                                        },
                                    },
                                ],
                            }
                        ],
                        stream=False,
                    )
                    print(stream.choices[0].message.content)
                    speak("The obstacle blocking the path is "+stream.choices[0].message.content)
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                        temp_file_path1 = temp_file.name
                        cv2.imwrite(temp_file_path1, parts[0])
                        current_url_1 = upload_image(temp_file_path1)
                            
                        stream = client.chat.completions.create(
                        model="meta-llama/Llama-Vision-Free",
                        max_tokens=15,
                        temperature=0.7,
                        top_p=0.7,
                        top_k=50,
                        repetition_penalty=1,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Just reply with Yes or No. Is there any object/obstacle blocking the path or is there anything kept on the floor?"},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpg;base64,{current_url_1}",
                                        },
                                    },
                                ],
                            }
                        ],
                        stream=False,
                    )
                    if "No" in stream.choices[0].message.content:
                        speak("Step 2 steps to the left")
                    elif "Yes" in stream.choices[0].message.content:
                        speak("Step 2 steps to the right")
                path_not_clear_count = 0
                path_clear_count = 0
            if path_clear_count > 15 and path_not_clear_count < 10 or path_clear_count > 20:
                speak("Path clear, walk 3 steps ahead.")
                path_clear_count = 0
                path_not_clear_count = 0
            

    # Show all camera feeds (only if available)
    cv2.imshow("Camera 1", frame1)
    if cam2 and cam2.isOpened():
        ret2, frame2 = cam2.read()
        if ret2:
            cv2.imshow("Camera 2", frame2)

    # Exit condition
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
speech_queue.put(None)  # Signal the speech thread to stop
speech_thread.join()  # Wait for the speech thread to exit
# Release resources
cam1.release()
if cam2:
    cam2.release()
cv2.destroyAllWindows()
