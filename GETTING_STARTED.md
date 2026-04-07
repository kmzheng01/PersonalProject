# AudioStream - Getting Started

Welcome to **AudioStream**, a powerful, customizable high-definition audio player with advanced features for music management, streaming, and hardware integration.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone/Navigate to project**:
   ```bash
   cd /workspaces/PersonalProject
   ```

2. **Create virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**:
   ```bash
   python test_imports.py
   ```

### Running AudioStream

#### Desktop Mode (Interactive Menu)
```bash
python main.py --mode desktop
```
This launches the interactive command-line menu for local control.

#### Web Server Mode
```bash
python main.py --mode web
```
Access the web interface at `http://localhost:5000`

#### Raspberry Pi Headless Mode
```bash
python main.py --mode rpi --config config/rpi_config.yaml
```
Runs without display, controlled via GPIO buttons.

#### Server Mode (Combines web + audio)
```bash
python main.py --mode server
```

## 🎯 Features Overview

### 1. **High-Definition Audio Playback**
- Support for lossless formats: FLAC, WAV, ALAC, DSD
- Automatic sample rate detection and handling
- Volume control and real-time DSP effects

### 2. **Auto Output Detection**
- Automatically detects connected audio outputs (HDMI, USB, Analog)
- Intelligent selection based on device type
- Manual output switching capability

### 3. **Custom DSL (Domain-Specific Language)**
Create custom features and automation rules:
```dsl
define FEATURE "AutoNext" {
    on_song_end {
        next_track()
        display_show("Next: {now_playing}")
    }
}
```

### 4. **Hardware Integration**
- **Raspberry Pi**: GPIO button support, LCD display control
- **ESP32/ESP8266**: Network communication via MicroPython
- Display support: 16x2 LCD, OLED screens
- Multiple button configurations for track control

### 5. **Music Library Management**
- Automatic scanning of music directories
- Track metadata extraction and indexing
- SQLite database for library persistence
- Fast search and filtering capabilities

### 6. **Web Interface**
- Upload music files directly from any device on the network
- Browse and manage your library
- Control playback remotely
- View now-playing information in real-time

### 7. **Auto-Torrenting** (Optional)
Configure automatic downloading of lossless music from legal sources.

## 📁 Project Structure

```
AudioStream/
├── core/                    # Audio engine
│   ├── audio_player.py     # Playback engine
│   ├── output_manager.py   # Output detection/selection
│   ├── format_handler.py   # Audio format support
│   └── dsp_effects.py      # Real-time effects
├── dsl/                     # Custom scripting language
│   ├── parser.py           # DSL parser
│   ├── interpreter.py      # DSL interpreter
│   └── builtins.py         # Built-in functions
├── hardware/               # Device integration
│   ├── button_handler.py   # Button input processing
│   ├── display_driver.py   # Display control
│   ├── rpi_gpio.py        # Raspberry Pi support
│   └── esp_interface.py    # ESP device communication
├── web/                    # Web interface
│   ├── app.py             # Flask application
│   ├── routes.py          # API endpoints
│   ├── upload_handler.py  # File uploads
│   └── static/            # Frontend assets
├── library/               # Music library management
│   ├── library_manager.py # Main library handler
│   ├── metadata_handler.py# Metadata extraction
│   └── db_manager.py      # Database operations
├── torrenting/            # Torrent integration
│   ├── torrent_manager.py # Download management
│   ├── music_indexer.py   # Music metadata indexing
│   └── sources.py         # Torrent sources
├── config/                # Configuration
│   ├── config.py         # Config manager
│   ├── default_config.yaml # Default settings
│   └── feature_scripts/    # User DSL scripts
├── utils/                 # Utilities
│   ├── logger.py         # Logging setup
│   ├── file_utils.py     # File operations
│   └── network_utils.py  # Network utilities
├── main.py               # Entry point
├── requirements.txt      # Dependencies
└── README.md            # Full documentation
```

## ⚙️ Configuration

Edit `config/default_config.yaml` to customize:

### Audio Settings
```yaml
audio:
  sample_rate: 44100      # Hz
  channels: 2             # Mono=1, Stereo=2
  format: PCM_16          # Bit depth
  auto_output_detect: true
```

### Hardware Configuration
```yaml
hardware:
  enable_rpi_gpio: true
  enable_display: true
  rpi:
    debounce_ms: 50        # Button debouncing
    long_press_ms: 1000
```

### Web Server
```yaml
web:
  host: 0.0.0.0
  port: 5000
  upload_dir: ./uploads
  max_file_size: 5368709120  # 5GB
```

### Playback Options
```yaml
playback:
  shuffle: false
  repeat: off              # off, one, all
  autoplay: true
  crossfade: false
```

## 🛠️ Development

### Running Tests
```bash
python test_imports.py
```

### Code Style
```bash
black .                    # Format code
pylint *.py              # Lint code
```

### Logging
Logs are written to console and can be configured in `utils/logger.py`.

## 🌐 Web API Endpoints

### Get Status
```bash
GET /health               # Server health check
```

### Music Library
```bash
GET /api/library          # List all tracks
GET /api/library/search   # Search tracks
POST /api/library/scan    # Scan for new files
```

### Playback Control
```bash
POST /api/player/play     # Start playing
POST /api/player/pause    # Pause playback
POST /api/player/stop     # Stop playback
POST /api/player/next     # Next track
POST /api/player/previous # Previous track
```

### File Upload
```bash
POST /api/upload          # Upload music file
```

## 🐛 Troubleshooting

### "sounddevice not available"
- Audio libraries require PortAudio system library
- On Ubuntu: `sudo apt-get install portaudio19-dev`
- The app still works in demo mode without audio hardware

### "No modules found"
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version is 3.8 or higher: `python --version`

### Import errors
- Run `python test_imports.py` to check all imports
- Ensure you're in the correct directory
- Try reinstalling dependencies: `pip install --upgrade -r requirements.txt`

## 📚 Advanced Usage

### Custom DSL Features
Create `.dsl` files in `config/feature_scripts/` to extend functionality.

### Raspberry Pi Setup
1. Install RPi.GPIO: `pip install RPi.GPIO`
2. Connect buttons to GPIO pins (configure in config.yaml)
3. Run: `python main.py --mode rpi`

### ESP32 Integration
1. Flash MicroPython to device
2. Configure ESP IP in config.yaml
3. Run server mode on main device
4. ESP will auto-connect via network

## 📝 Contributing

Contributions are welcome! Areas for enhancement:
- Additional audio format support
- More DSL built-in functions
- Mobile app frontend
- Cloud music source integration
- Advanced metadata handling

## 📄 License

MIT License - See LICENSE file for details.

## 🤝 Support

For issues, feature requests, or questions:
1. Check troubleshooting section above
2. Review logs in console output
3. Open an issue on the project repository

---

**Happy listening!** 🎵
