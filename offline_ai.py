from datetime import datetime

def offline_response(cmd):
    if "time" in cmd:
        return datetime.now().strftime("Time is %H:%M")
    if "date" in cmd:
        return datetime.now().strftime("%d %B %Y")
    return "I'm offline right now"