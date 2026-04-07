"""Music indexing and metadata management."""

import os
from typing import List, Dict, Optional
import mutagen
from mutagen.flac import FLAC
from mutagen.wave import WAVE
import json

from utils.logger import get_logger

logger = get_logger(__name__)


class MusicTrack:
    """Represents a music track with metadata."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.title = "Unknown"
        self.artist = "Unknown"
        self.album = "Unknown"
        self.duration = 0
        self.bitrate = 0
        self.sample_rate = 0
        self.channels = 0
        self.format = "Unknown"
        self.lossless = False
        self.year = 0
        self.genre = "Unknown"
        self.track_number = 0
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load metadata from file."""
        try:
            audio = mutagen.File(self.filepath)
            
            if audio is None:
                logger.warning(f"Could not load metadata: {self.filepath}")
                return
            
            # Basic info
            self.duration = int(audio.info.length) if hasattr(audio, 'info') else 0
            
            # Format-specific
            if isinstance(audio, FLAC):
                self.format = "FLAC"
                self.lossless = True
                self.sample_rate = audio.info.sample_rate
                self.channels = audio.info.channels
                self.bitrate = audio.info.bitrate
            elif isinstance(audio, WAVE):
                self.format = "WAV"
                self.lossless = True
            else:
                self.format = audio.mime[0].split('/')[1].upper() if audio.mime else "Unknown"
            
            # Metadata tags
            if 'title' in audio or 'TIT2' in audio:
                self.title = str(audio.get('title') or audio.get('TIT2', ["Unknown"])[0])
            if 'artist' in audio or 'TPE1' in audio:
                self.artist = str(audio.get('artist') or audio.get('TPE1', ["Unknown"])[0])
            if 'album' in audio or 'TALB' in audio:
                self.album = str(audio.get('album') or audio.get('TALB', ["Unknown"])[0])
            if 'genre' in audio or 'TCON' in audio:
                self.genre = str(audio.get('genre') or audio.get('TCON', ["Unknown"])[0])
            if 'date' in audio or 'TDRC' in audio:
                year_str = str(audio.get('date') or audio.get('TDRC', ["0"])[0])
                try:
                    self.year = int(year_str.split('-')[0])
                except:
                    self.year = 0
            if 'tracknumber' in audio or 'TRCK' in audio:
                track_str = str(audio.get('tracknumber') or audio.get('TRCK', ["0"])[0])
                try:
                    self.track_number = int(track_str.split('/')[0])
                except:
                    self.track_number = 0
            
        except Exception as e:
            logger.error(f"Error loading metadata for {self.filepath}: {e}")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'filepath': self.filepath,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'duration': self.duration,
            'format': self.format,
            'lossless': self.lossless,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'bitrate': self.bitrate,
            'year': self.year,
            'genre': self.genre,
            'track_number': self.track_number,
        }


class MusicIndexer:
    """Indexes a music library."""

    SUPPORTED_FORMATS = {'.flac', '.wav', '.ogg', '.mp3', '.m4a', '.aiff', '.alac'}

    def __init__(self):
        """Initialize indexer."""
        self.library: Dict[str, MusicTrack] = {}
        logger.info("MusicIndexer initialized")

    def scan_directory(self, directory: str) -> int:
        """
        Scan directory for music files.
        
        Args:
            directory: Directory to scan
            
        Returns:
            Number of files found
        """
        count = 0
        
        if not os.path.isdir(directory):
            logger.warning(f"Not a directory: {directory}")
            return 0
        
        for root, dirs, files in os.walk(directory):
            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext in self.SUPPORTED_FORMATS:
                    filepath = os.path.join(root, filename)
                    try:
                        track = MusicTrack(filepath)
                        self.library[filepath] = track
                        count += 1
                    except Exception as e:
                        logger.error(f"Error indexing {filepath}: {e}")
        
        logger.info(f"Scanned directory, found {count} music files")
        return count

    def add_file(self, filepath: str) -> bool:
        """Add a file to library."""
        if not os.path.isfile(filepath):
            return False
        
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in self.SUPPORTED_FORMATS:
            return False
        
        try:
            track = MusicTrack(filepath)
            self.library[filepath] = track
            return True
        except Exception as e:
            logger.error(f"Error adding file {filepath}: {e}")
            return False

    def search_by_artist(self, artist: str) -> List[MusicTrack]:
        """Search tracks by artist."""
        results = [
            track for track in self.library.values()
            if artist.lower() in track.artist.lower()
        ]
        return results

    def search_by_album(self, album: str) -> List[MusicTrack]:
        """Search tracks by album."""
        results = [
            track for track in self.library.values()
            if album.lower() in track.album.lower()
        ]
        return results

    def search_by_title(self, title: str) -> List[MusicTrack]:
        """Search tracks by title."""
        results = [
            track for track in self.library.values()
            if title.lower() in track.title.lower()
        ]
        return results

    def get_lossless_tracks(self) -> List[MusicTrack]:
        """Get all lossless tracks."""
        return [t for t in self.library.values() if t.lossless]

    def get_high_def_tracks(self) -> List[MusicTrack]:
        """Get high-definition tracks (96kHz+)."""
        return [
            t for t in self.library.values()
            if t.sample_rate >= 96000 and t.lossless
        ]

    def get_library_stats(self) -> dict:
        """Get library statistics."""
        tracks = list(self.library.values())
        total_duration = sum(t.duration for t in tracks)
        lossless_count = sum(1 for t in tracks if t.lossless)
        hires_count = sum(1 for t in tracks if t.sample_rate >= 96000)
        
        return {
            'total_tracks': len(tracks),
            'total_duration_hours': total_duration / 3600,
            'lossless_tracks': lossless_count,
            'hires_tracks': hires_count,
            'unique_artists': len(set(t.artist for t in tracks)),
            'unique_albums': len(set(t.album for t in tracks)),
        }

    def export_library_json(self, filepath: str) -> bool:
        """Export library to JSON file."""
        try:
            data = {
                'tracks': [t.to_dict() for t in self.library.values()],
                'stats': self.get_library_stats(),
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Exported library to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting library: {e}")
            return False

    def get_all_tracks(self) -> List[MusicTrack]:
        """Get all tracks in library."""
        return list(self.library.values())
