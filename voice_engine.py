import platform
import pyttsx3
import speech_recognition as sr
import threading
import queue

driver = 'sapi5' if platform.system() == 'Windows' else None
engine = pyttsx3.init(driver) if driver else pyttsx3.init()
engine.setProperty('rate', 175)
voices = engine.getProperty('voices')
selected_voice = None
for voice in voices:
    if 'zira' in voice.name.lower() or 'female' in voice.name.lower():
        selected_voice = voice.id
        break
if not selected_voice and voices:
    selected_voice = voices[0].id
if selected_voice:
    engine.setProperty('voice', selected_voice)
engine.setProperty('volume', 1.0)

def speak(text):
    try:
        # Run in thread to avoid blocking
        def _speak():
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"Speak error: {e}")
        
        thread = threading.Thread(target=_speak, daemon=True)
        thread.start()
    except Exception as e:
        print(f"Speak error: {e}")

def listen():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening for command...")
            r.adjust_for_ambient_noise(source, duration=1)
            r.energy_threshold = 400
            r.dynamic_energy_threshold = True
            
            try:
                audio = r.listen(source, timeout=10, phrase_time_limit=15)
            except sr.WaitTimeoutError:
                print("No speech detected, returning to auto mode...")
                return ""
            
        # Recognize using Google
        text = r.recognize_google(audio, language="en-IN")
        cmd = str(text).lower().strip()
        print(f"Raw STT cmd: '{cmd}' (len: {len(cmd)})")
        return cmd if cmd else ""
        
    except sr.UnknownValueError:
        print("STT: Could not understand audio")
        return ""
    except sr.RequestError as e:
        print(f"STT error: {e}")
        return ""
    except Exception as e:
        print(f"Listen error: {e}")
        return ""

