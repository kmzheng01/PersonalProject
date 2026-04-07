"""Torrent download manager for high-definition music."""

import os
import threading
from typing import List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import time

from utils.logger import get_logger

logger = get_logger(__name__)


class TorrentStatus(Enum):
    """Torrent download status."""
    WAITING = "waiting"
    DOWNLOADING = "downloading"
    SEEDING = "seeding"
    COMPLETED = "completed"
    ERROR = "error"
    PAUSED = "paused"


@dataclass
class Torrent:
    """Represents a torrent download."""
    name: str
    magnet_link: Optional[str] = None
    torrent_path: Optional[str] = None
    status: TorrentStatus = TorrentStatus.WAITING
    progress: float = 0.0  # 0-100%
    size_bytes: int = 0
    downloaded_bytes: int = 0
    upload_speed: float = 0.0  # bytes/sec
    download_speed: float = 0.0  # bytes/sec
    eta_seconds: Optional[int] = None


class TorrentManager:
    """Manages torrent downloads."""

    def __init__(self, download_dir: str = "./downloads"):
        """
        Initialize torrent manager.
        
        Args:
            download_dir: Directory for torrent downloads
        """
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        
        self.torrents: dict[str, Torrent] = {}
        self.active_downloads: List[str] = []
        self.max_concurrent_downloads = 3
        self.callbacks = {
            'on_progress': [],
            'on_complete': [],
            'on_error': [],
        }
        
        logger.info(f"TorrentManager initialized, download dir: {download_dir}")

    def add_torrent_magnet(self, name: str, magnet_link: str) -> str:
        """
        Add a torrent via magnet link.
        
        Args:
            name: Torrent name
            magnet_link: Magnet link URL
            
        Returns:
            Torrent ID
        """
        torrent_id = f"torrent_{len(self.torrents)}_{int(time.time())}"
        
        torrent = Torrent(
            name=name,
            magnet_link=magnet_link,
            status=TorrentStatus.WAITING,
        )
        
        self.torrents[torrent_id] = torrent
        logger.info(f"Added torrent: {name} (ID: {torrent_id})")
        
        self._try_start_download(torrent_id)
        return torrent_id

    def add_torrent_file(self, name: str, torrent_path: str) -> str:
        """
        Add a torrent from file.
        
        Args:
            name: Torrent name
            torrent_path: Path to .torrent file
            
        Returns:
            Torrent ID
        """
        if not os.path.exists(torrent_path):
            logger.error(f"Torrent file not found: {torrent_path}")
            return ""
        
        torrent_id = f"torrent_{len(self.torrents)}_{int(time.time())}"
        
        torrent = Torrent(
            name=name,
            torrent_path=torrent_path,
            status=TorrentStatus.WAITING,
        )
        
        self.torrents[torrent_id] = torrent
        logger.info(f"Added torrent file: {name} (ID: {torrent_id})")
        
        self._try_start_download(torrent_id)
        return torrent_id

    def _try_start_download(self, torrent_id: str) -> None:
        """Try to start a torrent download if slots are available."""
        if len(self.active_downloads) < self.max_concurrent_downloads:
            self.start_download(torrent_id)

    def start_download(self, torrent_id: str) -> bool:
        """
        Start downloading a torrent.
        
        Args:
            torrent_id: Torrent ID
            
        Returns:
            True if started
        """
        if torrent_id not in self.torrents:
            logger.error(f"Torrent not found: {torrent_id}")
            return False
        
        torrent = self.torrents[torrent_id]
        
        if torrent.status == TorrentStatus.DOWNLOADING:
            logger.warning(f"Torrent already downloading: {torrent_id}")
            return False
        
        self.active_downloads.append(torrent_id)
        torrent.status = TorrentStatus.DOWNLOADING
        
        # Simulate download in background thread
        thread = threading.Thread(target=self._simulate_download, args=(torrent_id,))
        thread.daemon = True
        thread.start()
        
        logger.info(f"Started download: {torrent_id}")
        return True

    def _simulate_download(self, torrent_id: str) -> None:
        """Simulate downloading a torrent."""
        torrent = self.torrents[torrent_id]
        
        # Simulate download progress
        torrent.size_bytes = 500 * 1024 * 1024  # 500 MB
        
        try:
            for i in range(101):
                if torrent_id not in self.active_downloads:
                    break
                
                torrent.progress = float(i)
                torrent.downloaded_bytes = int(torrent.size_bytes * i / 100)
                torrent.download_speed = 1 * 1024 * 1024  # 1 MB/s
                
                if i > 0:
                    remaining_bytes = torrent.size_bytes - torrent.downloaded_bytes
                    torrent.eta_seconds = int(remaining_bytes / max(torrent.download_speed, 1))
                
                for cb in self.callbacks['on_progress']:
                    cb(torrent_id, torrent)
                
                time.sleep(0.5)  # Simulate network delay
            
            # Complete
            torrent.status = TorrentStatus.COMPLETED
            torrent.progress = 100.0
            torrent.downloaded_bytes = torrent.size_bytes
            torrent.eta_seconds = None
            
            if torrent_id in self.active_downloads:
                self.active_downloads.remove(torrent_id)
            
            for cb in self.callbacks['on_complete']:
                cb(torrent_id, torrent)
            
            logger.info(f"Download completed: {torrent.name}")
            
        except Exception as e:
            logger.error(f"Error downloading {torrent_id}: {e}")
            torrent.status = TorrentStatus.ERROR
            
            for cb in self.callbacks['on_error']:
                cb(torrent_id, str(e))
            
            if torrent_id in self.active_downloads:
                self.active_downloads.remove(torrent_id)
        
        # Try to start next download
        for tid in self.torrents:
            if self.torrents[tid].status == TorrentStatus.WAITING:
                self._try_start_download(tid)
                break

    def pause_download(self, torrent_id: str) -> bool:
        """Pause a download."""
        if torrent_id in self.torrents:
            self.torrents[torrent_id].status = TorrentStatus.PAUSED
            return True
        return False

    def resume_download(self, torrent_id: str) -> bool:
        """Resume a download."""
        if torrent_id in self.torrents:
            self.torrents[torrent_id].status = TorrentStatus.DOWNLOADING
            return self.start_download(torrent_id)
        return False

    def cancel_download(self, torrent_id: str) -> bool:
        """Cancel a download."""
        if torrent_id in self.torrents:
            if torrent_id in self.active_downloads:
                self.active_downloads.remove(torrent_id)
            del self.torrents[torrent_id]
            logger.info(f"Cancelled download: {torrent_id}")
            return True
        return False

    def get_torrent_status(self, torrent_id: str) -> Optional[dict]:
        """Get torrent status."""
        if torrent_id not in self.torrents:
            return None
        
        torrent = self.torrents[torrent_id]
        return {
            'id': torrent_id,
            'name': torrent.name,
            'status': torrent.status.value,
            'progress': torrent.progress,
            'size_mb': torrent.size_bytes / (1024 * 1024),
            'downloaded_mb': torrent.downloaded_bytes / (1024 * 1024),
            'download_speed_mbps': torrent.download_speed / (1024 * 1024),
            'eta_seconds': torrent.eta_seconds,
        }

    def get_all_torrents(self) -> List[dict]:
        """Get status of all torrents."""
        return [self.get_torrent_status(tid) for tid in self.torrents]

    def register_callback(self, event: str, callback: Callable) -> None:
        """Register callback for torrent events."""
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def get_download_dir(self) -> str:
        """Get download directory."""
        return self.download_dir
