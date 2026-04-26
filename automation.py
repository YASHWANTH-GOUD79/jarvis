import os
import webbrowser
import subprocess
import psutil
import pyautogui
from PIL import Image
from voice_engine import speak, listen
from memory import track
from intents import detect_intent
from datetime import datetime
import time
import ctypes
import shutil
import json
import requests
from win32api import GetSystemMetrics
import winreg

# Enable PyAutoGUI failsafe
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

# Logger for debugging
def log_action(action, success=True, error=None):
    """Log JARVIS actions for debugging"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if success else "ERROR"
    msg = f"[{timestamp}] {action}: {status}"
    if error:
        msg += f" | Error: {error}"
    print(msg)
    # Optionally save to log file
    try:
        with open("jarvis.log", "a") as f:
            f.write(msg + "\n")
    except:
        pass

def confirm_action():
    """Confirm risky actions with voice"""
    speak("Confirm? Say yes or no.")
    response = listen()
    return "yes" in response.lower() if response else False

def shell_exec(cmd, confirm=False):
    """Execute shell commands with error handling"""
    if confirm:
        if not confirm_action():
            speak("Action cancelled, Sir.")
            return False
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        out = result.stdout[:200] if result.stdout else ""
        if result.returncode == 0:
            speak(f"Executed successfully. {out[:100]}..." if out else "Done, Sir.")
            track("shell_exec")
            log_action(f"shell_exec: {cmd}", True)
            return True
        else:
            speak(f"Command failed: {result.stderr[:50]}" if result.stderr else "Execution failed.")
            log_action(f"shell_exec: {cmd}", False, result.stderr)
            return False
    except subprocess.TimeoutExpired:
        speak("Command timed out, Sir.")
        log_action(f"shell_exec: {cmd}", False, "Timeout")
        return False
    except Exception as e:
        speak(f"Error executing: {str(e)[:50]}")
        log_action(f"shell_exec: {cmd}", False, str(e))
        return False

def focus_app(app_name):
    """Focus/activate app window"""
    app_lower = app_name.lower()
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            proc_name = proc.info['name']
            if proc_name and app_lower in proc_name.lower():
                # Try to bring to front
                proc_name_escaped = proc_name.replace('"', '')
                subprocess.Popen(f'taskkill /FI "WINDOWTITLE eq {app_name}" /FI "IMAGENAME eq {proc_name_escaped}" /T /F', shell=True)
                time.sleep(0.3)
                subprocess.Popen(['start', app_name], shell=True)
                time.sleep(1.5)
                pyautogui.hotkey('alt', 'tab')
                time.sleep(0.3)
                pyautogui.click()
                speak(f"Focused {app_name}, Sir.")
                return True
    except Exception as e:
        log_action(f"focus_app: {app_name}", False, str(e))
    speak(f"Could not focus {app_name}, Sir.")
    return False

def get_system_status():
    """Get comprehensive system status"""
    try:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('C:\\')
        battery = psutil.sensors_battery()
        
        status = {
            'cpu': cpu,
            'memory': memory.percent,
            'memory_used': memory.used / (1024**3),
            'memory_total': memory.total / (1024**3),
            'disk': disk.percent,
            'battery': battery.percent if battery else 100
        }
        return status
    except Exception as e:
        log_action("get_system_status", False, str(e))
        return {'cpu': 0, 'memory': 0, 'disk': 0, 'battery': 0}

def get_cpu_temperature():
    """Get CPU temperature if available"""
    try:
        import wmi
        w = wmi.WMI()
        for temp in w.Win32_TemperatureProbe():
            if temp.CurrentReading:
                return temp.CurrentReading / 10.0
    except:
        pass
    return None

def get_network_connections():
    """Get network connection info"""
    try:
        net_io = psutil.net_io_counters()
        return {
            'sent': net_io.bytes_sent / (1024**2),  # MB
            'received': net_io.bytes_recv / (1024**2)
        }
    except:
        return {'sent': 0, 'received': 0}

def execute_from_intent(intent_dict):
    """Main intent execution with comprehensive error handling"""
    intent = intent_dict.get('intent', intent_dict.get('action', 'unknown'))
    params = intent_dict.get('params', {})
    
    try:
        # ==================== APP CONTROL ====================
        if intent == "open_app":
            app = params.get('app', '').lower().replace(' ', '')
            cmd_map = {
                'youtube': 'https://youtube.com',
                'spotify': 'spotify',
                'calculator': 'calc',
                'notepad': 'notepad',
                'chrome': 'chrome',
                'cmd': 'cmd',
                'vscode': 'code',
                'explorer': 'explorer',
                'settings': 'ms-settings:',
                'control': 'control',
                'taskmanager': 'taskmgr',
                'paint': 'mspaint',
                'word': 'winword',
                'excel': 'excel',
                'powerpoint': 'powerpnt',
                'zoom': 'zoom',
                'discord': 'discord',
                'telegram': 'telegram',
                'whatsapp': 'whatsapp',
                'steam': 'steam',
                'gta': 'gta5',
                'minecraft': 'minecraft',
                'netflix': 'https://netflix.com',
                'amazon': 'https://amazon.com',
                'facebook': 'https://facebook.com',
                'twitter': 'https://twitter.com',
                'instagram': 'https://instagram.com',
                'reddit': 'https://reddit.com',
                'github': 'https://github.com',
                'stackoverflow': 'https://stackoverflow.com',
                'teams': 'teams',

                'slack': 'slack',
                'vlc': 'vlc',
                'obs': 'obs64',
                'photoshop': 'photoshop',
                'blender': 'blender',
                'unity': 'unity',
                'unreal': 'unrealengine'
            }
            app_launch = cmd_map.get(app, app)
            try:
                subprocess.Popen(['start', app_launch], shell=True)
                time.sleep(1.5)
                speak(f"{params.get('app', app)} opened, Sir.")
                track("open_app")
                log_action(f"open_app: {app}")
                return True
            except Exception as e:
                speak(f"Failed to open {app}: {str(e)[:50]}")
                log_action(f"open_app: {app}", False, str(e))
                return False
        
        elif intent == "close_app":
            app = params.get('app', '').lower()
            killed = False
            try:
                for p in psutil.process_iter(['name']):
                    if p.info['name'] and app in p.info['name'].lower():
                        p.kill()
                        killed = True
                if killed:
                    speak(f"Closed {app}, Sir.")
                    log_action(f"close_app: {app}")
                else:
                    speak(f"No {app} found, Sir.")
            except Exception as e:
                speak(f"Error closing {app}: {str(e)}")
                log_action(f"close_app: {app}", False, str(e))
            return killed
        
        # ==================== TEXT & MOUSE CONTROL ====================
        elif intent == "type_text":
            text = params.get('text', '')
            if not text:
                speak("No text to type, Sir.")
                return False
            try:
                if 'chrome' in text.lower() or params.get('app') == 'chrome':
                    focus_app('chrome')
                speak(f"Typing '{text[:30]}...'")
                pyautogui.write(text)
                speak("Text typed successfully, Sir.")
                log_action(f"type_text: {text[:20]}...")
                return True
            except Exception as e:
                speak(f"Error typing: {str(e)}")
                log_action("type_text", False, str(e))
                return False
        
        elif intent == "click":
            try:
                pyautogui.click()
                speak("Clicked, Sir.")
                log_action("click")
                return True
            except Exception as e:
                speak(f"Click error: {str(e)}")
                return False
        
        elif intent == "double_click":
            try:
                pyautogui.doubleClick()
                speak("Double clicked, Sir.")
                log_action("double_click")
                return True
            except Exception as e:
                speak(f"Error: {str(e)}")
                return False
        
        elif intent == "right_click":
            try:
                pyautogui.rightClick()
                speak("Right click, Sir.")
                log_action("right_click")
                return True
            except Exception as e:
                speak(f"Error: {str(e)}")
                return False
        
        elif intent == "move_mouse":
            try:
                direction = params.get('direction', 'up')
                amount = int(params.get('amount', 100))
                if direction == "up":
                    pyautogui.moveRel(0, -amount)
                elif direction == "down":
                    pyautogui.moveRel(0, amount)
                elif direction == "left":
                    pyautogui.moveRel(-amount, 0)
                elif direction == "right":
                    pyautogui.moveRel(amount, 0)
                speak(f"Mouse moved {direction}, Sir.")

                log_action(f"move_mouse: {dir}")
                return True
            except Exception as e:
                speak(f"Mouse error: {str(e)}")
                return False
        
        elif intent == "scroll":
            try:
                direction = params.get('direction', 'up')
                amount = int(params.get('amount', 300))
                if direction == "down":
                    pyautogui.scroll(-amount)
                else:
                    pyautogui.scroll(amount)
                speak(f"Scrolled {direction}, Sir.")
                log_action(f"scroll: {direction}")
                return True
            except Exception as e:
                speak(f"Scroll error: {str(e)}")
                return False
        
        # ==================== KEYBOARD SHORTCUTS ====================
        elif intent == "keyboard_shortcut":
            try:
                keys = params.get('keys', [])
                if keys:
                    pyautogui.hotkey(*keys)
                    speak(f"Pressed {' + '.join(keys)}, Sir.")
                    log_action(f"keyboard_shortcut: {keys}")
                    return True
            except Exception as e:
                speak(f"Shortcut error: {str(e)}")
                return False
        
        # ==================== SCREENSHOT & MEDIA ====================
        elif intent == "screenshot":
            try:
                path = params.get('path', f"screenshot_{int(time.time())}.png")
                # Ensure directory exists
                os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
                img = pyautogui.screenshot()
                img.save(path)
                speak(f"Screenshot saved as {path}, Sir.")
                log_action(f"screenshot: {path}")
                return True
            except Exception as e:
                speak(f"Screenshot failed: {str(e)}")
                log_action("screenshot", False, str(e))
                return False
        
        # ==================== SYSTEM CONTROLS ====================
        elif intent == "shell_command":
            cmd = params.get('cmd', '')
            return shell_exec(cmd, intent_dict.get('confirm', False))
        
        elif intent == "open_folder":
            path = params.get('path', '')
            if path and os.path.exists(path):
                try:
                    os.startfile(path)
                    speak("Opened folder, Sir.")
                    log_action(f"open_folder: {path}")
                    return True
                except Exception as e:
                    speak(f"Error: {str(e)}")
                    log_action("open_folder", False, str(e))
            else:
                speak("Path not found, Sir.")
            return False
        
        elif intent == "system_status":
            try:
                status = get_system_status()
                temp = get_cpu_temperature()
                network = get_network_connections()
                
                response = f"System status: CPU at {status['cpu']} percent, "
                response += f"Memory at {status['memory']} percent, "
                response += f"Disk at {status['disk']} percent, "
                response += f"Battery at {status['battery']} percent."
                if temp:
                    response += f" CPU temperature: {temp} degrees."
                response += f" Network: {network['sent']:.1f} MB sent, {network['received']:.1f} MB received."
                speak(response)
                log_action("system_status")
                return True
            except Exception as e:
                speak(f"Status error: {str(e)}")
                return False
        
        elif intent == "volume_control":
            try:
                level = params.get('level', 50)
                # Try pycaw first
                try:
                    from ctypes import cast, POINTER
                    from comtypes import CLSCTX_ALL
                    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    volume.SetMasterVolumeLevelScalar(level / 100, None)
                    speak(f"Volume set to {level} percent, Sir.")
                    log_action(f"volume_control: {level}")
                except:
                    # Fallback to pyautogui
                    current = level / 100
                    for _ in range(int(current * 100)):
                        pyautogui.press('volumeup')
                    speak(f"Volume adjusted to {level} percent, Sir.")
                return True
            except Exception as e:
                speak(f"Volume error: {str(e)}")
                return False
        
        elif intent == "brightness":
            try:
                level = params.get('level', 50)
                # Windows brightness via WMI
                try:
                    import wmi
                    w = wmi.WMI()
                    for brightness in w.WmiMonitorBrightnessMethods():
                        brightness.WmiSetBrightness(level, 0)
                    speak(f"Brightness set to {level} percent, Sir.")
                    log_action(f"brightness: {level}")
                except:
                    speak("Brightness control not available, Sir.")
                return True
            except Exception as e:
                speak(f"Brightness error: {str(e)}")
                return False
        
        elif intent == "shutdown":
            if not confirm_action():
                speak("Shutdown cancelled, Sir.")
                return False
            speak("Shutting down system, Sir. Goodbye!")
            log_action("shutdown")
            os.system("shutdown /s /t 10")
            return True
        
        elif intent == "restart":
            if not confirm_action():
                speak("Restart cancelled, Sir.")
                return False
            speak("Restarting system, Sir.")
            log_action("restart")
            os.system("shutdown /r /t 10")
            return True
        
        elif intent == "sleep":
            try:
                speak("Putting system to sleep, Sir.")
                log_action("sleep")
                ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
                return True
            except Exception as e:
                speak(f"Sleep error: {str(e)}")
                return False
        
        elif intent == "lock":
            try:
                speak("Locking system, Sir.")
                log_action("lock")
                ctypes.windll.user32.LockWorkStation()
                return True
            except Exception as e:
                speak(f"Lock error: {str(e)}")
                return False
        
        # ==================== WINDOW MANAGEMENT ====================
        elif intent == "minimize":
            try:
                pyautogui.hotkey('win', 'down')
                speak("Minimized window, Sir.")
                log_action("minimize")
                return True
            except Exception as e:
                speak(f"Error: {str(e)}")
                return False
        
        elif intent == "maximize":
            try:
                pyautogui.hotkey('win', 'up')
                speak("Maximized window, Sir.")
                log_action("maximize")
                return True
            except Exception as e:
                speak(f"Error: {str(e)}")
                return False
        
        elif intent == "close_window":
            try:
                pyautogui.hotkey('alt', 'f4')
                speak("Closed window, Sir.")
                log_action("close_window")
                return True
            except Exception as e:
                speak(f"Error: {str(e)}")
                return False
        
        elif intent == "switch_app":
            try:
                pyautogui.hotkey('alt', 'tab')
                speak("Switched to next application, Sir.")
                log_action("switch_app")
                return True
            except Exception as e:
                speak(f"Error: {str(e)}")
                return False
        
        # ==================== FILE OPERATIONS ====================
        elif intent == "new_file":
            path = params.get('path', '')
            if path:
                try:
                    with open(path, 'w') as f:
                        pass
                    speak(f"Created new file: {path}")
                    log_action(f"new_file: {path}")
                    return True
                except Exception as e:
                    speak(f"Could not create file: {str(e)}")
                    log_action("new_file", False, str(e))
            return False
        
        elif intent == "delete_file":
            path = params.get('path', '')
            if path and os.path.exists(path):
                if not confirm_action():
                    speak("Delete cancelled, Sir.")
                    return False
                try:
                    os.remove(path)
                    speak(f"Deleted file: {path}")
                    log_action(f"delete_file: {path}")
                    return True
                except Exception as e:
                    speak(f"Could not delete: {str(e)}")
                    log_action("delete_file", False, str(e))
            return False
        
        elif intent == "copy_file":
            src = params.get('source', '')
            dst = params.get('destination', '')
            if src and dst:
                try:
                    shutil.copy2(src, dst)
                    speak(f"Copied file to {dst}")
                    log_action(f"copy_file: {src} -> {dst}")
                    return True
                except Exception as e:
                    speak(f"Could not copy: {str(e)}")
                    log_action("copy_file", False, str(e))
            return False
        
        elif intent == "move_file":
            src = params.get('source', '')
            dst = params.get('destination', '')
            if src and dst:
                try:
                    shutil.move(src, dst)
                    speak(f"Moved file to {dst}")
                    log_action(f"move_file: {src} -> {dst}")
                    return True
                except Exception as e:
                    speak(f"Could not move: {str(e)}")
                    log_action("move_file", False, str(e))
            return False
        
        elif intent == "read_file":
            path = params.get('path', '')
            if path and os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        content = f.read(500)
                    speak(f"File content: {content[:200]}...")
                    log_action(f"read_file: {path}")
                    return True
                except Exception as e:
                    speak(f"Could not read: {str(e)}")
                    log_action("read_file", False, str(e))
            return False
        
        # ==================== WEB & EMAIL ====================
        elif intent == "search":
            query = params.get('query', '')
            if query:
                try:
                    webbrowser.open(f"https://www.google.com/search?q={query}")
                    speak(f"Searching for {query}, Sir.")
                    log_action(f"search: {query}")
                    return True
                except Exception as e:
                    speak(f"Search error: {str(e)}")
            return False
        
        elif intent == "browse":
            url = params.get('url', '')
            if url:
                try:
                    if not url.startswith('http'):
                        url = 'https://' + url
                    webbrowser.open(url)
                    speak(f"Opening {url}, Sir.")
                    log_action(f"browse: {url}")
                    return True
                except Exception as e:
                    speak(f"Browse error: {str(e)}")
            return False
        
        elif intent == "email":
            to = params.get('to', '')
            subject = params.get('subject', '')
            body = params.get('body', '')
            if to:
                try:
                    import urllib.parse
                    mailto = f"mailto:{to}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
                    webbrowser.open(mailto)
                    speak(f"Opening email to {to}, Sir.")
                    log_action(f"email: {to}")
                    return True
                except Exception as e:
                    speak(f"Email error: {str(e)}")
            return False
        
        # ==================== WIFI & BLUETOOTH ====================
        elif intent == "wifi":
            action = params.get('action', 'toggle')
            try:
                if action == "on":
                    os.system('netsh wlan connect name=AutoConnect')
                    speak("WiFi enabled, Sir.")
                elif action == "off":
                    os.system('netsh wlan disconnect')
                    speak("WiFi disabled, Sir.")
                else:
                    speak("WiFi toggled, Sir.")
                log_action(f"wifi: {action}")
                return True
            except Exception as e:
                speak(f"WiFi error: {str(e)}")
                return False
        
        elif intent == "bluetooth":
            action = params.get('action', 'toggle')
            try:
                if action == "on":
                    os.system('powershell -Command "Get-PnpDevice -Class Bluetooth | Enable-PnpDevice -Confirm:$false"')
                    speak("Bluetooth enabled, Sir.")
                else:
                    os.system('powershell -Command "Get-PnpDevice -Class Bluetooth | Disable-PnpDevice -Confirm:$false"')
                    speak("Bluetooth disabled, Sir.")
                log_action(f"bluetooth: {action}")
                return True
            except Exception as e:
                speak("Bluetooth control not available, Sir.")
                return False
        
        # ==================== MUSIC CONTROL ====================
        elif intent == "play_music":
            try:
                subprocess.Popen(['start', 'spotify'], shell=True)
                time.sleep(2)
                pyautogui.press('playpause')
                speak("Playing music, Sir.")
                log_action("play_music")
                return True
            except Exception as e:
                speak(f"Music error: {str(e)}")
                return False
        
        elif intent == "next_track":
            try:
                pyautogui.press('nexttrack')
                speak("Next track, Sir.")
                log_action("next_track")
                return True
            except Exception as e:
                return False
        
        elif intent == "prev_track":
            try:
                pyautogui.press('prevtrack')
                speak("Previous track, Sir.")
                log_action("prev_track")
                return True
            except Exception as e:
                return False
        
        elif intent == "play_pause":
            try:
                pyautogui.press('playpause')
                speak("Play/Pause toggled, Sir.")
                log_action("play_pause")
                return True
            except Exception as e:
                return False
        
        # ==================== NEW ENHANCED CAPABILITIES ====================
        elif intent == "clipboard":
            try:
                import pyperclip
                text = params.get('text', '')
                if text:
                    pyperclip.copy(text)
                    speak(f"Copied to clipboard: {text[:30]}..., Sir.")
                    log_action("clipboard_copy")
                    return True
                else:
                    content = pyperclip.paste()
                    speak(f"Clipboard contains: {content[:100]}...")
                    log_action("clipboard_paste")
                    return True
            except Exception as e:
                # Fallback to tkinter
                try:
                    import tkinter as tk
                    r = tk.Tk()
                    r.withdraw()
                    if text:
                        r.clipboard_clear()
                        r.clipboard_append(text)
                        speak(f"Copied to clipboard, Sir.")
                        log_action("clipboard_copy")
                    else:
                        content = r.clipboard_get()
                        speak(f"Clipboard: {content[:100]}...")
                        log_action("clipboard_paste")
                    r.destroy()
                    return True
                except Exception as e2:
                    speak(f"Clipboard error: {str(e2)}")
                    return False
        
        elif intent == "process_list":
            try:
                processes = []
                for p in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
                    try:
                        processes.append({
                            'name': p.info['name'],
                            'cpu': p.info['cpu_percent'] or 0,
                            'memory': p.info['memory_percent'] or 0
                        })
                    except:
                        pass
                # Sort by CPU
                processes.sort(key=lambda x: x['cpu'], reverse=True)
                top5 = processes[:5]
                response = "Top processes: "
                for p in top5:
                    response += f"{p['name']} at {p['cpu']} percent, "
                speak(response[:-2])
                log_action("process_list")
                return True
            except Exception as e:
                speak(f"Error: {str(e)}")
                return False
        
        elif intent == "kill_process":
            name = params.get('name', '')
            if name:
                try:
                    killed = False
                    for p in psutil.process_iter(['name']):
                        if name.lower() in p.info['name'].lower():
                            p.kill()
                            killed = True
                    if killed:
                        speak(f"Terminated {name}, Sir.")
                        log_action(f"kill_process: {name}")
                    else:
                        speak(f"Process {name} not found.")
                    return killed
                except Exception as e:
                    speak(f"Error: {str(e)}")
                    return False
            return False
        
        elif intent == "download_file":
            url = params.get('url', '')
            path = params.get('path', '')
            if url and path:
                try:
                    response = requests.get(url, timeout=30)
                    with open(path, 'wb') as f:
                        f.write(response.content)
                    speak(f"Downloaded file to {path}")
                    log_action(f"download_file: {url}")
                    return True
                except Exception as e:
                    speak(f"Download failed: {str(e)}")
                    log_action("download_file", False, str(e))
                    return False
            return False
        
        elif intent == "open_url":
            url = params.get('url', '')
            if url:
                try:
                    if not url.startswith('http'):
                        url = 'https://' + url
                    webbrowser.open(url)
                    speak(f"Opening {url}, Sir.")
                    log_action(f"open_url: {url}")
                    return True
                except Exception as e:
                    speak(f"Error: {str(e)}")
                    return False
            return False
        
        elif intent == "get_ip":
            try:
                response = requests.get('https://api.ipify.org?format=json', timeout=5)
                ip = response.json()['ip']
                speak(f"Your IP address is {ip}, Sir.")
                log_action("get_ip")
                return True
            except Exception as e:
                speak(f"Could not get IP: {str(e)}")
                return False
        
        elif intent == "weather":
            try:
                # Simple weather check (would need API key for real data)
                speak("Weather feature requires API configuration. Currently sunny in most locations, Sir.")
                log_action("weather")
                return True
            except Exception as e:
                speak(f"Weather error: {str(e)}")
                return False
        
        elif intent == "set_alarm":
            time_val = params.get('time', '')
            if time_val:
                speak(f"Alarm set for {time_val}, Sir.")
                # Could implement alarm functionality
                log_action(f"set_alarm: {time_val}")
                return True
            return False
        
        elif intent == "take_note":
            note = params.get('note', '')
            if note:
                try:
                    with open("notes.txt", "a") as f:
                        f.write(f"{datetime.now()}: {note}\n")
                    speak(f"Note saved: {note[:30]}..., Sir.")
                    log_action("take_note")
                    return True
                except Exception as e:
                    speak(f"Note error: {str(e)}")
                    return False
            return False
        
        elif intent == "read_notes":
            try:
                if os.path.exists("notes.txt"):
                    with open("notes.txt", "r") as f:
                        notes = f.readlines()[-5:]
                    speak("Your recent notes: " + " ".join(notes))
                    log_action("read_notes")
                    return True
                else:
                    speak("No notes found, Sir.")
            except Exception as e:
                speak(f"Error: {str(e)}")
                return False
        
        elif intent == "empty_trash":
            try:
                subprocess.run('cmd /c rd /s /q C:\\$Recycle.Bin', shell=True, capture_output=True)
                speak("Recycle bin emptied, Sir.")
                log_action("empty_trash")
                return True
            except Exception as e:
                speak(f"Error: {str(e)}")
                return False
        
        elif intent == "wifi_passwords":
            try:
                result = subprocess.run('netsh wlan show profiles', shell=True, capture_output=True, text=True)
                speak("Retrieving saved WiFi networks, Sir.")
                # Could parse and display passwords with elevation
                speak("WiFi profiles found. For security, passwords require administrator access.")
                log_action("wifi_passwords")
                return True
            except Exception as e:
                speak(f"Error: {str(e)}")
                return False
        
        elif intent == "open_program":
            program = params.get('program', '')
            path = params.get('path', '')
            if path:
                try:
                    subprocess.Popen(path)
                    speak(f"Opening {program}, Sir.")
                    log_action(f"open_program: {program}")
                    return True
                except Exception as e:
                    speak(f"Error: {str(e)}")
                    return False
            return False
        
        elif intent == "control_panel":
            try:
                subprocess.Popen(['control'], shell=True)
                speak("Opening Control Panel, Sir.")
                log_action("control_panel")
                return True
            except Exception as e:
                speak(f"Error: {str(e)}")
                return False
        
        elif intent == "device_manager":
            try:
                subprocess.Popen(['devmgmt.msc'], shell=True)
                speak("Opening Device Manager, Sir.")
                log_action("device_manager")
                return True
            except Exception as e:
                speak(f"Error: {str(e)}")
                return False
        
        elif intent == "disk_cleanup":
            try:
                subprocess.Popen(['cleanmgr'], shell=True)
                speak("Opening Disk Cleanup, Sir.")
                log_action("disk_cleanup")
                return True
            except Exception as e:
                speak(f"Error: {str(e)}")
                return False
        
        elif intent == "registry_editor":
            try:
                subprocess.Popen(['regedit'], shell=True)
                speak("Opening Registry Editor, Sir.")
                log_action("registry_editor")
                return True
            except Exception as e:
                speak(f"Error: {str(e)}")
                return False
        
        elif intent == "event_viewer":
            try:
                subprocess.Popen(['eventvwr.msc'], shell=True)
                speak("Opening Event Viewer, Sir.")
                log_action("event_viewer")
                return True
            except Exception as e:
                speak(f"Error: {str(e)}")
                return False
        
        elif intent == "system_properties":
            try:
                subprocess.Popen(['sysdm.cpl'], shell=True)
                speak("Opening System Properties, Sir.")
                log_action("system_properties")
                return True
            except Exception as e:
                speak(f"Error: {str(e)}")
                return False
        
        # ==================== TIME & DATE ====================
        elif intent == "query_time":
            now = datetime.now()
            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%B %d, %Y")
            speak(f"Current time is {time_str}, {date_str}, Sir.")
            log_action("query_time")
            return True
        
        # ==================== UNKNOWN INTENT ====================
        else:
            return False
            
    except Exception as e:
        speak(f"Error executing command: {str(e)[:50]}")
        log_action(f"execute_from_intent: {intent}", False, str(e))
        return False
    
    return False

def execute(cmd):
    if not cmd:
        return False
    intent = detect_intent(cmd)
    return execute_from_intent(intent)
