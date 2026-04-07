"""ESP32/ESP8266 communication interface."""

import socket
import json
from typing import Optional, Dict, Any
import threading
import time

from utils.logger import get_logger

logger = get_logger(__name__)


class ESPInterface:
    """Communicates with ESP32/ESP8266 devices."""

    def __init__(self, esp_ip: str, esp_port: int = 5000):
        """
        Initialize ESP interface.
        
        Args:
            esp_ip: IP address of ESP device
            esp_port: Port number on ESP device
        """
        self.esp_ip = esp_ip
        self.esp_port = esp_port
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.callbacks: Dict[str, list] = {}
        logger.info(f"ESPInterface initialized for {esp_ip}:{esp_port}")

    def connect(self, timeout: float = 5.0) -> bool:
        """
        Connect to ESP device.
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            True if successful
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(timeout)
            self.socket.connect((self.esp_ip, self.esp_port))
            self.connected = True
            logger.info(f"Connected to ESP at {self.esp_ip}:{self.esp_port}")
            
            # Start receiver thread
            recv_thread = threading.Thread(target=self._receive_loop)
            recv_thread.daemon = True
            recv_thread.start()
            
            return True
        except Exception as e:
            logger.error(f"Error connecting to ESP: {e}")
            self.connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from ESP device."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        logger.info("Disconnected from ESP")

    def send_command(self, command: str, params: Dict[str, Any] = None) -> bool:
        """
        Send command to ESP device.
        
        Args:
            command: Command name
            params: Command parameters
            
        Returns:
            True if successful
        """
        if not self.connected:
            logger.error("Not connected to ESP")
            return False
        
        try:
            message = {
                'cmd': command,
                'params': params or {},
            }
            
            json_msg = json.dumps(message) + '\n'
            self.socket.send(json_msg.encode('utf-8'))
            
            logger.debug(f"Sent command to ESP: {command}")
            return True
        except Exception as e:
            logger.error(f"Error sending command to ESP: {e}")
            self.connected = False
            return False

    def _receive_loop(self) -> None:
        """Receive messages from ESP device."""
        buffer = ""
        
        while self.connected:
            try:
                if self.socket:
                    data = self.socket.recv(1024).decode('utf-8')
                    if not data:
                        self.connected = False
                        break
                    
                    buffer += data
                    
                    # Process complete messages
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.strip():
                            self._process_message(line.strip())
            except socket.timeout:
                continue
            except Exception as e:
                logger.error(f"Error receiving from ESP: {e}")
                self.connected = False
                break

    def _process_message(self, message: str) -> None:
        """Process message from ESP."""
        try:
            data = json.loads(message)
            event = data.get('event')
            payload = data.get('payload', {})
            
            if event in self.callbacks:
                for callback in self.callbacks[event]:
                    try:
                        callback(payload)
                    except Exception as e:
                        logger.error(f"Error in callback for event {event}: {e}")
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON from ESP: {message}")
        except Exception as e:
            logger.error(f"Error processing message from ESP: {e}")

    def register_callback(self, event: str, callback) -> None:
        """
        Register callback for events from ESP.
        
        Args:
            event: Event name
            callback: Callback function
        """
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)

    def set_button_state(self, button_id: int, state: int) -> bool:
        """
        Set button state (inform ESP about button press).
        
        Args:
            button_id: Button ID
            state: Button state (0 or 1)
            
        Returns:
            True if successful
        """
        return self.send_command('button_press', {
            'button_id': button_id,
            'state': state,
        })

    def set_display_text(self, line: int, text: str) -> bool:
        """
        Set display text on ESP device.
        
        Args:
            line: Display line (0-based)
            text: Text to display
            
        Returns:
            True if successful
        """
        return self.send_command('display_text', {
            'line': line,
            'text': text,
        })

    def set_led(self, led_id: int, color: str, brightness: int = 255) -> bool:
        """
        Control LED on ESP device.
        
        Args:
            led_id: LED ID
            color: Color name (e.g., 'red', 'green', 'blue')
            brightness: Brightness (0-255)
            
        Returns:
            True if successful
        """
        return self.send_command('set_led', {
            'led_id': led_id,
            'color': color,
            'brightness': brightness,
        })

    def get_device_info(self) -> Optional[dict]:
        """Get device information from ESP."""
        # This would typically use a synchronous request-response pattern
        logger.debug("Device info requested from ESP")
        return {'device': 'ESP32', 'version': '1.0.0'}

    def __del__(self) -> None:
        """Cleanup on destruction."""
        self.disconnect()
