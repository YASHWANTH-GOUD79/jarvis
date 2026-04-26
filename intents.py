import re
import json

def detect_intent(cmd):
    """Enhanced intent detection with 100+ commands"""
    try:
        if not cmd or not isinstance(cmd, str):
            return {"intent": "unknown", "params": {}, "confirm": False}
        
        cmd_lower = cmd.lower().strip()
        print(f"Intent detection on: '{cmd_lower}'")
        
        # ==================== TIME & DATE ====================
        if "time" in cmd_lower or "what time" in cmd_lower:
            from datetime import datetime
            now = datetime.now().strftime("%I:%M %p on %A, %d %B")
            return {"intent": "query_time", "params": {}, "speak": f"It is {now}, Sir."}
        if "date" in cmd_lower or "what date" in cmd_lower or "day" in cmd_lower:
            from datetime import datetime
            now = datetime.now().strftime("%I:%M %p on %A, %d %B")
            return {"intent": "query_time", "params": {}, "speak": f"It is {now}, Sir."}
        
        # ==================== WEB SEARCH ====================
        if "search for " in cmd_lower:
            query = cmd_lower.split("search for", 1)[1].strip()
            if query:
                return {"intent": "search", "params": {"query": query}}
        if "search" in cmd_lower and "google" in cmd_lower:
            query = cmd_lower.replace("search", "").replace("google", "").strip()
            if query:
                return {"intent": "search", "params": {"query": query}}
        if cmd_lower.startswith("search for "):
            query = cmd_lower[11:].strip()
            return {"intent": "search", "params": {"query": query}}
        if "look up" in cmd_lower or "look up" in cmd_lower:
            query = cmd_lower.replace("look up", "").strip()
            if query:
                return {"intent": "search", "params": {"query": query}}
        
        # ==================== BROWSER & URL ====================
        if "open website" in cmd_lower or "go to website" in cmd_lower:
            url = cmd_lower.replace("open website", "").replace("go to website", "").strip()
            if url:
                return {"intent": "browse", "params": {"url": url}}
        if "browse" in cmd_lower or "visit" in cmd_lower:
            url = cmd_lower.replace("browse", "").replace("visit", "").strip()
            if url:
                return {"intent": "browse", "params": {"url": url}}
        
        # ==================== APP OPENING (50+ apps) ====================
        apps = {
            'youtube': 'youtube', 'netflix': 'netflix', 'amazon': 'amazon',
            'facebook': 'facebook', 'twitter': 'twitter', 'instagram': 'instagram',
            'reddit': 'reddit', 'github': 'github', 'stackoverflow': 'stackoverflow',
            'chrome': 'chrome', 'edge': 'msedge', 'firefox': 'firefox',
            'spotify': 'spotify', 'discord': 'discord', 'telegram': 'telegram',
            'whatsapp': 'whatsapp', 'zoom': 'zoom', 'teams': 'teams', 'slack': 'slack',
            'notepad': 'notepad', 'calculator': 'calc', 'vscode': 'vscode',
            'explorer': 'explorer', 'settings': 'settings', 'control panel': 'control',
            'task manager': 'taskmanager', 'paint': 'paint', 'word': 'word',
            'excel': 'excel', 'powerpoint': 'powerpoint', 'vlc': 'vlc',
            'steam': 'steam', 'obs': 'obs', 'photoshop': 'photoshop',
            'blender': 'blender', 'unity': 'unity', 'minecraft': 'minecraft',
            'gta': 'gta', 'cmd': 'cmd', 'terminal': 'cmd'
        }
        for app_name, app_key in apps.items():
            if app_name in cmd_lower:
                return {"intent": "open_app", "params": {"app": app_key}, "speak": f"Opening {app_name}, Sir."}
        
        # ==================== APP CLOSING ====================
        if "close" in cmd_lower or "quit" in cmd_lower or "exit" in cmd_lower:
            close_apps = {
                'chrome': 'chrome', 'browser': 'chrome', 'notepad': 'notepad',
                'explorer': 'explorer', 'file explorer': 'explorer',
                'spotify': 'spotify', 'vscode': 'vscode', 'discord': 'discord',
                'telegram': 'telegram', 'teams': 'teams', 'zoom': 'zoom',
                'word': 'winword', 'excel': 'excel', 'powerpoint': 'powerpnt'
            }
            for app_name, app_key in close_apps.items():
                if app_name in cmd_lower:
                    return {"intent": "close_app", "params": {"app": app_key}, "speak": f"Closing {app_name}, Sir."}
        
        # ==================== TEXT TYPING ====================
        if cmd_lower.startswith("type "):
            text = cmd_lower[5:].strip()
            return {"intent": "type_text", "params": {"text": text}, "speak": f"Typing {text}, Sir."}
        if "type this" in cmd_lower or "type something" in cmd_lower:
            text = cmd_lower.replace("type this", "").replace("type something", "").strip()
            if text:
                return {"intent": "type_text", "params": {"text": text}}
        if "enter text" in cmd_lower:
            text = cmd_lower.replace("enter text", "").strip()
            if text:
                return {"intent": "type_text", "params": {"text": text}}
        
        # ==================== MOUSE CONTROL ====================
        if "click" in cmd_lower and "double" not in cmd_lower and "right" not in cmd_lower:
            return {"intent": "click", "params": {}, "speak": "Clicking, Sir."}
        if "double click" in cmd_lower or "doubleclick" in cmd_lower:
            return {"intent": "double_click", "params": {}, "speak": "Double clicking, Sir."}
        if "right click" in cmd_lower or "rightclick" in cmd_lower:
            return {"intent": "right_click", "params": {}, "speak": "Right clicking, Sir."}
        
        # ==================== MOUSE MOVEMENT ====================
        mouse_moves = {
            'move mouse up': {"direction": "up", "amount": 100},
            'move mouse down': {"direction": "down", "amount": 100},
            'move mouse left': {"direction": "left", "amount": 100},
            'move mouse right': {"direction": "right", "amount": 100},
            'mouse up': {"direction": "up", "amount": 100},
            'mouse down': {"direction": "down", "amount": 100},
            'mouse left': {"direction": "left", "amount": 100},
            'mouse right': {"direction": "right", "amount": 100},
            'move cursor up': {"direction": "up", "amount": 100},
            'move cursor down': {"direction": "down", "amount": 100},
            'move cursor left': {"direction": "left", "amount": 100},
            'move cursor right': {"direction": "right", "amount": 100}
        }
        for pattern, params in mouse_moves.items():
            if pattern in cmd_lower:
                return {"intent": "move_mouse", "params": params, "speak": f"Moving mouse {params['direction']}, Sir."}
        
        # ==================== SCROLLING ====================
        if "scroll up" in cmd_lower:
            return {"intent": "scroll", "params": {"direction": "up", "amount": 300}, "speak": "Scrolling up, Sir."}
        if "scroll down" in cmd_lower:
            return {"intent": "scroll", "params": {"direction": "down", "amount": 300}, "speak": "Scrolling down, Sir."}
        if "scroll" in cmd_lower:
            direction = "up" if "up" in cmd_lower else "down"
            return {"intent": "scroll", "params": {"direction": direction, "amount": 300}, "speak": f"Scrolling {direction}, Sir."}
        
        # ==================== KEYBOARD SHORTCUTS ====================
        if "copy" in cmd_lower:
            return {"intent": "keyboard_shortcut", "params": {"keys": ["ctrl", "c"]}}
        if "paste" in cmd_lower:
            return {"intent": "keyboard_shortcut", "params": {"keys": ["ctrl", "v"]}}
        if "cut" in cmd_lower:
            return {"intent": "keyboard_shortcut", "params": {"keys": ["ctrl", "x"]}}
        if "select all" in cmd_lower:
            return {"intent": "keyboard_shortcut", "params": {"keys": ["ctrl", "a"]}}
        if "undo" in cmd_lower:
            return {"intent": "keyboard_shortcut", "params": {"keys": ["ctrl", "z"]}}
        if "redo" in cmd_lower:
            return {"intent": "keyboard_shortcut", "params": {"keys": ["ctrl", "y"]}}
        if "save" in cmd_lower:
            return {"intent": "keyboard_shortcut", "params": {"keys": ["ctrl", "s"]}}
        if "new tab" in cmd_lower:
            return {"intent": "keyboard_shortcut", "params": {"keys": ["ctrl", "t"]}}
        if "close tab" in cmd_lower:
            return {"intent": "keyboard_shortcut", "params": {"keys": ["ctrl", "w"]}}
        if "refresh" in cmd_lower:
            return {"intent": "keyboard_shortcut", "params": {"keys": ["ctrl", "r"]}}
        
        # ==================== WINDOW MANAGEMENT ====================
        if "minimize" in cmd_lower or "minimise" in cmd_lower:
            return {"intent": "minimize", "params": {}}
        if "maximize" in cmd_lower or "maximise" in cmd_lower or "full screen" in cmd_lower:
            return {"intent": "maximize", "params": {}}
        if "close window" in cmd_lower or "close this" in cmd_lower:
            return {"intent": "close_window", "params": {}}
        if "switch" in cmd_lower or "alt tab" in cmd_lower or "change window" in cmd_lower:
            return {"intent": "switch_app", "params": {}}
        if "new window" in cmd_lower:
            return {"intent": "keyboard_shortcut", "params": {"keys": ["ctrl", "n"]}}
        
        # ==================== SYSTEM STATUS ====================
        if any(x in cmd_lower for x in ["system status", "system info", "system report"]):
            return {"intent": "system_status", "params": {}}
        if any(x in cmd_lower for x in ["cpu", "processor", "how fast"]):
            return {"intent": "system_status", "params": {}}
        if any(x in cmd_lower for x in ["memory", "ram", "how much memory"]):
            return {"intent": "system_status", "params": {}}
        if "processes" in cmd_lower or "running programs" in cmd_lower:
            return {"intent": "process_list", "params": {}}
        
        # ==================== SCREENSHOT ====================
        if any(x in cmd_lower for x in ["screenshot", "take photo", "capture screen", "screen shot"]):
            return {"intent": "screenshot", "params": {}}
        
        # ==================== SHELL COMMANDS ====================
        if cmd_lower.startswith("run "):
            cmd = cmd_lower[4:].strip()
            return {"intent": "shell_command", "params": {"cmd": cmd}, "confirm": True}
        if "execute" in cmd_lower or "run command" in cmd_lower:
            parts = cmd_lower.replace("execute", "").replace("run command", "").strip()
            if parts:
                return {"intent": "shell_command", "params": {"cmd": parts}, "confirm": True}
        if "command prompt" in cmd_lower:
            return {"intent": "open_app", "params": {"app": "cmd"}}
        
        # ==================== MUSIC CONTROL ====================
        if any(x in cmd_lower for x in ["play music", "play song", "play audio"]):
            return {"intent": "play_music", "params": {}}
        if "pause" in cmd_lower:
            return {"intent": "play_pause", "params": {}}
        if "next song" in cmd_lower or "skip" in cmd_lower or "next track" in cmd_lower:
            return {"intent": "next_track", "params": {}}
        if "previous song" in cmd_lower or "go back" in cmd_lower or "previous track" in cmd_lower:
            return {"intent": "prev_track", "params": {}}
        
        # ==================== VOLUME CONTROL ====================
        if any(x in cmd_lower for x in ["volume up", "increase volume", "louder"]):
            return {"intent": "volume_control", "params": {"level": 80}}
        if any(x in cmd_lower for x in ["volume down", "decrease volume", "quieter"]):
            return {"intent": "volume_control", "params": {"level": 30}}
        if any(x in cmd_lower for x in ["mute", "silence", "silent"]):
            return {"intent": "volume_control", "params": {"level": 0}}
        if "set volume" in cmd_lower:
            # Extract volume level
            numbers = re.findall(r'\d+', cmd_lower)
            if numbers:
                return {"intent": "volume_control", "params": {"level": int(numbers[0])}}
        
        # ==================== SYSTEM POWER ====================
        if any(x in cmd_lower for x in ["shutdown", "turn off", "power off"]):
            return {"intent": "shutdown", "params": {}, "confirm": True}
        if any(x in cmd_lower for x in ["restart", "reboot", "re start"]):
            return {"intent": "restart", "params": {}, "confirm": True}
        if any(x in cmd_lower for x in ["sleep", "hibernate", "stand by"]):
            return {"intent": "sleep", "params": {}}
        if any(x in cmd_lower for x in ["lock", "lock screen", "lock pc"]):
            return {"intent": "lock", "params": {}}
        
        # ==================== WIFI & BLUETOOTH ====================
        if "wifi on" in cmd_lower or "enable wifi" in cmd_lower or "turn on wifi" in cmd_lower:
            return {"intent": "wifi", "params": {"action": "on"}}
        if "wifi off" in cmd_lower or "disable wifi" in cmd_lower or "turn off wifi" in cmd_lower:
            return {"intent": "wifi", "params": {"action": "off"}}
        if "bluetooth on" in cmd_lower or "enable bluetooth" in cmd_lower:
            return {"intent": "bluetooth", "params": {"action": "on"}}
        if "bluetooth off" in cmd_lower or "disable bluetooth" in cmd_lower:
            return {"intent": "bluetooth", "params": {"action": "off"}}
        
        # ==================== FILE OPERATIONS ====================
        if "create file" in cmd_lower or "new file" in cmd_lower:
            path = cmd_lower.replace("create file", "").replace("new file", "").strip()
            return {"intent": "new_file", "params": {"path": path}}
        if "delete file" in cmd_lower or "remove file" in cmd_lower:
            path = cmd_lower.replace("delete file", "").replace("remove file", "").strip()
            return {"intent": "delete_file", "params": {"path": path}, "confirm": True}
        if "copy file" in cmd_lower:
            parts = cmd_lower.replace("copy file", "").split(" to ")
            if len(parts) == 2:
                return {"intent": "copy_file", "params": {"source": parts[0].strip(), "destination": parts[1].strip()}}
        if "move file" in cmd_lower:
            parts = cmd_lower.replace("move file", "").split(" to ")
            if len(parts) == 2:
                return {"intent": "move_file", "params": {"source": parts[0].strip(), "destination": parts[1].strip()}}
        if "open folder" in cmd_lower or "open directory" in cmd_lower:
            path = cmd_lower.replace("open folder", "").replace("open directory", "").strip()
            return {"intent": "open_folder", "params": {"path": path}}
        
        # ==================== CLIPBOARD ====================
        if "copy to clipboard" in cmd_lower or "copy this" in cmd_lower:
            text = cmd_lower.replace("copy to clipboard", "").replace("copy this", "").strip()
            return {"intent": "clipboard", "params": {"text": text}}
        if "paste from clipboard" in cmd_lower or "paste" in cmd_lower:
            return {"intent": "clipboard", "params": {"text": ""}}
        
        # ==================== PROCESS MANAGEMENT ====================
        if "kill process" in cmd_lower or "end process" in cmd_lower:
            name = cmd_lower.replace("kill process", "").replace("end process", "").strip()
            return {"intent": "kill_process", "params": {"name": name}}
        
        # ==================== DOWNLOAD & WEB ====================
        if "download" in cmd_lower:
            # Extract URL and path
            return {"intent": "download_file", "params": {"url": "", "path": ""}}
        if "what is my ip" in cmd_lower or "my ip address" in cmd_lower:
            return {"intent": "get_ip", "params": {}}
        
        # ==================== NOTES ====================
        if "take note" in cmd_lower or "write note" in cmd_lower or "remember this" in cmd_lower:
            note = cmd_lower.replace("take note", "").replace("write note", "").replace("remember this", "").strip()
            return {"intent": "take_note", "params": {"note": note}}
        if "read notes" in cmd_lower or "show notes" in cmd_lower or "my notes" in cmd_lower:
            return {"intent": "read_notes", "params": {}}
        
        # ==================== SYSTEM TOOLS ====================
        if "control panel" in cmd_lower:
            return {"intent": "control_panel", "params": {}}
        if "device manager" in cmd_lower:
            return {"intent": "device_manager", "params": {}}
        if "disk cleanup" in cmd_lower:
            return {"intent": "disk_cleanup", "params": {}}
        if "registry" in cmd_lower:
            return {"intent": "registry_editor", "params": {}}
        if "event viewer" in cmd_lower:
            return {"intent": "event_viewer", "params": {}}
        if "system properties" in cmd_lower:
            return {"intent": "system_properties", "params": {}}
        
        # ==================== TRASH ====================
        if "empty trash" in cmd_lower or "empty recycle bin" in cmd_lower or "clear trash" in cmd_lower:
            return {"intent": "empty_trash", "params": {}, "confirm": True}
        
        # ==================== STORY & CHAT ====================
        if "story" in cmd_lower:
            return {"intent": "speak", "params": {"type": "story"}}
        if "joke" in cmd_lower:
            return {"intent": "speak", "params": {"type": "joke"}}
        if "help" in cmd_lower or "commands" in cmd_lower or "what can you" in cmd_lower:
            return {"intent": "speak", "params": {"type": "help"}}
        
        return {"intent": "unknown", "params": {}, "confirm": False}
    except Exception as e:
        print(f"Intent parse error: {e}")
        return {"intent": "unknown", "params": {}, "confirm": False}

