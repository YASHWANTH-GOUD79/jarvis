from ai import ask_jarvis
from voice_engine import listen, speak
from automation import execute, execute_from_intent, confirm_action, get_system_status
from memory import remember_chat
from gui import JarvisGUI
from brain import auto_mode
from system_monitor import monitor, get_status, format_short_status
import threading, time
from face_auth import authenticate
from speaker_auth import verify_user
from intents import detect_intent
from wake_word import listen_wake_word
from config import APP_NAME, APP_VERSION
import datetime

print(f"Starting {APP_NAME} v{APP_VERSION} - Iron Man System")
print("=" * 50)

def get_greeting():
    """Get time-based greeting"""
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

def run(gui):
    # First: Listen for wake word "Jarvis"
    speak("Initializing JARVIS systems...")
    listen_wake_word()
    
    # Wake word detected! Now do face auth
    if not authenticate():
        speak("Access denied. Face not recognized.")
        threading.Thread(target=lambda: run(gui), daemon=True).start()
        return

    greeting = get_greeting()
    speak(f"{greeting}, Sir! All systems are operational. I am online and ready.")

    # Show system status briefly
    status = get_status()
    speak(f"CPU at {status['cpu']} percent, Memory at {status['memory']} percent.")

    while True:
        cmd = listen()

        print(f"[MAIN] Received cmd: '{cmd}'")

        if not cmd:
            auto_mode(execute)
            time.sleep(0.5)
            continue

        gui.show_output("You: " + cmd)

        if not verify_user():
            speak("Voice not recognized. Please try again.")
            continue

        cmd_lower = cmd.lower()
        if "exit" in cmd_lower or "bye" in cmd_lower or "goodbye" in cmd_lower:
            speak("Goodbye, Sir! Shutting down JARVIS systems.")
            threading.Thread(target=lambda: run(gui), daemon=True).start()
            break

        # Unified intent processing
        response = detect_intent(cmd)
        print(f"[MAIN] Keyword intent: {response}")
        
        # If keywords don't handle or unknown, use LLM
        if response.get('intent', response.get('action', 'unknown')) == 'unknown':
            response = ask_jarvis(cmd)
            print(f"[MAIN] LLM response: {response}")
        
        intent_name = response.get('intent', response.get('action', 'unknown'))
        
        # Confirm risky actions
        if intent_name not in ['speak', 'query_time', 'unknown']:
            if response.get('confirm', False) or 'shell' in intent_name:
                if not confirm_action():
                    speak("Action cancelled, Sir.")
                    continue
        
        # Execute
        if execute_from_intent(response):
            speak(response.get('speak', 'Done, Sir!'))
            continue
        
        # Fallback speak
        speak(response.get('speak', 'Understood, Sir.') or response or "At your service, Sir.")

def run_text(gui):
    greeting = get_greeting()
    speak(f"{greeting}, Sir! Welcome to JARVIS text mode.")

    while True:
        cmd = input("You: ").strip()

        print(f"[MAIN] Received cmd: '{cmd}'")

        if not cmd:
            continue

        gui.show_output("You: " + cmd)

        if cmd.lower() in ["exit", "bye", "goodbye"]:
            speak("Goodbye, Sir! JARVIS signing off.")
            break

        # Unified intent processing
        response = detect_intent(cmd)
        print(f"[MAIN] Keyword intent: {response}")
        
        # If keywords don't handle or unknown, use LLM
        if response.get('intent', response.get('action', 'unknown')) == 'unknown':
            response = ask_jarvis(cmd)
            print(f"[MAIN] LLM response: {response}")
        
        intent_name = response.get('intent', 'unknown')
        
        # Confirm risky
        if intent_name not in ['speak', 'query_time', 'unknown']:
            if response.get('confirm', False):
                confirm = input("Confirm? (y/n): ").lower() == 'y'
                if not confirm:
                    speak("Action cancelled, Sir.")
                    continue
                response['confirm'] = False
        
        # Execute
        if execute_from_intent(response):
            speak(response.get('speak', 'Done, Sir!'))
            continue
        
        # Fallback speak
        speak(response.get('speak', 'Understood, Sir.') or response or "At your service, Sir.")

def main():
    print(f"Initializing {APP_NAME}...")
    gui = JarvisGUI()
    
    # Start GUI in main thread
    threading.Thread(target=run, args=(gui,), daemon=True).start()
    gui.run()

if __name__ == "__main__":
    main()
