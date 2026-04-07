"""Database manager for local storage."""

import sqlite3
import json
from typing import Dict, List, Any, Optional
import os

from utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Manages SQLite database for library and playback history."""

    def __init__(self, db_path: str = "./audiostream.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.init_database()

    def init_database(self) -> None:
        """Initialize database and create tables."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            
            # Create tables if they don't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tracks (
                    id INTEGER PRIMARY KEY,
                    filepath TEXT UNIQUE,
                    title TEXT,
                    artist TEXT,
                    album TEXT,
                    genre TEXT,
                    duration INTEGER,
                    year INTEGER,
                    format TEXT,
                    lossless BOOLEAN,
                    sample_rate INTEGER,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlist_tracks (
                    playlist_id INTEGER,
                    track_id INTEGER,
                    position INTEGER,
                    FOREIGN KEY (playlist_id) REFERENCES playlists(id),
                    FOREIGN KEY (track_id) REFERENCES tracks(id)
                )
            """)
            
            self.connection.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def add_track(self, track_data: Dict[str, Any]) -> bool:
        """
        Add a track to the database.
        
        Args:
            track_data: Dictionary with track information
            
        Returns:
            True if successful
        """
        if not self.connection:
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO tracks (filepath, title, artist, album, genre, duration, 
                                   year, format, lossless, sample_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                track_data.get('filepath'),
                track_data.get('title'),
                track_data.get('artist'),
                track_data.get('album'),
                track_data.get('genre'),
                track_data.get('duration'),
                track_data.get('year'),
                track_data.get('format'),
                track_data.get('lossless', False),
                track_data.get('sample_rate')
            ))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding track: {e}")
            return False

    def get_all_tracks(self) -> List[Dict[str, Any]]:
        """Get all tracks from database."""
        if not self.connection:
            return []
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM tracks")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting tracks: {e}")
            return []

    def __del__(self) -> None:
        """Cleanup when object is destroyed."""
        self.close()