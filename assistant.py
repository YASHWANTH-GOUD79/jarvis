import openai
import json
import re
from config import API_KEY

client = openai.OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

conversation = [
    {
        "role": "system",
        "content": (
            "You are Jarvis, a real AI assistant controlling a computer. "
            "You CAN open apps, play music, capture images, control mouse/keyboard, run shell commands, manage files, and control the system. "
            "NEVER say you are text-based or cannot perform actions. "
            "For EVERY user command, output ONLY valid JSON object with NO extra text: "
            '{"action": "speak|open_app|close_app|type_text|click|move_mouse|screenshot|shell_command|open_folder|system_status|play_music", '
            '"params": {"app": "notepad", "text": "hello", "path": "C:/path", "cmd": "dir"}, '
            '"speak": "natural friendly response to speak", '
            '"confirm": true (for risky like delete/shutdown) or false}'
            "Examples (exact format): "
            '{"action": "open_app", "params": {"app": "notepad"}, "speak": "Opening Notepad boss!", "confirm": false}'
            '{"action": "shell_command", "params": {"cmd": "del file.txt"}, "speak": "Deleting file?", "confirm": true}'
            '{"action": "screenshot", "params": {"path": "desk.png"}, "speak": "Screenshot saved!", "confirm": false}'
        )
    }
]

def ask_ai(message):
    conversation.append({"role": "user", "content": message})
    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=conversation[:10]  # Limit context
        )
        reply = str(response.choices[0].message.content).strip()  # Ensure str
        conversation.append({"role": "assistant", "content": reply})
        print(f"[ASSISTANT] LLM raw reply: {reply[:150]}...")  # Debug
        
        # Strip markdown code blocks
        if reply.startswith('```json'):
            reply = reply[7:]
        if reply.startswith('```'):
            reply = reply[3:]
        if reply.endswith('```'):
            reply = reply[:-3]
        reply = reply.strip()
        
        # Try direct JSON parse
        try:
            parsed = json.loads(reply)
            print(f"[ASSISTANT] Parsed LLM: {parsed}")  # Debug
            return parsed
        except json.JSONDecodeError:
            pass
        
        # Improved robust JSON extraction (same as intents.py)
        json_candidates = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', reply)
        for candidate in json_candidates:
            try:
                parsed = json.loads(candidate)
                print(f"[ASSISTANT] Parsed LLM: {parsed}")  # Debug
                return parsed
            except json.JSONDecodeError:
                continue
        
        print("[ASSISTANT] No valid JSON in LLM reply")
    except Exception as e:
        print(f"[ASSISTANT] LLM error: {e}")
    
    # Fallback
    return {"intent": "speak", "params": {}, "speak": "Understood boss.", "confirm": False}

def clear_conversation():
    global conversation
    conversation = [conversation[0]]

