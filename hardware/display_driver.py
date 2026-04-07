"""Display driver for LCD/OLED displays."""

from typing import Optional, List
from enum import Enum
import time

from utils.logger import get_logger

logger = get_logger(__name__)


class DisplayType(Enum):
    """Display types."""
    LCD_16X2 = "lcd_16x2"
    LCD_20X4 = "lcd_20x4"
    OLED_128X64 = "oled_128x64"
    OLED_128X32 = "oled_128x32"


class DisplayDriver:
    """Driver for LCD/OLED displays."""

    def __init__(self, display_type: DisplayType = DisplayType.LCD_16X2,
                 i2c_address: int = 0x27):
        """
        Initialize display driver.
        
        Args:
            display_type: Type of display
            i2c_address: I2C address of display
        """
        self.display_type = display_type
        self.i2c_address = i2c_address
        self.module = None
        self.display = None
        self.width = 16
        self.height = 2
        self.buffer: List[str] = []
        
        # Set dimensions based on type
        if display_type == DisplayType.LCD_16X2:
            self.width, self.height = 16, 2
        elif display_type == DisplayType.LCD_20X4:
            self.width, self.height = 20, 4
        elif display_type == DisplayType.OLED_128X64:
            self.width, self.height = 128, 64
        elif display_type == DisplayType.OLED_128X32:
            self.width, self.height = 128, 32
        
        # Initialize buffer
        self.buffer = [''] * self.height
        
        self.try_init_display()
        logger.info(f"DisplayDriver initialized: {display_type.value}")

    def try_init_display(self) -> bool:
        """Try to initialize display hardware."""
        try:
            # Try OLED
            if self.display_type in (DisplayType.OLED_128X64, DisplayType.OLED_128X32):
                try:
                    from adafruit_ssd1306 import SSD1306_I2C
                    import busio
                    import board
                    i2c = busio.I2C(board.SCL, board.SDA)
                    self.display = SSD1306_I2C(self.width, self.height, i2c)
                    logger.info("OLED display initialized")
                    return True
                except ImportError:
                    logger.warning("Adafruit SSD1306 not available")
            
            # Try LCD
            if self.display_type in (DisplayType.LCD_16X2, DisplayType.LCD_20X4):
                try:
                    from RPi import GPIO
                    import Adafruit_CharLCD as LCD
                    
                    self.display = LCD.Adafruit_CharLCDPlate()
                    logger.info("LCD display initialized")
                    return True
                except ImportError:
                    logger.warning("Adafruit Character LCD not available")
            
            logger.warning("Display hardware not available, using simulated mode")
            return False
        except Exception as e:
            logger.warning(f"Error initializing display: {e}, using simulated mode")
            return False

    def write_line(self, line: int, text: str, clear: bool = True) -> bool:
        """
        Write text to a display line.
        
        Args:
            line: Line number (0-based)
            text: Text to display
            clear: Clear line before writing
            
        Returns:
            True if successful
        """
        if line < 0 or line >= self.height:
            logger.error(f"Invalid line number: {line}")
            return False
        
        # Truncate text to fit display width
        text = str(text)[:self.width]
        
        # Pad with spaces if needed
        if clear or len(text) < self.width:
            text = text.ljust(self.width)
        
        self.buffer[line] = text
        
        try:
            if self.display:
                self.display.setCursor(0, line)
                self.display.message(text)
            
            logger.debug(f"Line {line}: {text.strip()}")
            return True
        except Exception as e:
            logger.error(f"Error writing to display: {e}")
            return False

    def clear(self) -> bool:
        """Clear display."""
        try:
            self.buffer = [''] * self.height
            
            if self.display:
                self.display.clear()
            
            logger.debug("Display cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing display: {e}")
            return False

    def show_message(self, message: str, duration: float = 0) -> bool:
        """
        Show a message on display.
        
        Args:
            message: Message to display (auto-wraps to fit)
            duration: Display duration in seconds (0 = indefinite)
            
        Returns:
            True if successful
        """
        self.clear()
        
        lines = self._wrap_text(message)
        
        for i, line in enumerate(lines):
            if i >= self.height:
                break
            self.write_line(i, line)
        
        if duration > 0:
            time.sleep(duration)
        
        return True

    def _wrap_text(self, text: str) -> List[str]:
        """Wrap text to fit display width."""
        lines = []
        words = text.split()
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= self.width:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines

    def show_scrolling_message(self, message: str, speed: float = 0.3) -> bool:
        """
        Show scrolling message on display.
        
        Args:
            message: Message to scroll
            speed: Scroll speed (seconds per character)
            
        Returns:
            True if successful
        """
        for i in range(len(message) - self.width + 1):
            self.clear()
            self.write_line(0, message[i:i + self.width])
            time.sleep(speed)
        
        return True

    def show_progress_bar(self, value: float, total: float = 100.0) -> bool:
        """
        Show progress bar on display.
        
        Args:
            value: Current progress value
            total: Maximum progress value
            
        Returns:
            True if successful
        """
        percentage = (value / total) * 100
        bar_width = self.width - 5  # Leave room for percentage
        filled = int((percentage / 100) * bar_width)
        bar = '[' + '#' * filled + ' ' * (bar_width - filled) + ']'
        
        self.write_line(0, bar)
        self.write_line(1, f"{percentage:6.1f}%")
        
        return True

    def get_display_info(self) -> dict:
        """Get display information."""
        return {
            'type': self.display_type.value,
            'width': self.width,
            'height': self.height,
            'i2c_address': f"0x{self.i2c_address:02x}",
            'connected': self.display is not None,
        }

    def __del__(self) -> None:
        """Cleanup on destruction."""
        if self.display:
            try:
                self.clear()
            except:
                pass
