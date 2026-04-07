"""Music library manager."""

from typing import List, Dict, Optional
import os

from torrenting.music_indexer import MusicIndexer, MusicTrack
from utils.logger import get_logger

logger = get_logger(__name__)


class LibraryManager:
    """Manages music library."""

    def __init__(self, library_dir: str = "./music"):
        """
        Initialize library manager.
        
        Args:
            library_dir: Library directory path
        """
        self.library_dir = library_dir
        self.indexer = MusicIndexer()
        os.makedirs(library_dir, exist_ok=True)
        logger.info(f"LibraryManager initialized, library_dir: {library_dir}")

    def scan_library(self, recursive: bool = True) -> int:
        """
        Scan library directory.
        
        Args:
            recursive: Scan subdirectories
            
        Returns:
            Number of tracks found
        """
        count = self.indexer.scan_directory(self.library_dir)
        logger.info(f"Library scan complete, found {count} tracks")
        return count

    def add_track(self, filepath: str) -> bool:
        """Add a track to library."""
        return self.indexer.add_file(filepath)

    def get_all_tracks(self) -> List[MusicTrack]:
        """Get all tracks."""
        return self.indexer.get_all_tracks()

    def search(self, query: str, search_type: str = 'title') -> List[MusicTrack]:
        """
        Search library.
        
        Args:
            query: Search query
            search_type: 'title', 'artist', or 'album'
            
        Returns:
            List of matching tracks
        """
        if search_type == 'artist':
            return self.indexer.search_by_artist(query)
        elif search_type == 'album':
            return self.indexer.search_by_album(query)
        else:
            return self.indexer.search_by_title(query)

    def get_statistics(self) -> dict:
        """Get library statistics."""
        return self.indexer.get_library_stats()

    def get_high_quality_tracks(self) -> List[MusicTrack]:
        """Get high-definition tracks."""
        return self.indexer.get_high_def_tracks()

    def get_lossless_tracks(self) -> List[MusicTrack]:
        """Get lossless tracks."""
        return self.indexer.get_lossless_tracks()

    def export_library(self, filepath: str) -> bool:
        """Export library to JSON."""
        return self.indexer.export_library_json(filepath)
