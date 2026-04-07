# AudioStream - Customizable High-Definition Audio Player

A versatile, cross-platform audio player with support for high-definition/lossless formats, auto-detecting outputs, custom scripting for features, auto-torrenting capabilities, hardware controls for small devices (RPi/ESP), display integration, and a web app for network-based music uploads.

## Features

- **High-Definition Audio Support**: Plays FLAC, WAV, DSD, and other lossless formats
- **Auto Output Detection**: Automatically detects available audio outputs and allows manual selection
- **Custom DSL**: Define custom features and behaviors using a simple domain-specific language
- **Auto-Torrenting**: Automatically download high-definition/lossless music from torrent sources
- **Hardware Controls**: Support for button inputs on Raspberry Pi, ESP32, and similar devices
- **Display Integration**: LCD/OLED display support to show currently playing music
- **Web App**: Upload music to your device over the local network
- **Cross-Platform**: Runs on desktops (Windows/macOS/Linux), Raspberry Pi, and microcontroller-compatible devices

## Project Structure

```
AudioStream/
├── core/                      # Core audio engine
│   ├── audio_player.py       # Main audio playback engine
│   ├── output_manager.py     # Audio output detection and selection
│   ├── format_handler.py     # Support for various audio formats
│   └── dsp_effects.py        # Real-time DSP effects
├── dsl/                       # Domain-Specific Language
│   ├── parser.py             # DSL parser
│   ├── interpreter.py        # DSL interpreter
│   └── builtins.py           # Built-in DSL functions
├── torrenting/                # Auto-torrenting system
│   ├── torrent_manager.py    # Torrent download management
│   ├── music_indexer.py      # Music metadata indexing
│   └── sources.py            # Torrent source configurations
├── hardware/                  # Hardware integration
│   ├── rpi_gpio.py           # Raspberry Pi GPIO support
│   ├── esp_interface.py      # ESP32/ESP8266 communication
│   ├── display_driver.py     # Display (LCD/OLED) support
│   └── button_handler.py     # Button input and debouncing
├── web/                       # Web interface and API
│   ├── app.py                # Flask/FastAPI app
│   ├── routes.py             # API routes
│   ├── websocket_handler.py  # Real-time status updates
│   ├── upload_handler.py     # File upload management
│   └── static/               # Frontend assets
│       ├── index.html
│       ├── style.css
│       └── app.js
├── config/                    # Configuration files
│   ├── config.py             # Configuration management
│   ├── default_config.yaml   # Default settings
│   └── feature_scripts/      # User-defined DSL scripts
├── library/                   # Music library management
│   ├── library_manager.py    # Track and album management
│   ├── metadata_handler.py   # Music metadata parsing
│   └── db_manager.py         # Database operations
├── utils/                     # Utility modules
│   ├── logger.py             # Logging setup
│   ├── file_utils.py         # File operations
│   └── network_utils.py      # Network utilities
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── setup.py                   # Package setup
└── README.md                  # This file
```

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- For Raspberry Pi: RPi.GPIO or gpiozero
- For ESP devices: MicroPython environment

### Setup

1. Clone or download the project:
```bash
cd PersonalProject
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

## Usage

### Desktop Application
```bash
python main.py --mode desktop
```

### Raspberry Pi (Headless with Hardware Controls)
```bash
python main.py --mode rpi --config config/rpi_config.yaml
```

### ESP32 Integration
```bash
# First, flash MicroPython to ESP device, then:
python main.py --mode server  # Run server on PC/RPi
# ESP connects to server via network
```

### Web App
Access the web interface at `http://localhost:5000` from any device on your network.

## Configuration

Edit `config/default_config.yaml` to customize:
- Audio output preferences
- Feature scripts (DSL)
- Hardware button mappings
- Torrent sources
- Display settings
- Web interface port

## API Documentation

### Audio Player API
```python
from core.audio_player import AudioPlayer

player = AudioPlayer()
player.load_file('path/to/music.flac')
player.play()
player.pause()
player.set_volume(0.8)
```

### Custom DSL Example
```
define FEATURE "AutoNext" {
    on_song_end {
        next_track()
        display_show("Next: {now_playing}")
    }
}
```

### Web Upload
POST to `/api/upload` with file content.

## Development Roadmap

- [x] Project structure
- [ ] Core audio player
- [ ] Output detection and selection
- [ ] DSL parser and interpreter
- [ ] Hardware GPIO support (RPi)
- [ ] Web app with upload
- [ ] Torrent integration
- [ ] Display driver support
- [ ] ESP integration
- [ ] Metadata and library management
- [ ] Testing suite

## Contributing

Contributions are welcome! Please fork the project and submit a pull request.

## License

MIT License - See LICENSE file for details

## Support

For issues, feature requests, or questions, please open an issue on the project repository.

