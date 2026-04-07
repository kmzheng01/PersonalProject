"""Handlers for various audio formats."""

import os
import mimetypes
from typing import Tuple, Optional
import soundfile as sf
import numpy as np

from utils.logger import get_logger

logger = get_logger(__name__)


class FormatHandler:
    """Handles various audio formats and conversions."""

    SUPPORTED_FORMATS = {
        '.flac': 'FLAC (Lossless)',
        '.wav': 'WAV (PCM)',
        '.ogg': 'OGG Vorbis',
        '.mp3': 'MP3',
        '.m4a': 'MP4/AAC',
        '.aiff': 'AIFF',
        '.alac': 'ALAC (Apple Lossless)',
    }

    LOSSLESS_FORMATS = {'.flac', '.wav', '.aiff', '.alac'}
    LOSSY_FORMATS = {'.mp3', '.m4a', '.ogg'}

    @staticmethod
    def is_supported(filepath: str) -> bool:
        """Check if file format is supported."""
        ext = os.path.splitext(filepath)[1].lower()
        return ext in FormatHandler.SUPPORTED_FORMATS

    @staticmethod
    def is_lossless(filepath: str) -> bool:
        """Check if file is lossless format."""
        ext = os.path.splitext(filepath)[1].lower()
        return ext in FormatHandler.LOSSLESS_FORMATS

    @staticmethod
    def get_format_info(filepath: str) -> Optional[dict]:
        """
        Get information about audio file format.
        
        Args:
            filepath: Path to audio file
            
        Returns:
            Dictionary with format info or None
        """
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            return None

        try:
            info = sf.info(filepath)
            ext = os.path.splitext(filepath)[1].lower()
            
            return {
                'format': FormatHandler.SUPPORTED_FORMATS.get(ext, 'Unknown'),
                'channels': info.channels,
                'sample_rate': info.samplerate,
                'duration': info.duration,
                'frames': info.frames,
                'subtype': info.subtype,
                'is_lossless': FormatHandler.is_lossless(filepath),
                'file_size': os.path.getsize(filepath),
            }
        except Exception as e:
            logger.error(f"Error getting format info: {e}")
            return None

    @staticmethod
    def analyze_quality(filepath: str) -> dict:
        """
        Analyze audio quality metrics.
        
        Args:
            filepath: Path to audio file
            
        Returns:
            Dictionary with quality metrics
        """
        try:
            info = FormatHandler.get_format_info(filepath)
            if not info:
                return {}
            
            quality_score = 0
            
            # Sample rate quality (higher is better, 44.1kHz is baseline)
            if info['sample_rate'] >= 96000:
                quality_score += 3
            elif info['sample_rate'] >= 48000:
                quality_score += 2
            elif info['sample_rate'] >= 44100:
                quality_score += 1
            
            # Channel quality
            if info['channels'] >= 2:
                quality_score += 1
            
            # Format quality
            if info['is_lossless']:
                quality_score += 2
            
            return {
                **info,
                'quality_score': quality_score,
                'quality_rating': 'High-def' if quality_score >= 7 else 'High' if quality_score >= 5 else 'Standard',
            }
        except Exception as e:
            logger.error(f"Error analyzing quality: {e}")
            return {}

    @staticmethod
    def read_audio_data(filepath: str, start: float = 0.0, 
                       duration: Optional[float] = None) -> Optional[Tuple[np.ndarray, int]]:
        """
        Read audio data from file.
        
        Args:
            filepath: Path to audio file
            start: Start time in seconds
            duration: Duration to read in seconds (None = all)
            
        Returns:
            Tuple of (audio_data, sample_rate) or None
        """
        try:
            data, sr = sf.read(filepath, dtype='float32')
            
            if len(data.shape) == 1:
                data = np.stack([data, data], axis=1)
            
            # Handle subsection reading
            if start > 0 or duration is not None:
                start_frame = int(start * sr)
                if duration is not None:
                    end_frame = int((start + duration) * sr)
                    data = data[start_frame:end_frame]
                else:
                    data = data[start_frame:]
            
            return data, sr
        except Exception as e:
            logger.error(f"Error reading audio data: {e}")
            return None

    @staticmethod
    def get_all_supported_formats() -> dict:
        """Get all supported formats."""
        return FormatHandler.SUPPORTED_FORMATS.copy()

    @staticmethod
    def validate_audio_file(filepath: str) -> Tuple[bool, str]:
        """
        Validate that file is a valid audio file.
        
        Args:
            filepath: Path to check
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not os.path.exists(filepath):
            return False, "File does not exist"
        
        if not os.path.isfile(filepath):
            return False, "Path is not a file"
        
        if not FormatHandler.is_supported(filepath):
            ext = os.path.splitext(filepath)[1]
            return False, f"Format {ext} is not supported"
        
        try:
            info = sf.info(filepath)
            if info.channels == 0 or info.samplerate == 0:
                return False, "Invalid audio file (no channels or sample rate)"
            return True, "Valid audio file"
        except Exception as e:
            return False, f"Error validating file: {e}"
