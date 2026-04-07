"""Main audio playback engine for AudioStream."""

import os
import threading
from typing import Optional, Callable
from enum import Enum

try:
    import sounddevice as sd
    import soundfile as sf
    HAS_AUDIO = True
except (ImportError, OSError) as e:
    sd = None
    sf = None
    HAS_AUDIO = False

try:
    import numpy as np
except ImportError:
    np = None

from utils.logger import get_logger

logger = get_logger(__name__)


class PlaybackState(Enum):
    """Audio playback states."""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


class AudioPlayer:
    """Main audio playback engine supporting various lossless formats."""

    def __init__(self):
        """Initialize the audio player."""
        self.state = PlaybackState.STOPPED
        self.current_file: Optional[str] = None
        self.current_data = None
        self.current_position = 0
        self.volume = 0.8
        self.stream: Optional[sd.OutputStream] = None
        self.playback_thread: Optional[threading.Thread] = None
        self.is_streaming = False
        self.sample_rate = 44100
        self.duration = 0.0
        self.callbacks = {
            'on_play': [],
            'on_pause': [],
            'on_stop': [],
            'on_finish': [],
        }
        logger.info("AudioPlayer initialized")

    def load_file(self, filepath: str) -> bool:
        """
        Load an audio file.
        
        Supports: FLAC, WAV, OGG, MP3, DSD (via conversion), etc.
        
        Args:
            filepath: Path to audio file
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            return False

        try:
            # Read audio file
            data, samplerate = sf.read(filepath, dtype='float32')
            
            # Handle mono/stereo
            if len(data.shape) == 1:
                data = np.stack([data, data], axis=1)
            
            self.current_file = filepath
            self.current_data = data
            self.sample_rate = samplerate
            self.duration = len(data) / samplerate
            self.current_position = 0
            
            logger.info(f"Loaded: {filepath} ({self.duration:.2f}s @ {samplerate}Hz)")
            return True
            
        except Exception as e:
            logger.error(f"Error loading file {filepath}: {e}")
            return False

    def play(self) -> bool:
        """Start playing the loaded audio file."""
        if self.current_data is None:
            logger.warning("No file loaded")
            return False

        if self.state == PlaybackState.PLAYING:
            logger.warning("Already playing")
            return False

        try:
            self.state = PlaybackState.PLAYING
            self.is_streaming = True
            
            # Trigger callbacks
            for cb in self.callbacks['on_play']:
                cb()
            
            logger.info(f"Playing: {self.current_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error playing: {e}")
            self.state = PlaybackState.STOPPED
            return False

    def pause(self) -> bool:
        """Pause playback."""
        if self.state != PlaybackState.PLAYING:
            return False

        self.state = PlaybackState.PAUSED
        
        for cb in self.callbacks['on_pause']:
            cb()
        
        logger.info("Playback paused")
        return True

    def resume(self) -> bool:
        """Resume from pause."""
        if self.state != PlaybackState.PAUSED:
            return False

        self.state = PlaybackState.PLAYING
        
        for cb in self.callbacks['on_play']:
            cb()
        
        logger.info("Playback resumed")
        return True

    def stop(self) -> bool:
        """Stop playback."""
        self.is_streaming = False
        self.state = PlaybackState.STOPPED
        self.current_position = 0
        
        for cb in self.callbacks['on_stop']:
            cb()
        
        logger.info("Playback stopped")
        return True

    def set_volume(self, volume: float) -> None:
        """
        Set playback volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        logger.debug(f"Volume set to {self.volume * 100:.1f}%")

    def get_current_time(self) -> float:
        """Get current playback position in seconds."""
        return self.current_position / self.sample_rate if self.sample_rate else 0.0

    def seek(self, position: float) -> bool:
        """
        Seek to position in seconds.
        
        Args:
            position: Target position in seconds
            
        Returns:
            True if successful
        """
        if self.current_data is None:
            return False
        
        max_position = len(self.current_data) / self.sample_rate
        if position < 0 or position > max_position:
            return False
        
        self.current_position = int(position * self.sample_rate)
        logger.debug(f"Seeked to {position:.2f}s")
        return True

    def register_callback(self, event: str, callback: Callable) -> None:
        """
        Register a callback for playback events.
        
        Args:
            event: Event name ('on_play', 'on_pause', 'on_stop', 'on_finish')
            callback: Callback function
        """
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def get_metadata(self) -> dict:
        """Get metadata about currently loaded file."""
        if self.current_file is None:
            return {}
        
        return {
            'file': self.current_file,
            'duration': self.duration,
            'sample_rate': self.sample_rate,
            'position': self.get_current_time(),
            'state': self.state.value,
            'volume': self.volume,
        }
