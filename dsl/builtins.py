"""Built-in functions for DSL."""

from typing import Dict, Callable, Any
import time

from utils.logger import get_logger

logger = get_logger(__name__)


def get_builtin_functions() -> Dict[str, Callable]:
    """Get all builtin functions available in DSL."""
    
    def print_msg(*args):
        """Print message."""
        msg = ' '.join(str(arg) for arg in args)
        logger.info(f"DSL: {msg}")
        return msg
    
    def sleep_ms(ms: int):
        """Sleep for milliseconds."""
        time.sleep(ms / 1000.0)
        return True
    
    def current_time():
        """Get current time in seconds."""
        return time.time()
    
    def play_sound(sound_name: str):
        """Play a sound."""
        logger.info(f"DSL: Playing sound - {sound_name}")
        return True
    
    def next_track():
        """Go to next track."""
        logger.info("DSL: Next track")
        return True
    
    def previous_track():
        """Go to previous track."""
        logger.info("DSL: Previous track")
        return True
    
    def pause_playback():
        """Pause playback."""
        logger.info("DSL: Pause")
        return True
    
    def resume_playback():
        """Resume playback."""
        logger.info("DSL: Resume")
        return True
    
    def display_show(text: str):
        """Show text on display."""
        logger.info(f"DSL: Display - {text}")
        return True
    
    def display_clear():
        """Clear display."""
        logger.info("DSL: Display cleared")
        return True
    
    def get_now_playing():
        """Get currently playing track info."""
        return {
            'title': 'Unknown',
            'artist': 'Unknown',
            'album': 'Unknown',
            'duration': 0,
            'position': 0,
        }
    
    def set_volume(volume: float):
        """Set volume level."""
        vol_percent = max(0, min(100, volume * 100))
        logger.info(f"DSL: Volume set to {vol_percent:.1f}%")
        return True
    
    def get_volume():
        """Get current volume."""
        return 0.8
    
    def add_to_playlist(track_name: str):
        """Add track to playlist."""
        logger.info(f"DSL: Added to playlist - {track_name}")
        return True
    
    def clear_playlist():
        """Clear current playlist."""
        logger.info("DSL: Playlist cleared")
        return True
    
    def shuffle_playlist(enabled: bool = True):
        """Enable/disable playlist shuffle."""
        logger.info(f"DSL: Shuffle {'enabled' if enabled else 'disabled'}")
        return True
    
    def repeat_mode(mode: str):
        """Set repeat mode: 'off', 'one', 'all'."""
        logger.info(f"DSL: Repeat mode - {mode}")
        return True
    
    def send_notification(title: str, message: str):
        """Send a notification."""
        logger.info(f"DSL: Notification - {title}: {message}")
        return True
    
    def string_concat(*args):
        """Concatenate strings."""
        return ''.join(str(arg) for arg in args)
    
    def string_length(s: str):
        """Get string length."""
        return len(str(s))
    
    def int_add(a: int, b: int):
        """Add two integers."""
        return int(a) + int(b)
    
    def int_subtract(a: int, b: int):
        """Subtract two integers."""
        return int(a) - int(b)
    
    def int_multiply(a: int, b: int):
        """Multiply two integers."""
        return int(a) * int(b)
    
    def int_divide(a: int, b: int):
        """Divide two integers."""
        if b == 0:
            logger.error("Division by zero")
            return 0
        return int(a) // int(b)
    
    def float_add(a: float, b: float):
        """Add two floats."""
        return float(a) + float(b)
    
    def compare_equal(a, b):
        """Check equality."""
        return a == b
    
    def compare_greater(a, b):
        """Check greater than."""
        return a > b
    
    def compare_less(a, b):
        """Check less than."""
        return a < b
    
    def bool_and(a, b):
        """Logical AND."""
        return bool(a) and bool(b)
    
    def bool_or(a, b):
        """Logical OR."""
        return bool(a) or bool(b)
    
    def bool_not(a):
        """Logical NOT."""
        return not bool(a)
    
    return {
        # I/O
        'print': print_msg,
        'display_show': display_show,
        'display_clear': display_clear,
        'notify': send_notification,
        
        # Playback control
        'play': lambda: logger.info("DSL: Play"),
        'pause': pause_playback,
        'resume': resume_playback,
        'next': next_track,
        'previous': previous_track,
        'stop': lambda: logger.info("DSL: Stop"),
        
        # Volume control
        'set_volume': set_volume,
        'get_volume': get_volume,
        
        # Playlist operations
        'add_track': add_to_playlist,
        'clear_playlist': clear_playlist,
        'shuffle': shuffle_playlist,
        'repeat': repeat_mode,
        
        # Info retrieval
        'now_playing': get_now_playing,
        
        # Time functions
        'sleep': sleep_ms,
        'now': current_time,
        
        # String functions
        'concat': string_concat,
        'strlen': string_length,
        
        # Math functions
        'add': int_add,
        'sub': int_subtract,
        'mul': int_multiply,
        'div': int_divide,
        'fadd': float_add,
        
        # Comparison
        'eq': compare_equal,
        'gt': compare_greater,
        'lt': compare_less,
        
        # Logical
        'and': bool_and,
        'or': bool_or,
        'not': bool_not,
    }
