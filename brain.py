# brain.py - JARVIS Proactive AI Brain

from memory import get_usage, load, save, get_user_name
from voice_engine import speak_jarvis, get_jarvis_response
import time
import random
from datetime import datetime

last_action_time = time.time()
last_proactive_time = 0

def auto_mode(execute_function):
    """Proactive AI mode - anticipates user needs"""
    global last_action_time, last_proactive_time
    
    current_time = time.time()
    
    # Run proactive checks every 60 seconds
    if current_time - last_action_time < 60:
        return
    
    # Check for proactive suggestions every 5 minutes
    if current_time - last_proactive_time < 300:
        last_action_time = current_time
        return
    
    usage = get_usage()
    
    if not usage:
        last_action_time = current_time
        return
    
    # Time-based proactive suggestions
    hour = datetime.now().hour
    
    # Morning routine
    if 6 <= hour <= 8:
        speak_jarvis("Good morning, Sir. It is " + datetime.now().strftime("%I %M") + ". Would you like me to open your usual applications?")
        last_proactive_time = current_time
        last_action_time = current_time
        return
    
    # Evening shutdown suggestion
    if 21 <= hour <= 22:
        speak_jarvis("It is " + datetime.now().strftime("%I %M") + ", Sir. Would you like me to shut down the system?")
        last_proactive_time = current_time
        last_action_time = current_time
        return
    
    # Activity-based suggestions
    top = max(usage, key=usage.get)
    
    messages = {
        "coding": ["Ready to build something, Sir?", "Shall I open your project?"],
        "music": ["Would you like some music, Sir?", "Feeling like some tunes?"],
        "youtube": ["Want to watch something, Sir?", "Feeling bored?"],
        "chrome": ["Need to browse, Sir?", "Opening browser?"]
    }
    
    if top in messages:
        msg = random.choice(messages[top])
        speak_jarvis(msg)
        last_proactive_time = current_time
    
    last_action_time = current_time

def analyze_intent(user_input):
    """Deep intent analysis - asks smart clarification if unclear"""
    input_lower = user_input.lower()
    
    # Boredom detection
    if "bored" in input_lower or "nothing to do" in input_lower:
        return {
            "clarification": "Would you like a movie recommendation, or shall I play music, Sir?",
            "options": ["movie", "music", "youtube"]
        }
    
    # Unclear intent
    if len(user_input) < 3:
        return {
            "clarification": "I did not catch that, Sir. Could you repeat?",
            "options": []
        }
    
    return None

def get_system_status():
    """Get current system awareness"""
    import psutil
    
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    
    status = {
        "cpu": cpu,
        "memory": mem,
        "disk": disk,
        "time": datetime.now().strftime("%I:%M %p")
    }
    
    return status

def report_system_status():
    """Report system status in JARVIS style"""
    status = get_system_status()
    
    report = f"System status: CPU at {status['cpu']:.0f} percent, "
    report += f"memory at {status['memory']:.0f} percent. "
    report += f"It is {status['time']}, Sir."
    
    speak_jarvis(report)
    return status