import cv2
from voice_engine import speak

def see():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        cv2.imwrite("vision.jpg", frame)
        speak("Captured image")
    cam.release()