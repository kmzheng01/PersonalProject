"""File upload handler for web interface."""

import os
import uuid
from typing import Dict, Any
from werkzeug.utils import secure_filename

from utils.logger import get_logger
from core.format_handler import FormatHandler

logger = get_logger(__name__)


class FileUploadHandler:
    """Handles file uploads."""

    ALLOWED_EXTENSIONS = FormatHandler.SUPPORTED_FORMATS
    MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB

    def __init__(self, upload_dir: str):
        """
        Initialize upload handler.
        
        Args:
            upload_dir: Directory for uploads
        """
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
        self.uploads: Dict[str, Dict[str, Any]] = {}
        logger.info(f"FileUploadHandler initialized, upload_dir: {upload_dir}")

    def handle_upload(self, file) -> Dict[str, Any]:
        """
        Handle file upload.
        
        Args:
            file: Flask file object
            
        Returns:
            Result dictionary
        """
        if not file or not file.filename:
            return {'success': False, 'error': 'No file provided'}
        
        # Check file extension
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1].lower()
        
        if ext not in self.ALLOWED_EXTENSIONS:
            return {
                'success': False,
                'error': f'File type {ext} not supported'
            }
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Seek back to start
        
        if file_size > self.MAX_FILE_SIZE:
            return {
                'success': False,
                'error': 'File too large'
            }
        
        # Save file with UUID
        upload_id = str(uuid.uuid4())
        filepath = os.path.join(self.upload_dir, f"{upload_id}_{filename}")
        
        try:
            file.save(filepath)
            
            # Validate audio file
            is_valid, message = FormatHandler.validate_audio_file(filepath)
            if not is_valid:
                os.remove(filepath)
                return {'success': False, 'error': message}
            
            # Get format info
            info = FormatHandler.get_format_info(filepath)
            
            # Store upload info
            self.uploads[upload_id] = {
                'filename': filename,
                'filepath': filepath,
                'size': file_size,
                'info': info,
            }
            
            logger.info(f"File uploaded: {filename} (ID: {upload_id})")
            
            return {
                'success': True,
                'upload_id': upload_id,
                'filename': filename,
                'filepath': filepath,
                'size': file_size,
                'info': info,
            }
        
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return {'success': False, 'error': str(e)}

    def get_upload_status(self, upload_id: str) -> Dict[str, Any]:
        """Get status of an upload."""
        if upload_id in self.uploads:
            return {
                'upload_id': upload_id,
                **self.uploads[upload_id],
            }
        return {}

    def delete_upload(self, upload_id: str) -> bool:
        """Delete an uploaded file."""
        if upload_id not in self.uploads:
            return False
        
        try:
            filepath = self.uploads[upload_id]['filepath']
            if os.path.exists(filepath):
                os.remove(filepath)
            del self.uploads[upload_id]
            logger.info(f"Upload deleted: {upload_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting upload {upload_id}: {e}")
            return False

    def get_all_uploads(self) -> Dict[str, Dict[str, Any]]:
        """Get all uploads."""
        return self.uploads.copy()
