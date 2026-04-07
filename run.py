#!/usr/bin/env python3
"""
AudioStream Setup and Quick Start Script
Run this to set up and start AudioStream easily.
"""

import os
import subprocess
import sys
import json
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_success(text):
    """Print success message."""
    print(f"✓ {text}")

def print_error(text):
    """Print error message."""
    print(f"✗ {text}")

def check_python_version():
    """Check if Python version is adequate."""
    print_header("Checking Python Version")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    print_header("Checking Dependencies")
    
    required = {
        'flask': 'Flask',
        'yaml': 'PyYAML',
        'numpy': 'NumPy',
    }
    
    optional = {
        'sounddevice': 'Audio playback (sounddevice)',
        'soundfile': 'Audio file support (soundfile)',
        'mutagen': 'Metadata reading (mutagen)',
    }
    
    missing_required = []
    missing_optional = []
    
    for module, name in required.items():
        try:
            __import__(module)
            print_success(name)
        except (ImportError, OSError):
            print_error(name)
            missing_required.append(name)
    
    for module, name in optional.items():
        try:
            __import__(module)
            print_success(name + " (optional)")
        except (ImportError, OSError):
            missing_optional.append(name)
    
    return missing_required, missing_optional

def install_dependencies():
    """Install missing dependencies."""
    print_header("Installing Dependencies")
    
    print("Installing from requirements.txt...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'])
        print_success("Dependencies installed")
        return True
    except Exception as e:
        print_error(f"Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create required directories."""
    print_header("Creating Directories")
    
    dirs = [
        './music',
        './downloads',
        './uploads',
        './config/feature_scripts',
    ]
    
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        print_success(f"Directory ready: {d}")

def choose_mode():
    """Let user choose how to run AudioStream."""
    print_header("AudioStream - Choose Mode")
    
    modes = {
        '1': ('desktop', 'Desktop (Interactive Menu)'),
        '2': ('web', 'Web Server'),
        '3': ('server', 'Server (Web + Audio)'),
        '4': ('rpi', 'Raspberry Pi Headless'),
        '5': ('test', 'Test Mode (Verify Installation)'),
    }
    
    for key, (mode, description) in modes.items():
        print(f"{key}. {description}")
    
    choice = input("\nSelect mode (1-5): ").strip()
    
    if choice in modes:
        return modes[choice][0]
    return 'desktop'

def run_audiostream(mode):
    """Run AudioStream in the selected mode."""
    print_header(f"Starting AudioStream - {mode.upper()} Mode")
    
    if mode == 'test':
        print("Running import tests...")
        subprocess.call([sys.executable, 'test_imports.py'])
    else:
        try:
            subprocess.call([sys.executable, 'main.py', '--mode', mode])
        except KeyboardInterrupt:
            print("\n\nAudioStream stopped by user")

def main():
    """Main setup and run function."""
    print("\n" + "="*60)
    print("  AudioStream - High-Definition Audio Player")
    print("  Setup & Quick Start")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    missing_required, missing_optional = check_dependencies()
    
    if missing_required:
        print_header("Installing Missing Dependencies")
        if not install_dependencies():
            sys.exit(1)
    
    if missing_optional:
        print("\nOptional packages not installed (audio features may be limited):")
        for pkg in missing_optional:
            print(f"  - {pkg}")
    
    # Create directories
    create_directories()
    
    # Choose mode
    mode = choose_mode()
    
    # Run AudioStream
    run_audiostream(mode)

if __name__ == '__main__':
    main()
