# JARVIS AI Configuration
# ========================

# API Configuration
import os
API_KEY = os.getenv("JARVIS_API_KEY", "")
# Set your OpenRouter API key in environment: set JARVIS_API_KEY=your_key_here

# Wake Word Configuration
WAKE_WORD = "jarvis"
USE_WAKE_WORD = False  # Set to True to enable wake word detection

# Voice Configuration
VOICE_RATE = 180
VOICE_VOLUME = 1.0

# Application Settings
APP_NAME = "JARVIS AI"
APP_VERSION = "3.0"

# Authentication Settings
USE_FACE_AUTH = True
USE_SPEAKER_AUTH = True

# GUI Settings
GUI_STYLE = "arc_reactor"  # Iron Man style GUI
GUI_ALWAYS_ON_TOP = True

# System Monitoring
MONITOR_INTERVAL = 60  # seconds
ENABLE_ALERTS = True

# Auto Mode
AUTO_MODE_ENABLED = True
AUTO_MODE_INTERVAL = 60  # seconds

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "jarvis.log"

# Default Paths
SCREENSHOT_PATH = "screenshots/"
VOICE_SAMPLES_PATH = "voice_samples/"
FACE_DATA_PATH = "data/faces/"
MODEL_PATH = "trainer.yml"
