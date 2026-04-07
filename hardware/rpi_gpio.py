"""Raspberry Pi GPIO support."""

from typing import Callable, Dict, Optional
from enum import Enum

from utils.logger import get_logger

logger = get_logger(__name__)


class GPIOMode(Enum):
    """GPIO pin modes."""
    IN = "IN"  # Input
    OUT = "OUT"  # Output
    PWM = "PWM"  # Pulse Width Modulation


class GPIOState(Enum):
    """GPIO pin states."""
    LOW = 0
    HIGH = 1


class RPiGPIOHandler:
    """Handles GPIO operations on Raspberry Pi."""

    def __init__(self):
        """Initialize GPIO handler."""
        self.pins: Dict[int, Dict] = {}
        self.callbacks: Dict[int, list] = {}
        self.try_import_gpio()
        logger.info("RPiGPIOHandler initialized")

    def try_import_gpio(self) -> bool:
        """Try to import RPi.GPIO library."""
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            self.GPIO.setmode(GPIO.BCM)
            logger.info("RPi.GPIO library loaded")
            return True
        except ImportError:
            logger.warning("RPi.GPIO not available, using simulated mode")
            self.GPIO = None
            return False
        except Exception as e:
            logger.warning(f"Error initializing GPIO: {e}, using simulated mode")
            self.GPIO = None
            return False

    def setup_pin(self, pin: int, mode: GPIOMode, pull_up: bool = False) -> bool:
        """
        Setup a GPIO pin.
        
        Args:
            pin: Pin number
            mode: GPIO mode (IN/OUT/PWM)
            pull_up: Enable pull-up resistor (for inputs)
            
        Returns:
            True if successful
        """
        try:
            if self.GPIO:
                if mode == GPIOMode.IN:
                    pull = self.GPIO.PUD_UP if pull_up else self.GPIO.PUD_OFF
                    self.GPIO.setup(pin, self.GPIO.IN, pull_up_down=pull)
                elif mode == GPIOMode.OUT:
                    self.GPIO.setup(pin, self.GPIO.OUT)
                elif mode == GPIOMode.PWM:
                    self.GPIO.setup(pin, self.GPIO.OUT)
            
            self.pins[pin] = {
                'mode': mode,
                'state': GPIOState.LOW,
                'pull_up': pull_up,
            }
            
            logger.info(f"Pin {pin} setup as {mode.value}")
            return True
        except Exception as e:
            logger.error(f"Error setting up pin {pin}: {e}")
            return False

    def set_pin(self, pin: int, state: GPIOState) -> bool:
        """
        Set GPIO pin state.
        
        Args:
            pin: Pin number
            state: Pin state (HIGH/LOW)
            
        Returns:
            True if successful
        """
        if pin not in self.pins:
            logger.error(f"Pin {pin} not configured")
            return False
        
        try:
            if self.GPIO and self.pins[pin]['mode'] == GPIOMode.OUT:
                self.GPIO.output(pin, state.value)
            
            self.pins[pin]['state'] = state
            logger.debug(f"Pin {pin} set to {state.name}")
            return True
        except Exception as e:
            logger.error(f"Error setting pin {pin}: {e}")
            return False

    def get_pin(self, pin: int) -> Optional[GPIOState]:
        """
        Get GPIO pin state.
        
        Args:
            pin: Pin number
            
        Returns:
            Pin state or None
        """
        if pin not in self.pins:
            return None
        
        try:
            if self.GPIO and self.pins[pin]['mode'] == GPIOMode.IN:
                value = self.GPIO.input(pin)
                state = GPIOState.HIGH if value else GPIOState.LOW
                self.pins[pin]['state'] = state
                return state
            
            return self.pins[pin]['state']
        except Exception as e:
            logger.error(f"Error reading pin {pin}: {e}")
            return None

    def set_pwm(self, pin: int, frequency: float, duty_cycle: float) -> bool:
        """
        Set PWM on a pin.
        
        Args:
            pin: Pin number
            frequency: Frequency in Hz
            duty_cycle: Duty cycle (0-100%)
            
        Returns:
            True if successful
        """
        if pin not in self.pins:
            logger.error(f"Pin {pin} not configured")
            return False
        
        try:
            if self.GPIO and self.pins[pin]['mode'] == GPIOMode.PWM:
                pwm = self.GPIO.PWM(pin, frequency)
                pwm.start(duty_cycle)
                self.pins[pin]['pwm'] = pwm
                logger.info(f"PWM on pin {pin}: {frequency}Hz, {duty_cycle}%")
            return True
        except Exception as e:
            logger.error(f"Error setting PWM on pin {pin}: {e}")
            return False

    def add_event_listener(self, pin: int, callback: Callable, 
                          edge: str = 'both') -> bool:
        """
        Add event listener to pin.
        
        Args:
            pin: Pin number
            callback: Callback function (called with pin number)
            edge: Edge type ('rising', 'falling', 'both')
            
        Returns:
            True if successful
        """
        if pin not in self.pins:
            logger.error(f"Pin {pin} not configured")
            return False
        
        try:
            if pin not in self.callbacks:
                self.callbacks[pin] = []
            
            self.callbacks[pin].append(callback)
            
            if self.GPIO:
                edge_map = {
                    'rising': self.GPIO.RISING,
                    'falling': self.GPIO.FALLING,
                    'both': self.GPIO.BOTH,
                }
                self.GPIO.add_event_detect(
                    pin, edge_map.get(edge, self.GPIO.BOTH),
                    callback=lambda p: self._on_pin_change(pin)
                )
            
            logger.info(f"Event listener added to pin {pin}")
            return True
        except Exception as e:
            logger.error(f"Error adding event listener to pin {pin}: {e}")
            return False

    def _on_pin_change(self, pin: int) -> None:
        """Handle pin state change."""
        if pin in self.callbacks:
            for callback in self.callbacks[pin]:
                try:
                    callback(pin)
                except Exception as e:
                    logger.error(f"Error in callback for pin {pin}: {e}")

    def cleanup(self) -> None:
        """Cleanup GPIO."""
        try:
            if self.GPIO:
                self.GPIO.cleanup()
            logger.info("GPIO cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up GPIO: {e}")

    def __del__(self) -> None:
        """Cleanup on destruction."""
        self.cleanup()
