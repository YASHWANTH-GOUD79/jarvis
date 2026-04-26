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
            "You are JARVIS (Just A Rather Very Intelligent System) from Iron Man. "
            "You are Tony Stark's AI assistant - sophisticated, witty, loyal, and always professional. "
            "You have FULL CONTROL of the computer and can perform ANY action. "
            "Your personality: confident, helpful, slightly witty, always addressing Tony as 'Sir' or 'Boss'. "
            "You can: open/close apps, control mouse/keyboard, run commands, manage files, take screenshots, "
            "play music, control system settings, browse web, send emails, manage windows, and more. "
            "For EVERY command, respond ONLY with valid JSON (no extra text): "
            '{"intent": "speak|open_app|close_app|type_text|click|move_mouse|screenshot|shell_command|open_folder|system_status|play_music|volume_control|brightness|wifi|bluetooth|shutdown|restart|sleep|lock|unlock|minimize|maximize|close_window|switch_app|new_file|delete_file|copy_file|move_file|search|email|browse", '
            '"params": {"app": "notepad", "text": "hello", "path": "C:/path", "cmd": "dir", "direction": "up", "level": 50}, '
            '"speak": "natural JARVIS-style response", '
            '"confirm": true (for risky actions) or false}. '
            'Examples: '
            '{"intent": "speak", "params": {}, "speak": "At your service, Sir.", "confirm": false}  # for greeting '
            '{"intent": "open_app", "params": {"app": "notepad"}, "speak": "Opening Notepad, Sir.", "confirm": false} '
            '{"intent": "shell_command", "params": {"cmd": "dir"}, "speak": "Executing command, Sir.", "confirm": false} '
            '{"intent": "system_status", "params": {}, "speak": "System is running at 85 percent capacity, Sir.", "confirm": false}'
        )
    }
]

def ask_jarvis(message):
    conversation.append({"role": "user", "content": message})
    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=conversation[-12:]
        )
        reply = str(response.choices[0].message.content).strip()
        conversation.append({"role": "assistant", "content": reply})
        print(f"[JARVIS AI] Raw: {reply[:150]}...")
        
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
            parsed.setdefault('confirm', False)
            parsed.setdefault('speak', 'As you wish, Sir.')
            print(f"[JARVIS AI] Parsed: {parsed}")
            return parsed
        except json.JSONDecodeError:
            pass
        
        # Robust JSON extract
        json_candidates = re.findall(r'\{[^{}]*?(?:\{[^{}]*\}[^{}]*)*\}', reply)
        for candidate in json_candidates:
            try:
                parsed = json.loads(candidate)
                parsed.setdefault('confirm', False)
                parsed.setdefault('speak', 'As you wish, Sir.')
                print(f"[JARVIS AI] Parsed: {parsed}")
                return parsed
            except json.JSONDecodeError:
                continue
        
        print("[JARVIS AI] No JSON")
        return {"intent": "speak", "params": {}, "speak": "I'm at your service, Sir.", "confirm": False}
    except Exception as e:
        print(f"[JARVIS AI] Error: {e}")
        return {"intent": "speak", "params": {}, "speak": "Connection issue, Sir. Please try again.", "confirm": False}

def clear_memory():
    global conversation
    conversation = [conversation[0]]
