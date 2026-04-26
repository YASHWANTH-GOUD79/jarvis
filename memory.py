import json
from datetime import datetime

FILE = "memory.json"

def load():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

# === User Preferences ===

def get_user_name():
    """Get stored user name"""
    data = load()
    return data.get("user_name", "Sir")

def set_user_name(name):
    """Set user name for personalization"""
    data = load()
    data["user_name"] = name
    save(data)

def get_preference(key, default=None):
    """Get user preference"""
    data = load()
    return data.get("preferences", {}).get(key, default)

def set_preference(key, value):
    """Set user preference"""
    data = load()
    if "preferences" not in data:
        data["preferences"] = {}
    data["preferences"][key] = value
    save(data)

# === Usage Tracking ===

def track(action):
    """Track user action for proactive suggestions"""
    data = load()
    usage = data.get("usage", {})
    usage[action] = usage.get(action, 0) + 1
    data["usage"] = usage
    
    # Track timestamp
    data["last_action"] = datetime.now().isoformat()
    save(data)

def get_usage():
    """Get usage statistics"""
    return load().get("usage", {})

def get_frequent_commands():
    """Get most used commands"""
    usage = get_usage()
    if not usage:
        return []
    sorted_usage = sorted(usage.items(), key=lambda x: x[1], reverse=True)
    return [cmd for cmd, count in sorted_usage[:5]]

# === Chat History ===

def remember_chat(user_input, bot_response):
    """Remember conversation for context"""
    data = load()
    chats = data.get("chat", [])
    chats.append({
        "u": user_input,
        "b": bot_response,
        "ts": datetime.now().isoformat()
    })
    data["chat"] = chats[-50:]  # Keep last 50
    save(data)

def get_recent_chats(count=5):
    """Get recent chat history"""
    data = load()
    return data.get("chat", [])[-count:]

# === Goals ===

def save_goal(goal):
    """Save user goal"""
    data = load()
    goals = data.get("goals", [])
    goals.append({
        "goal": goal,
        "created": datetime.now().isoformat(),
        "completed": False
    })
    data["goals"] = goals
    save(data)

def get_goals():
    """Get all goals"""
    return load().get("goals", [])

def complete_goal(goal_text):
    """Mark goal as completed"""
    data = load()
    goals = data.get("goals", [])
    for g in goals:
        if g.get("goal") == goal_text:
            g["completed"] = True
            g["completed_at"] = datetime.now().isoformat()
    save(data)

# === Context ===

def get_last_context():
    """Get last conversation context"""
    chats = get_recent_chats(1)
    if chats:
        return chats[-1]
    return None