"""File utility functions."""

import os
import shutil
from typing import List

from .logger import get_logger

logger = get_logger(__name__)


class FileUtils:
    """File utility functions."""

    @staticmethod
    def ensure_dir(directory: str) -> bool:
        """
        Ensure directory exists, create if necessary.
        
        Args:
            directory: Directory path
            
        Returns:
            True if successful
        """
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Error creating directory {directory}: {e}")
            return False

    @staticmethod
    def get_file_size(filepath: str) -> int:
        """Get file size in bytes."""
        try:
            return os.path.getsize(filepath)
        except:
            return 0

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format byte size to human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"

    @staticmethod
    def list_files(directory: str, extension: str = None) -> List[str]:
        """
        List files in directory.
        
        Args:
            directory: Directory path
            extension: File extension filter (e.g., '.mp3')
            
        Returns:
            List of file paths
        """
        files = []
        try:
            for entry in os.listdir(directory):
                full_path = os.path.join(directory, entry)
                if os.path.isfile(full_path):
                    if extension is None or entry.endswith(extension):
                        files.append(full_path)
            return files
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {e}")
            return []

    @staticmethod
    def copy_file(src: str, dst: str) -> bool:
        """Copy a file."""
        try:
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            logger.error(f"Error copying {src} to {dst}: {e}")
            return False

    @staticmethod
    def delete_file(filepath: str) -> bool:
        """Delete a file."""
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            logger.error(f"Error deleting {filepath}: {e}")
            return False