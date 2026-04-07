"""Button input handling with debouncing."""

from typing import Callable, Dict, List
from enum import Enum
import threading
import time

from utils.logger import get_logger

logger = get_logger(__name__)


class ButtonEvent(Enum):
    """Button events."""
    PRESSED = "pressed"
    RELEASED = "released"
    LONG_PRESS = "long_press"
    DOUBLE_CLICK = "double_click"


class Button:
    """Represents a single button."""

    def __init__(self, button_id: int, pin: int, name: str = ""):
        self.button_id = button_id
        self.pin = pin
        self.name = name or f"Button_{button_id}"
        self.state = False  # False = released, True = pressed
        self.last_press_time = 0
        self.last_event_time = 0
        self.callbacks: Dict[ButtonEvent, List[Callable]] = {
            event: [] for event in ButtonEvent
        }

    def add_listener(self, event: ButtonEvent, callback: Callable) -> None:
        """Add event listener."""
        self.callbacks[event].append(callback)

    def trigger_event(self, event: ButtonEvent) -> None:
        """Trigger button event."""
        for callback in self.callbacks[event]:
            try:
                callback(self)
            except Exception as e:
                logger.error(f"Error in button callback: {e}")


class ButtonHandler:
    """Handles button inputs with debouncing."""

    def __init__(self, debounce_ms: int = 50, long_press_ms: int = 1000):
        """
        Initialize button handler.
        
        Args:
            debounce_ms: Debounce time in milliseconds
            long_press_ms: Long press detection time in milliseconds
        """
        self.buttons: Dict[int, Button] = {}
        self.debounce_ms = debounce_ms
        self.long_press_ms = long_press_ms
        self.monitoring = False
        self.monitor_thread: threading.Thread = None
        logger.info("ButtonHandler initialized")

    def register_button(self, button_id: int, pin: int, 
                       name: str = "") -> Button:
        """
        Register a button.
        
        Args:
            button_id: Unique button ID
            pin: GPIO pin number
            name: Button name
            
        Returns:
            Button object
        """
        button = Button(button_id, pin, name)
        self.buttons[button_id] = button
        logger.info(f"Registered button: {name} (ID: {button_id}, Pin: {pin})")
        return button

    def on_button_press(self, button_id: int) -> None:
        """
        Handle button press event from hardware.
        
        Args:
            button_id: ID of pressed button
        """
        if button_id not in self.buttons:
            logger.warning(f"Unknown button: {button_id}")
            return
        
        button = self.buttons[button_id]
        current_time = time.time()
        
        # Debounce check
        if current_time - button.last_event_time < (self.debounce_ms / 1000):
            return
        
        button.last_event_time = current_time
        
        if not button.state:
            # Button pressed
            button.state = True
            button.last_press_time = current_time
            button.trigger_event(ButtonEvent.PRESSED)
            logger.debug(f"Button pressed: {button.name}")
        else:
            # Button released
            button.state = False
            press_duration = current_time - button.last_press_time
            
            # Check for long press
            if press_duration >= (self.long_press_ms / 1000):
                button.trigger_event(ButtonEvent.LONG_PRESS)
                logger.debug(f"Long press: {button.name}")
            else:
                button.trigger_event(ButtonEvent.RELEASED)
                logger.debug(f"Button released: {button.name}")

    def on_button_release(self, button_id: int) -> None:
        """Handle button release event."""
        # This is handled in on_button_press with state tracking
        pass

    def add_event_listener(self, button_id: int, event: ButtonEvent, 
                          callback: Callable) -> bool:
        """
        Add event listener to button.
        
        Args:
            button_id: Button ID
            event: Event type
            callback: Callback function
            
        Returns:
            True if successful
        """
        if button_id not in self.buttons:
            return False
        
        self.buttons[button_id].add_listener(event, callback)
        logger.debug(f"Added listener to {self.buttons[button_id].name}: {event.value}")
        return True

    def start_monitoring(self) -> None:
        """Start monitoring buttons."""
        if self.monitoring:
            return
        
        self.monitoring = True
        logger.info("Button monitoring started")

    def stop_monitoring(self) -> None:
        """Stop monitoring buttons."""
        self.monitoring = False
        logger.info("Button monitoring stopped")

    def get_button(self, button_id: int) -> Button:
        """Get button by ID."""
        return self.buttons.get(button_id)

    def get_all_buttons(self) -> List[Button]:
        """Get all registered buttons."""
        return list(self.buttons.values())

    def get_button_state(self, button_id: int) -> bool:
        """Get current button state."""
        if button_id in self.buttons:
            return self.buttons[button_id].state
        return False

    def reset_all(self) -> None:
        """Reset all buttons."""
        for button in self.buttons.values():
            button.state = False
            button.last_press_time = 0
            button.last_event_time = 0
        logger.info("All buttons reset")
