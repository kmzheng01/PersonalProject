"""Metadata handling for music files."""

from typing import Dict, Any
import mutagen

from utils.logger import get_logger

logger = get_logger(__name__)


class MetadataHandler:
    """Handles music file metadata."""

    @staticmethod
    def read_metadata(filepath: str) -> Dict[str, Any]:
        """
        Read metadata from audio file.
        
        Args:
            filepath: Path to audio file
            
        Returns:
            Dictionary with metadata
        """
        try:
            audio = mutagen.File(filepath)
            
            if audio is None:
                return {}
            
            metadata = {
                'title': 'Unknown',
                'artist': 'Unknown',
                'album': 'Unknown',
                'genre': 'Unknown',
                'year': 0,
                'track_number': 0,
                'album_artist': 'Unknown',
                'composer': 'Unknown',
                'duration': 0,
            }
            
            # Extract available metadata
            for key, value in audio.items():
                if isinstance(value, list) and value:
                    value = value[0]
                value_str = str(value)
                
                if 'title' in key.lower():
                    metadata['title'] = value_str
                elif 'artist' in key.lower():
                    if 'album' not in key.lower():
                        metadata['artist'] = value_str
                elif 'album' in key.lower() and 'artist' not in key.lower():
                    metadata['album'] = value_str
                elif 'genre' in key.lower():
                    metadata['genre'] = value_str
                elif 'date' in key.lower() or 'year' in key.lower():
                    try:
                        metadata['year'] = int(value_str.split('-')[0])
                    except:
                        pass
                elif 'track' in key.lower():
                    try:
                        metadata['track_number'] = int(value_str.split('/')[0])
                    except:
                        pass
            
            if hasattr(audio, 'info'):
                metadata['duration'] = int(audio.info.length)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error reading metadata: {e}")
            return {}

    @staticmethod
    def write_metadata(filepath: str, metadata: Dict[str, Any]) -> bool:
        """
        Write metadata to audio file.
        
        Args:
            filepath: Path to audio file
            metadata: Metadata dictionary
            
        Returns:
            True if successful
        """
        try:
            audio = mutagen.File(filepath, easy=True)
            
            if audio is None:
                return False
            
            for key, value in metadata.items():
                if value is not None:
                    audio[key] = str(value)
            
            audio.save()
            logger.info(f"Metadata written to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing metadata: {e}")
            return False

    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration in seconds to HH:MM:SS."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"
