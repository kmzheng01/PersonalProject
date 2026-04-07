"""API routes for AudioStream web interface."""

from flask import Blueprint, request, jsonify, send_file 
import os
import json

from utils.logger import get_logger
from .upload_handler import FileUploadHandler

logger = get_logger(__name__)


def register_routes(app):
    """Register all API routes."""
    
    @app.route('/')
    def index():
        """Serve main page."""
        return send_file(os.path.join(app.static_folder, 'index.html'))
    
    # Player routes
    @app.route('/api/player/load', methods=['POST'])
    def player_load():
        """Load audio file."""
        data = request.json or {}
        filepath = data.get('filepath')
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 400
        
        logger.info(f"Loading file: {filepath}")
        return jsonify({'status': 'loaded', 'file': filepath})
    
    @app.route('/api/player/play', methods=['POST'])
    def player_play():
        """Start playback."""
        logger.info("Play requested")
        return jsonify({'status': 'playing'})
    
    @app.route('/api/player/pause', methods=['POST'])
    def player_pause():
        """Pause playback."""
        logger.info("Pause requested")
        return jsonify({'status': 'paused'})
    
    @app.route('/api/player/stop', methods=['POST'])
    def player_stop():
        """Stop playback."""
        logger.info("Stop requested")
        return jsonify({'status': 'stopped'})
    
    @app.route('/api/player/next', methods=['POST'])
    def player_next():
        """Next track."""
        logger.info("Next track requested")
        return jsonify({'status': 'next'})
    
    @app.route('/api/player/previous', methods=['POST'])
    def player_previous():
        """Previous track."""
        logger.info("Previous track requested")
        return jsonify({'status': 'previous'})
    
    @app.route('/api/player/seek', methods=['POST'])
    def player_seek():
        """Seek to position."""
        data = request.json or {}
        position = data.get('position', 0)
        logger.info(f"Seek to {position}s requested")
        return jsonify({'status': 'seeked', 'position': position})
    
    @app.route('/api/player/volume', methods=['POST'])
    def player_volume():
        """Set volume."""
        data = request.json or {}
        volume = data.get('volume', 0.8)
        logger.info(f"Volume set to {volume}")
        return jsonify({'status': 'volume_set', 'volume': volume})
    
    @app.route('/api/player/status', methods=['GET'])
    def player_status():
        """Get playback status."""
        return jsonify({
            'state': 'playing',
            'file': 'current_song.flac',
            'position': 25.5,
            'duration': 245.3,
            'volume': 0.8,
        })
    
    # Library routes
    @app.route('/api/library/scan', methods=['POST'])
    def library_scan():
        """Scan directory for music files."""
        data = request.json or {}
        directory = data.get('directory', './music')
        
        logger.info(f"Scanning directory: {directory}")
        # In real implementation, would call library manager
        return jsonify({'status': 'scanning', 'directory': directory})
    
    @app.route('/api/library/list', methods=['GET'])
    def library_list():
        """List library tracks."""
        offset = request.args.get('offset', 0, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        return jsonify({
            'tracks': [],
            'offset': offset,
            'limit': limit,
            'total': 0,
        })
    
    @app.route('/api/library/search', methods=['GET'])
    def library_search():
        """Search library."""
        query = request.args.get('q', '')
        search_type = request.args.get('type', 'title')
        
        logger.info(f"Search: {query} (type: {search_type})")
        return jsonify({'results': []})
    
    @app.route('/api/library/stats', methods=['GET'])
    def library_stats():
        """Get library statistics."""
        return jsonify({
            'total_tracks': 0,
            'total_duration_hours': 0,
            'lossless_tracks': 0,
            'hires_tracks': 0,
            'unique_artists': 0,
            'unique_albums': 0,
        })
    
    # Upload routes
    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        """Upload music file."""
        uploader = FileUploadHandler(app.config['UPLOAD_FOLDER'])
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        result = uploader.handle_upload(file)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    @app.route('/api/upload/status/<upload_id>', methods=['GET'])
    def upload_status(upload_id):
        """Get upload status."""
        return jsonify({'status': 'completed', 'progress': 100})
    
    # Output routes
    @app.route('/api/outputs', methods=['GET'])
    def get_outputs():
        """Get available audio outputs."""
        return jsonify({
            'outputs': [
                {'id': 0, 'name': 'HDMI Output', 'channels': 2},
                {'id': 1, 'name': 'Analog Output', 'channels': 2},
            ],
            'current': 0,
        })
    
    @app.route('/api/outputs/<int:output_id>', methods=['POST'])
    def select_output(output_id):
        """Select audio output."""
        logger.info(f"Output {output_id} selected")
        return jsonify({'status': 'selected', 'output_id': output_id})
    
    # Settings routes
    @app.route('/api/settings', methods=['GET'])
    def get_settings():
        """Get application settings."""
        return jsonify({
            'volume': 0.8,
            'theme': 'dark',
            'language': 'en',
            'autoplay': True,
            'shuffle': False,
            'repeat': 'off',
        })
    
    @app.route('/api/settings', methods=['PUT'])
    def update_settings():
        """Update settings."""
        data = request.json or {}
        logger.info(f"Settings updated: {data}")
        return jsonify({'status': 'updated', 'settings': data})
    
    # Torrenting routes
    @app.route('/api/torrents', methods=['GET'])
    def list_torrents():
        """List active torrents."""
        return jsonify({'torrents': []})
    
    @app.route('/api/torrents/add', methods=['POST'])
    def add_torrent():
        """Add new torrent."""
        data = request.json or {}
        magnet = data.get('magnet')
        
        logger.info(f"Adding torrent: {magnet}")
        return jsonify({'status': 'added', 'id': 'torrent_1'})
    
    # Device info routes
    @app.route('/api/device/info', methods=['GET'])
    def device_info():
        """Get device information."""
        return jsonify({
            'name': 'AudioStream Player',
            'version': '1.0.0',
            'platform': 'Linux',
            'uptime': 3600,
        })
    
    logger.info("Routes registered")
