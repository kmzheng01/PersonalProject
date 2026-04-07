"""Network utility functions."""

import socket
from typing import Optional, Tuple

from .logger import get_logger

logger = get_logger(__name__)


class NetworkUtils:
    """Network utility functions."""

    @staticmethod
    def get_local_ip() -> Optional[str]:
        """Get local IP address."""
        try:
            socket_obj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_obj.connect(("8.8.8.8", 80))
            ip = socket_obj.getsockname()[0]
            socket_obj.close()
            return ip
        except Exception as e:
            logger.error(f"Error getting local IP: {e}")
            return None

    @staticmethod
    def is_port_available(port: int, host: str = 'localhost') -> bool:
        """Check if port is available."""
        try:
            socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_obj.bind((host, port))
            socket_obj.close()
            return True
        except:
            return False

    @staticmethod
    def find_available_port(start_port: int = 5000, max_attempts: int = 10) -> int:
        """Find an available port."""
        for port in range(start_port, start_port + max_attempts):
            if NetworkUtils.is_port_available(port):
                logger.info(f"Found available port: {port}")
                return port
        
        logger.error("Could not find available port")
        return start_port

    @staticmethod
    def get_network_interfaces() -> dict:
        """Get information about network interfaces."""
        try:
            interfaces = {}
            import netifaces
            
            for interface in netifaces.interfaces():
                addr_info = netifaces.ifaddresses(interface)
                interfaces[interface] = addr_info
            
            return interfaces
        except ImportError:
            logger.warning("netifaces not available")
            return {}