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
navigation_steps = ["1","1","1","1","turn left", "1","1","1","reached"]
steps_walked = 0
total_steps_required = 21
k=0

# User input for journey info
start_point = "In front of Ladies Washroom"
destination_point = "Girls Exit"

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
cam1 = cv2.VideoCapture("http://192.168.77.126:4747/video")  # Camera 1 (Processing applied)

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
