import datetime
import json
import os

def format_duration(seconds):
    """
    Convert raw seconds from the engine into a human-readable HH:MM:SS format.
    Used for the VideoCard display.
    """
    if not seconds:
        return "00:00"
    duration = str(datetime.timedelta(seconds=int(seconds)))
    # Remove leading zeros for a cleaner look (e.g., 0:05:30 instead of 00:05:30)
    return duration.lstrip('0:').zfill(4) if duration.startswith('0:') else duration

def format_view_count(views):
    """
    Convert large view counts into shorthand (K, M, B).
    Essential for keeping the UI clean and minimalist.
    """
    if not views:
        return "0 views"
    views = int(views)
    if views >= 1_000_000_000:
        return f"{views / 1_000_000_000:.1f}B views"
    if views >= 1_000_000:
        return f"{views / 1_000_000:.1f}M views"
    if views >= 1_000:
        return f"{views / 1_000:.1f}K views"
    return f"{views} views"

def clean_filename(title):
    """
    Sanitize video titles to be used as safe filenames for the downloader.
    Removes special characters that cause issues in Linux/Windows file systems.
    """
    return "".join([c for c in title if c.isalnum() or c in (' ', '.', '_')]).strip()

def load_config():
    """
    Load user preferences from config.json.
    If the file is missing, returns default 'Helwan' settings.
    """
    config_path = "config.json"
    defaults = {
        "default_player": "mpv",
        "quality": "720",
        "theme": "dark",
        "download_path": os.path.join(os.path.expanduser("~"), "Downloads")
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Ensure all default keys exist in the loaded config
                defaults.update(config)
                return defaults
        except (json.JSONDecodeError, IOError):
            return defaults
    return defaults

def save_config(config_data):
    """
    Save or update user preferences to config.json.
    """
    config_path = "config.json"
    try:
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=4)
        return True
    except IOError:
        return False
