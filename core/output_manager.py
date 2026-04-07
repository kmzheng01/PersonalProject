"""Audio output detection and selection."""

try:
    import sounddevice as sd
    HAS_SOUNDDEVICE = True
except (ImportError, OSError):
    sd = None
    HAS_SOUNDDEVICE = False

from typing import List, Optional, Dict
import json

from utils.logger import get_logger

logger = get_logger(__name__)


class AudioOutput:
    """Represents an audio output device."""

    def __init__(self, device_id: int, name: str, channels: int, sample_rate: int):
        """Initialize audio output."""
        self.device_id = device_id
        self.name = name
        self.channels = channels
        self.sample_rate = sample_rate

    def __repr__(self) -> str:
        return f"AudioOutput({self.device_id}: {self.name}, {self.channels}ch @ {self.sample_rate}Hz)"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'device_id': self.device_id,
            'name': self.name,
            'channels': self.channels,
            'sample_rate': self.sample_rate,
        }


class OutputManager:
    """Manages audio output detection and selection."""

    def __init__(self):
        """Initialize output manager."""
        self.outputs: List[AudioOutput] = []
        self.current_output: Optional[AudioOutput] = None
        self.refresh_outputs()
        logger.info("OutputManager initialized")

    def refresh_outputs(self) -> None:
        """Detect all available audio outputs."""
        self.outputs = []
        
        if not HAS_SOUNDDEVICE:
            logger.warning("sounddevice not available, no outputs detected")
            return
        
        try:
            devices = sd.query_devices()
            for i, device in enumerate(devices):
                if device.get('max_output_channels', 0) > 0:
                    output = AudioOutput(
                        device_id=i,
                        name=device['name'],
                        channels=device['max_output_channels'],
                        sample_rate=int(device.get('default_samplerate', 44100))
                    )
                    self.outputs.append(output)
            
            logger.info(f"Found {len(self.outputs)} audio outputs")
            for output in self.outputs:
                logger.debug(f"  {output}")
        except Exception as e:
            logger.error(f"Error refreshing audio outputs: {e}")

    def list_outputs(self) -> List[AudioOutput]:
        """Get list of all available outputs."""
        return self.outputs

    def get_default_output(self) -> Optional[AudioOutput]:
        """Get the default audio output."""
        if not HAS_SOUNDDEVICE or not self.outputs:
            return None
        
        try:
            default_device = sd.default.device[1]  # Index 1 is output
            if default_device >= 0 and default_device < len(self.outputs):
                return self.outputs[default_device]
        except Exception as e:
            logger.error(f"Error getting default output: {e}")
        
        return self.outputs[0] if self.outputs else None

    def select_output(self, device_id: int) -> bool:
        """
        Select an audio output device.
        
        Args:
            device_id: Device ID to select
            
        Returns:
            True if successful
        """
        if not HAS_SOUNDDEVICE:
            logger.warning("sounddevice not available, cannot select output")
            return False
        
        for output in self.outputs:
            if output.device_id == device_id:
                self.current_output = output
                try:
                    sd.default.device = (None, device_id)
                    logger.info(f"Selected output: {output.name}")
                    return True
                except Exception as e:
                    logger.error(f"Error selecting output: {e}")
                    return False
        
        logger.error(f"Device {device_id} not found")
        return False

    def select_output_by_name(self, name: str) -> bool:
        """
        Select output by device name.
        
        Args:
            name: Device name (partial match supported)
            
        Returns:
            True if successful
        """
        for output in self.outputs:
            if name.lower() in output.name.lower():
                return self.select_output(output.device_id)
        
        logger.error(f"Output '{name}' not found")
        return False

    def get_current_output(self) -> Optional[AudioOutput]:
        """Get currently selected output."""
        if self.current_output is None:
            self.current_output = self.get_default_output()
        return self.current_output

    def auto_detect_best_output(self) -> Optional[AudioOutput]:
        """
        Auto-detect the best audio output.
        
        Prefers: HDMI/Digital > Analog Stereo > Others
        
        Returns:
            Best detected output or None
        """
        if not self.outputs:
            return None

        # Preference order
        priorities = [
            ('hdmi', 2), ('digital', 2), ('optical', 2),
            ('analog', 1), ('stereo', 1),
            ('default', 0), ('speakers', 0),
        ]

        best_output = self.outputs[0]
        best_score = -1

        for output in self.outputs:
            score = -1
            name_lower = output.name.lower()
            
            for keyword, priority in priorities:
                if keyword in name_lower:
                    score = priority
                    break
            
            if score > best_score:
                best_score = score
                best_output = output

        logger.info(f"Auto-detected best output: {best_output.name}")
        self.current_output = best_output
        return best_output

    def get_output_info_json(self) -> str:
        """Get output information as JSON."""
        outputs_dict = [output.to_dict() for output in self.outputs]
        current = self.get_current_output()
        
        return json.dumps({
            'outputs': outputs_dict,
            'current': current.to_dict() if current else None,
            'count': len(self.outputs),
        }, indent=2)

    def test_output(self, device_id: int, duration: float = 1.0) -> bool:
        """
        Test an output device with a test tone.
        
        Args:
            device_id: Device to test
            duration: Tone duration in seconds
            
        Returns:
            True if successful
        """
        import numpy as np
        try:
            # Generate test tone (440 Hz sine wave)
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration))
            tone = 0.3 * np.sin(2 * np.pi * 440 * t)
            
            # Play on specified device
            sd.play(tone, samplerate=sample_rate, device=device_id, blocking=True)
            logger.info(f"Test tone played on device {device_id}")
            return True
        except Exception as e:
            logger.error(f"Error testing output: {e}")
            return False
