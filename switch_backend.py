#!/usr/bin/env python3
"""
Script to switch between different CASI backend configurations
"""

import os
import json
from pathlib import Path

def get_config_path():
    """Get the path to the configuration file."""
    config_dir = os.path.join(os.getenv("APPDATA"), "CASI")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "config.json")

def load_config():
    """Load current configuration."""
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    """Save configuration to file."""
    config_path = get_config_path()
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    return True

def switch_backend():
    """Interactive backend switching."""
    print("🔄 CASI Backend Configuration Switcher")
    print("=" * 40)
    
    # Available backends
    backends = {
        "1": {
            "name": "On-Premise Server",
            "url": "http://172.16.11.69:9000",
            "description": "Local on-premise CASI backend server"
        },
        "2": {
            "name": "Vercel Cloud",
            "url": "https://casto-ai-bot.vercel.app",
            "description": "Cloud-hosted CASI backend on Vercel"
        },
        "3": {
            "name": "Custom URL",
            "url": None,
            "description": "Enter a custom backend URL"
        }
    }
    
    # Show current configuration
    current_config = load_config()
    current_url = current_config.get("backend_url", "Not configured")
    print(f"📍 Current backend: {current_url}")
    print()
    
    # Show options
    print("Available backends:")
    for key, backend in backends.items():
        print(f"  {key}. {backend['name']}")
        print(f"     {backend['description']}")
        if backend['url']:
            print(f"     URL: {backend['url']}")
        print()
    
    # Get user choice
    while True:
        choice = input("Select backend (1-3) or 'q' to quit: ").strip()
        
        if choice.lower() == 'q':
            print("👋 Goodbye!")
            return
        
        if choice in backends:
            break
        else:
            print("❌ Invalid choice. Please select 1, 2, 3, or 'q'.")
    
    # Handle custom URL
    if choice == "3":
        while True:
            custom_url = input("Enter custom backend URL: ").strip()
            if custom_url:
                if not custom_url.startswith(('http://', 'https://')):
                    print("❌ URL must start with http:// or https://")
                    continue
                backends["3"]["url"] = custom_url
                break
            else:
                print("❌ URL cannot be empty")
    
    # Update configuration
    selected_backend = backends[choice]
    config = load_config()
    config["backend_url"] = selected_backend["url"]
    
    if save_config(config):
        print(f"✅ Successfully switched to: {selected_backend['name']}")
        print(f"📍 New backend URL: {selected_backend['url']}")
        print()
        print("💡 Restart CASI application to use the new backend configuration.")
    else:
        print("❌ Failed to save configuration.")

if __name__ == "__main__":
    switch_backend()
