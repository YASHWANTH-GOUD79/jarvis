import pvporcupine
import pyaudio
import struct
import sys
import threading
from voice_engine import speak_jarvis

# Wake word states
WAKE_STATE_PASSIVE = "passive"
WAKE_STATE_ACTIVE = "active"
WAKE_STATE_SLEEP = "sleep"

current_wake_state = WAKE_STATE_PASSIVE
wake_thread = None
wake_running = False

def listen_wake_word():
    """Listen for wake word 'Jarvis' or 'Hey Jarvis' - blocking until detected"""
    global wake_running
    wake_running = True
    
    try:
        print("[WAKE] Initializing wake word detection...")
        porcupine = pvporcupine.create(keywords=["jarvis"])
        pa = pyaudio.PyAudio()

        stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print("[WAKE] Listening for 'Hey Jarvis'... (Passive Mode)")

        while wake_running:
            try:
                pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

                if porcupine.process(pcm) >= 0:
                    print("[WAKE] Wake word detected!")
                    speak_jarvis("Yes, Sir.")
                    break
            except Exception as e:
                print(f"[WAKE] Error: {e}")
                continue

        stream.close()
        pa.terminate()
        
    except Exception as e:
        print(f"[WAKE] Error: {e}")
        # Fallback: return True to allow manual activation
        pass
    
    return True

def start_wake_listener():
    """Start background wake word listener"""
    global wake_thread
    if wake_thread is None or not wake_thread.is_alive():
        wake_thread = threading.Thread(target=listen_wake_word, daemon=True)
        wake_thread.start()
    return wake_thread

def stop_wake_listener():
    """Stop wake word listener"""
    global wake_running
    wake_running = False

def get_wake_state():
    """Get current wake state"""
    return current_wake_state

def set_wake_state(state):
    """Set wake state: passive, active, or sleep"""
    global current_wake_state
    current_wake_state = state
    print(f"[WAKE] State: {state}")