"""Flask web application for AudioStream."""

from flask import Flask, render_template,jsonify
from flask_cors import CORS
import os

from utils.logger import get_logger
from web.routes import register_routes

logger = get_logger(__name__)


def create_app(config=None):
    """
    Create and configure Flask app.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Flask app instance
    """
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), 'static'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Enable CORS for local network access
    CORS(app)
    
    # Configuration
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB max file size
    app.config['UPLOAD_FOLDER'] = './uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    if config:
        app.config.update(config)
    
    # Health check endpoint
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({'status': 'ok'})
    
    # Register routes
    register_routes(app)
    
    logger.info("Flask app created")
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False)
