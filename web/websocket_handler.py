"""WebSocket handler for real-time updates."""

from typing import Callable, Dict, Any
import json

from utils.logger import get_logger

logger = get_logger(__name__)


class WebSocketHandler:
    """Handles WebSocket connections for real-time updates."""

    def __init__(self):
        """Initialize WebSocket handler."""
        self.connections: Dict[str, Any] = {}
        self.callbacks: Dict[str, list] = {}
        logger.info("WebSocketHandler initialized")

    def on_connect(self, client_id: str, connection: Any) -> None:
        """Handle client connection."""
        self.connections[client_id] = connection
        logger.info(f"Client connected: {client_id}")
        self.broadcast({
            'event': 'client_connected',
            'client_id': client_id,
        })

    def on_disconnect(self, client_id: str) -> None:
        """Handle client disconnect."""
        if client_id in self.connections:
            del self.connections[client_id]
        logger.info(f"Client disconnected: {client_id}")
        self.broadcast({
            'event': 'client_disconnected',
            'client_id': client_id,
        })

    def send_message(self, client_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to specific client.
        
        Args:
            client_id: Target client ID
            message: Message dictionary
            
        Returns:
            True if successful
        """
        if client_id not in self.connections:
            return False
        
        try:
            connection = self.connections[client_id]
            # In real implementation, would use emit() for WebSocket
            logger.debug(f"Message sent to {client_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    def broadcast(self, message: Dict[str, Any]) -> None:
        """
        Broadcast message to all clients.
        
        Args:
            message: Message dictionary
        """
        for client_id in self.connections:
            self.send_message(client_id, message)

    def register_callback(self, event: str, callback: Callable) -> None:
        """
        Register callback for event.
        
        Args:
            event: Event name
            callback: Callback function
        """
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)

    def trigger_event(self, event: str, data: Any = None) -> None:
        """
        Trigger event and broadcast to clients.
        
        Args:
            event: Event name
            data: Event data
        """
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in callback for {event}: {e}")
        
        self.broadcast({
            'event': event,
            'data': data,
        })

    def send_playback_update(self, status: Dict[str, Any]) -> None:
        """Send playback status update."""
        self.broadcast({
            'event': 'playback_update',
            'status': status,
        })

    def send_library_update(self, data: Dict[str, Any]) -> None:
        """Send library update."""
        self.broadcast({
            'event': 'library_update',
            'data': data,
        })

    def get_connected_clients(self) -> list:
        """Get list of connected clients."""
        return list(self.connections.keys())
