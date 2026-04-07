"""Real-time DSP effects for audio processing."""

import numpy as np
from typing import Optional
from enum import Enum

from utils.logger import get_logger

logger = get_logger(__name__)


class EqualizerPreset(Enum):
    """EQ preset options."""
    FLAT = "flat"
    BASS_BOOST = "bass_boost"
    TREBLE_BOOST = "treble_boost"
    WARM = "warm"
    BRIGHT = "bright"


class DSPEffects:
    """Real-time DSP effects processing."""

    def __init__(self, sample_rate: int = 44100):
        """Initialize DSP effects."""
        self.sample_rate = sample_rate
        self.enabled = True
        
        # Effect parameters
        self.eq_enabled = False
        self.eq_preset = EqualizerPreset.FLAT
        self.eq_gains = {
            '60Hz': 0.0,
            '250Hz': 0.0,
            '1kHz': 0.0,
            '4kHz': 0.0,
            '16kHz': 0.0,
        }
        
        self.normalizer_enabled = False
        self.normalizer_threshold = -20.0  # dB
        self.normalizer_attack = 0.005  # seconds
        self.normalizer_release = 0.1  # seconds
        
        logger.info(f"DSPEffects initialized @ {sample_rate}Hz")

    def apply_gain(self, audio: np.ndarray, gain_db: float) -> np.ndarray:
        """
        Apply linear gain to audio.
        
        Args:
            audio: Audio data
            gain_db: Gain in dB
            
        Returns:
            Processed audio
        """
        if gain_db == 0.0:
            return audio
        
        gain_linear = 10 ** (gain_db / 20.0)
        return audio * gain_linear

    def apply_equalizer(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply parametric equalizer.
        
        Args:
            audio: Audio data
            
        Returns:
            Equalized audio
        """
        if not self.eq_enabled:
            return audio
        
        processed = audio.copy()
        
        # Simple gain-based EQ (more sophisticated implementations would use filters)
        for band, gain in self.eq_gains.items():
            if gain != 0.0:
                processed = self.apply_gain(processed, gain * 0.1)  # Scale down gain
        
        return processed

    def apply_normalizer(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply audio normalizer.
        
        Args:
            audio: Audio data
            
        Returns:
            Normalized audio
        """
        if not self.normalizer_enabled:
            return audio
        
        # Calculate RMS level
        rms = np.sqrt(np.mean(audio ** 2))
        rms_db = 20 * np.log10(max(rms, 1e-10))
        
        # Apply gain reduction if above threshold
        if rms_db > self.normalizer_threshold:
            gain_reduction = self.normalizer_threshold - rms_db
            return self.apply_gain(audio, gain_reduction)
        
        return audio

    def apply_soft_clipping(self, audio: np.ndarray, threshold: float = 0.9) -> np.ndarray:
        """
        Apply soft clipping to prevent distortion.
        
        Args:
            audio: Audio data
            threshold: Clipping threshold (0-1)
            
        Returns:
            Clipped audio
        """
        # Tanh-based soft clipping
        return np.tanh(audio / threshold) * threshold

    def set_equalizer_preset(self, preset: EqualizerPreset) -> None:
        """
        Set EQ to a preset.
        
        Args:
            preset: Preset to use
        """
        presets = {
            EqualizerPreset.FLAT: {'60Hz': 0, '250Hz': 0, '1kHz': 0, '4kHz': 0, '16kHz': 0},
            EqualizerPreset.BASS_BOOST: {'60Hz': 8, '250Hz': 4, '1kHz': 0, '4kHz': -2, '16kHz': -4},
            EqualizerPreset.TREBLE_BOOST: {'60Hz': -4, '250Hz': -2, '1kHz': 0, '4kHz': 4, '16kHz': 8},
            EqualizerPreset.WARM: {'60Hz': 4, '250Hz': 2, '1kHz': 0, '4kHz': 0, '16kHz': -2},
            EqualizerPreset.BRIGHT: {'60Hz': -2, '250Hz': 0, '1kHz': 2, '4kHz': 4, '16kHz': 6},
        }
        
        self.eq_preset = preset
        self.eq_gains = presets.get(preset, presets[EqualizerPreset.FLAT])
        logger.info(f"EQ preset set to: {preset.value}")

    def enable_equalizer(self, enabled: bool) -> None:
        """Enable/disable equalizer."""
        self.eq_enabled = enabled
        logger.debug(f"Equalizer {'enabled' if enabled else 'disabled'}")

    def enable_normalizer(self, enabled: bool) -> None:
        """Enable/disable normalizer."""
        self.normalizer_enabled = enabled
        logger.debug(f"Normalizer {'enabled' if enabled else 'disabled'}")

    def process_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        Apply all enabled effects.
        
        Args:
            audio: Audio data
            
        Returns:
            Processed audio
        """
        if not self.enabled:
            return audio
        
        processed = audio.copy()
        
        # Apply effects in order
        processed = self.apply_equalizer(processed)
        processed = self.apply_normalizer(processed)
        processed = self.apply_soft_clipping(processed)
        
        return processed

    def get_status(self) -> dict:
        """Get effects status."""
        return {
            'enabled': self.enabled,
            'equalizer': {
                'enabled': self.eq_enabled,
                'preset': self.eq_preset.value,
                'gains': self.eq_gains,
            },
            'normalizer': {
                'enabled': self.normalizer_enabled,
                'threshold': self.normalizer_threshold,
            },
        }
