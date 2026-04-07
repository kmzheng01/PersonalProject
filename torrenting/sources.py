"""Torrent source configurations."""

from typing import List, Dict
from dataclasses import dataclass

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TorrentSource:
    """Represents a torrent source."""
    name: str
    url: str
    search_template: str  # URL template with {query} placeholder
    category: str  # e.g., "music", "lossless", "hires"
    enabled: bool = True


class TorrentSources:
    """Manages torrent sources for music discovery."""

    def __init__(self):
        """Initialize sources."""
        self.sources: Dict[str, TorrentSource] = {}
        self._setup_default_sources()

    def _setup_default_sources(self) -> None:
        """Setup default torrent sources."""
        
        default_sources = [
            TorrentSource(
                name="ThePirateBay",
                url="https://thepiratebay.org",
                search_template="https://thepiratebay.org/search.php?q={query}",
                category="general",
                enabled=False,  # Disabled by default due to legal concerns
            ),
            TorrentSource(
                name="RARBG",
                url="https://rarbg.to",
                search_template="https://rarbg.to/?search={query}",
                category="general",
                enabled=False,
            ),
            TorrentSource(
                name="Rutracker",
                url="https://rutracker.org",
                search_template="https://rutracker.org/forum/tracker.php?nm={query}",
                category="music",
                enabled=False,
            ),
            TorrentSource(
                name="Deezer (Legal - FLAC)",
                url="https://deezer.com",
                search_template="https://www.deezer.com/search/{query}",
                category="lossless",
                enabled=True,
            ),
            TorrentSource(
                name="Bandcamp",
                url="https://bandcamp.com",
                search_template="https://bandcamp.com/search?q={query}",
                category="music",
                enabled=True,
            ),
            TorrentSource(
                name="Archive.org (Legal Music)",
                url="https://archive.org",
                search_template="https://archive.org/search.php?query={query}+AND+mediatype:audio",
                category="music",
                enabled=True,
            ),
        ]
        
        for source in default_sources:
            self.sources[source.name] = source

    def add_source(self, name: str, url: str, search_template: str, 
                   category: str) -> bool:
        """Add a new source."""
        if name in self.sources:
            logger.warning(f"Source already exists: {name}")
            return False
        
        source = TorrentSource(
            name=name,
            url=url,
            search_template=search_template,
            category=category,
        )
        
        self.sources[name] = source
        logger.info(f"Added torrent source: {name}")
        return True

    def remove_source(self, name: str) -> bool:
        """Remove a source."""
        if name not in self.sources:
            return False
        
        del self.sources[name]
        logger.info(f"Removed torrent source: {name}")
        return True

    def enable_source(self, name: str) -> bool:
        """Enable a source."""
        if name in self.sources:
            self.sources[name].enabled = True
            return True
        return False

    def disable_source(self, name: str) -> bool:
        """Disable a source."""
        if name in self.sources:
            self.sources[name].enabled = False
            return True
        return False

    def get_enabled_sources(self) -> List[TorrentSource]:
        """Get all enabled sources."""
        return [s for s in self.sources.values() if s.enabled]

    def get_sources_by_category(self, category: str) -> List[TorrentSource]:
        """Get sources by category."""
        return [
            s for s in self.sources.values()
            if s.category == category and s.enabled
        ]

    def search_music(self, query: str, category: str = "music") -> Dict[str, str]:
        """
        Generate search URLs for music query.
        
        Args:
            query: Search query
            category: Source category to search in
            
        Returns:
            Dictionary of source names to search URLs
        """
        sources = self.get_sources_by_category(category)
        results = {}
        
        for source in sources:
            search_url = source.search_template.replace("{query}", query.replace(" ", "+"))
            results[source.name] = search_url
        
        logger.info(f"Generated {len(results)} search URLs for: {query}")
        return results

    def get_source_info(self, name: str) -> dict:
        """Get information about a source."""
        if name not in self.sources:
            return {}
        
        source = self.sources[name]
        return {
            'name': source.name,
            'url': source.url,
            'category': source.category,
            'enabled': source.enabled,
        }

    def list_sources(self) -> List[dict]:
        """List all sources."""
        return [self.get_source_info(name) for name in self.sources]

    def get_recommended_sources(self) -> List[TorrentSource]:
        """Get recommended sources for high-quality music."""
        # Prefer lossless sources
        lossless = self.get_sources_by_category("lossless")
        if lossless:
            return lossless
        
        # Fall back to music sources
        music = self.get_sources_by_category("music")
        return music if music else self.get_enabled_sources()
