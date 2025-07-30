"""
Remote Manager for QT Android Remote Control

Handles loading and saving Android TV remote configurations with proper cross-platform
config directory support.
"""

import json
import os
from pathlib import Path
import platform


def get_config_dir():
    """Get the appropriate configuration directory for the current OS"""
    system = platform.system()
    
    if system == "Windows":
        # Windows: Use APPDATA
        config_dir = Path(os.environ.get("APPDATA", "")) / "QTAndroidRemote"
    elif system == "Darwin":
        # macOS: Use ~/Library/Application Support
        config_dir = Path.home() / "Library" / "Application Support" / "QTAndroidRemote"
    else:
        # Linux and others: Use XDG_CONFIG_HOME or ~/.config
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            config_dir = Path(xdg_config) / "qt-android-remote"
        else:
            config_dir = Path.home() / ".config" / "qt-android-remote"
    
    # Create directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_remotes_file():
    """Get the path to the remotes configuration file"""
    return get_config_dir() / "remotes.json"


def get_certs_dir():
    """Get the directory for storing certificates"""
    certs_dir = get_config_dir() / "certs"
    certs_dir.mkdir(parents=True, exist_ok=True)
    return certs_dir


def load_remotes():
    """Load remote configurations from the config file"""
    remotes_file = get_remotes_file()
    
    if remotes_file.exists():
        try:
            with open(remotes_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading remotes configuration: {e}")
            return []
    
    return []


def save_remotes(remotes):
    """Save remote configurations to the config file"""
    remotes_file = get_remotes_file()
    
    try:
        with open(remotes_file, "w", encoding="utf-8") as f:
            json.dump(remotes, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving remotes configuration: {e}")


class RemoteManager:
    """Manager class for handling Android TV remote configurations"""
    
    def __init__(self):
        self.remotes = load_remotes()
    
    def get_remotes(self):
        """Get all configured remotes"""
        return self.remotes
    
    def add_remote(self, remote_config):
        """Add a new remote configuration"""
        self.remotes.append(remote_config)
        save_remotes(self.remotes)
    
    def update_remote(self, index, remote_config):
        """Update an existing remote configuration"""
        if 0 <= index < len(self.remotes):
            self.remotes[index] = remote_config
            save_remotes(self.remotes)
    
    def delete_remote(self, index):
        """Delete a remote configuration"""
        if 0 <= index < len(self.remotes):
            del self.remotes[index]
            save_remotes(self.remotes)
    
    def reload(self):
        """Reload remotes from file"""
        self.remotes = load_remotes()


# Example usage (for testing)
if __name__ == "__main__":
    # Add some dummy remotes
    dummy_remotes = [
        {
            "name": "Living Room Android TV",
            "host": "192.168.1.100",
            "client_name": "QT Android Remote",
            "cert_file": "living_room_cert.pem",
            "key_file": "living_room_key.pem"
        },
        {
            "name": "Bedroom Android TV",
            "host": "192.168.1.101",
            "client_name": "QT Android Remote",
            "cert_file": "bedroom_cert.pem",
            "key_file": "bedroom_key.pem"
        }
    ]
    save_remotes(dummy_remotes)
    print(f"Dummy remotes saved to: {get_remotes_file()}")

    # Load and print remotes
    loaded_remotes = load_remotes()
    print("Loaded remotes:")
    for remote in loaded_remotes:
        print(remote)