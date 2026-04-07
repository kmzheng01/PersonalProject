"""AudioStream - Main application entry point."""

import argparse
import sys
import os
from pathlib import Path

from utils.logger import get_logger
from config.config import ConfigManager
from core.audio_player import AudioPlayer
from core.output_manager import OutputManager
from core.format_handler import FormatHandler
from core.dsp_effects import DSPEffects
from dsl.parser import DSLParser
from dsl.interpreter import DSLInterpreter
from torrenting.torrent_manager import TorrentManager
from torrenting.music_indexer import MusicIndexer
from torrenting.sources import TorrentSources
from hardware.button_handler import ButtonHandler
from hardware.display_driver import DisplayDriver, DisplayType
from library.library_manager import LibraryManager
from web.app import create_app

logger = get_logger(__name__)


class AudioStream:
    """Main AudioStream application."""

    def __init__(self, config_file: str = 'config/default_config.yaml'):
        """
        Initialize AudioStream.
        
        Args:
            config_file: Configuration file path
        """
        logger.info("=" * 50)
        logger.info("AudioStream - High-Definition Audio Player v1.0.0")
        logger.info("=" * 50)
        
        # Configuration
        self.config = ConfigManager(config_file)
        self.config.validate()
        
        # Core components
        self.player = AudioPlayer()
        self.output_manager = OutputManager()
        self.dsp_effects = DSPEffects()
        
        # DSL
        self.dsl_interpreter = DSLInterpreter()
        
        # Torrenting
        self.torrent_manager = TorrentManager(
            self.config.get('torrenting.download_dir', './downloads')
        )
        self.torrent_sources = TorrentSources()
        
        # Hardware
        self.button_handler = ButtonHandler()
        self.display_driver = None
        if self.config.get('hardware.enable_display', False):
            self.display_driver = DisplayDriver(DisplayType.LCD_16X2)
        
        # Library
        self.library_manager = LibraryManager(
            self.config.get('library.music_dir', './music')
        )
        
        # Web app
        self.web_app = create_app({
            'UPLOAD_FOLDER': './uploads',
        })
        
        logger.info("AudioStream initialized successfully")

    def run_desktop_mode(self):
        """Run in desktop mode."""
        logger.info("Starting in desktop mode...")
        
        # Auto-detect best output
        best_output = self.output_manager.auto_detect_best_output()
        logger.info(f"Auto-selected output: {best_output}")
        
        # Scan library
        if self.config.get('library.auto_scan', True):
            count = self.library_manager.scan_library()
            logger.info(f"Library scanned, found {count} tracks")
        
        # Display menu
        self._show_menu()

    def run_rpi_mode(self):
        """Run in Raspberry Pi mode."""
        logger.info("Starting in Raspberry Pi headless mode...")
        
        # Setup display if available
        if self.display_driver:
            self.display_driver.show_message("AudioStream\nReady")
        
        # Setup buttons
        self._setup_rpi_buttons()
        
        # Auto-detect output
        self.output_manager.auto_detect_best_output()
        
        # Scan library
        if self.config.get('library.auto_scan', True):
            self.library_manager.scan_library()
        
        logger.info("RPi mode ready, waiting for button input...")
        
        # Keep running
        try:
            while True:
                pass
        except KeyboardInterrupt:
            logger.info("Shutting down...")

    def run_web_mode(self):
        """Run web server mode."""
        logger.info("Starting web server...")
        
        host = self.config.get('web.host', '0.0.0.0')
        port = self.config.get('web.port', 5000)
        
        logger.info(f"Web interface available at http://{host}:{port}")
        self.web_app.run(host=host, port=port, debug=False)

    def run_server_mode(self):
        """Run as server with web and audio player."""
        logger.info("Starting in server mode...")
        
        # Scan library
        if self.config.get('library.auto_scan', True):
            count = self.library_manager.scan_library()
            logger.info(f"Library scanned, found {count} tracks")
        
        # Start web server
        self.run_web_mode()

    def _show_menu(self):
        """Show interactive menu."""
        while True:
            print("\n" + "=" * 50)
            print("AudioStream Menu")
            print("=" * 50)
            print("1. Play track")
            print("2. Pause")
            print("3. Resume")
            print("4. Stop")
            print("5. Next track")
            print("6. Previous track")
            print("7. List library")
            print("8. Search library")
            print("9. Settings")
            print("0. Exit")
            print("-" * 50)
            
            choice = input("Select option: ").strip()
            
            if choice == '1':
                self._interactive_play()
            elif choice == '2':
                self.player.pause()
            elif choice == '3':
                self.player.resume()
            elif choice == '4':
                self.player.stop()
            elif choice == '5':
                self.player.call_function('next_track')
            elif choice == '6':
                self.player.call_function('previous_track')
            elif choice == '7':
                self._list_library()
            elif choice == '8':
                self._search_library()
            elif choice == '9':
                self._settings_menu()
            elif choice == '0':
                logger.info("Exiting AudioStream...")
                break
            else:
                print("Invalid option")

    def _interactive_play(self):
        """Interactive track selection."""
        library = self.library_manager.get_all_tracks()
        
        if not library:
            print("No tracks in library")
            return
        
        for i, track in enumerate(library[:10], 1):
            print(f"{i}. {track.title} - {track.artist}")
        
        choice = input("Select track (number): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(library):
                track = library[idx]
                self.player.load_file(track.filepath)
                self.player.play()
                print(f"Playing: {track.title}")
        except:
            print("Invalid selection")

    def _list_library(self):
        """List library tracks."""
        tracks = self.library_manager.get_all_tracks()
        print(f"\nTotal tracks: {len(tracks)}")
        for track in tracks[:20]:
            print(f"  {track.title} - {track.artist} ({track.duration}s)")

    def _search_library(self):
        """Search library."""
        query = input("Search query: ").strip()
        search_type = input("Search by (title/artist/album) [title]: ").strip() or 'title'
        
        results = self.library_manager.search(query, search_type)
        print(f"\nFound {len(results)} results:")
        for track in results:
            print(f"  {track.title} - {track.artist}")

    def _settings_menu(self):
        """Settings menu."""
        print("\n" + "=" * 50)
        print("Settings")
        print("=" * 50)
        print("1. Audio output")
        print("2. Volume")
        print("3. DSP Effects")
        print("0. Back")
        print("-" * 50)
        
        choice = input("Select: ").strip()
        
        if choice == '1':
            self._audio_output_menu()
        elif choice == '2':
            vol = float(input("Volume (0-1): ") or "0.8")
            self.player.set_volume(vol)
        elif choice == '3':
            self._dsp_menu()

    def _audio_output_menu(self):
        """Audio output selection menu."""
        outputs = self.output_manager.list_outputs()
        print(f"\nAvailable outputs:")
        for output in outputs:
            print(f"  {output.device_id}: {output.name} ({output.channels}ch @ {output.sample_rate}Hz)")
        
        device_id = int(input("Select output ID: ") or "0")
        self.output_manager.select_output(device_id)

    def _dsp_menu(self):
        """DSP effects menu."""
        print("\nDSP Effects")
        print("1. Enable/Disable")
        print("2. EQ Preset")
        print("3. Normalizer")
        
        choice = input("Select: ").strip()
        
        if choice == '1':
            self.dsp_effects.enabled = not self.dsp_effects.enabled
            print(f"DSP {'enabled' if self.dsp_effects.enabled else 'disabled'}")
        elif choice == '2':
            print("EQ Presets: flat, bass_boost, treble_boost, warm, bright")
            preset = input("Select preset: ").strip()
            # Set EQ preset
        elif choice == '3':
            self.dsp_effects.enable_normalizer(True)

    def _setup_rpi_buttons(self):
        """Setup hardware buttons for RPi."""
        # Example button setup
        play_btn = self.button_handler.register_button(0, 17, "Play/Pause")
        next_btn = self.button_handler.register_button(1, 27, "Next")
        prev_btn = self.button_handler.register_button(2, 22, "Previous")
        
        logger.info("Buttons configured")

    def load_dsl_scripts(self):
        """Load and execute DSL feature scripts."""
        scripts_dir = self.config.get('dsl.feature_scripts_dir', 'config/feature_scripts')
        
        if not os.path.exists(scripts_dir):
            logger.warning(f"DSL scripts directory not found: {scripts_dir}")
            return
        
        for filename in os.listdir(scripts_dir):
            if filename.endswith('.dsl'):
                filepath = os.path.join(scripts_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        code = f.read()
                    
                    parser = DSLParser(code)
                    ast = parser.parse()
                    self.dsl_interpreter.execute(ast)
                    logger.info(f"Loaded DSL script: {filename}")
                except Exception as e:
                    logger.error(f"Error loading DSL script {filename}: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='AudioStream - High-Definition Audio Player'
    )
    parser.add_argument(
        '--mode',
        choices=['desktop', 'rpi', 'web', 'server'],
        default='desktop',
        help='Operation mode'
    )
    parser.add_argument(
        '--config',
        default='config/default_config.yaml',
        help='Configuration file'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Web server port'
    )
    
    args = parser.parse_args()
    
    # Create application
    app = AudioStream(args.config)
    
    # Load DSL scripts
    app.load_dsl_scripts()
    
    # Run in selected mode
    if args.mode == 'desktop':
        app.run_desktop_mode()
    elif args.mode == 'rpi':
        app.run_rpi_mode()
    elif args.mode == 'web':
        app.run_web_mode()
    elif args.mode == 'server':
        app.run_server_mode()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nShutdown by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
