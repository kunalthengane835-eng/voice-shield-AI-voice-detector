"""
Voice Importer Module
Handles audio file imports, validation, and storage
"""
import os
import sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid


class VoiceImporter:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        os.makedirs(upload_folder, exist_ok=True)
    
    def import_audio(self, file, user_id):
        """
        Import and save an audio file
        
        Args:
            file: Flask file object
            user_id: ID of the user uploading the file
        
        Returns:
            dict: Result with success status, file_id, filename, or error message
        """
        try:
            # Validate file
            if not file:
                return {'success': False, 'error': 'No file provided'}
            
            # Get file info
            original_filename = secure_filename(file.filename)
            file_ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
            
            # Generate unique filename
            unique_id = str(uuid.uuid4())
            safe_filename = f"{unique_id}.{file_ext}"
            
            # Create user-specific directory
            user_folder = os.path.join(self.upload_folder, str(user_id))
            os.makedirs(user_folder, exist_ok=True)
            
            # Save file
            file_path = os.path.join(str(user_id), safe_filename)
            full_path = os.path.join(self.upload_folder, file_path)
            file.save(full_path)
            
            # Get file size
            file_size = os.path.getsize(full_path)
            
            # Validate file was saved
            if not os.path.exists(full_path):
                return {'success': False, 'error': 'Failed to save file'}
            
            # Store file metadata in database
            conn = sqlite3.connect('database/voiceshield.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO audio_files (user_id, filename, original_filename, file_path, file_size)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, safe_filename, original_filename, file_path, file_size))
            
            file_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'file_id': file_id,
                'filename': safe_filename,
                'original_filename': original_filename,
                'file_path': file_path,
                'file_size': file_size
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def validate_audio_file(self, file_path):
        """
        Validate that the file is a valid audio file
        
        Args:
            file_path: Path to the audio file
        
        Returns:
            dict: Validation result with success status and details
        """
        try:
            if not os.path.exists(file_path):
                return {'valid': False, 'error': 'File does not exist'}
            
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return {'valid': False, 'error': 'File is empty'}
            
            # Additional validation can be added here (e.g., check file headers)
            return {'valid': True, 'file_size': file_size}
        
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def delete_audio_file(self, file_id, user_id):
        """
        Delete an audio file and its database record
        
        Args:
            file_id: ID of the file to delete
            user_id: ID of the user (for security)
        
        Returns:
            dict: Result with success status
        """
        try:
            conn = sqlite3.connect('database/voiceshield.db')
            cursor = conn.cursor()
            
            # Get file info
            cursor.execute(
                'SELECT file_path FROM audio_files WHERE id = ? AND user_id = ?',
                (file_id, user_id)
            )
            file_record = cursor.fetchone()
            
            if not file_record:
                conn.close()
                return {'success': False, 'error': 'File not found'}
            
            file_path = file_record[0]
            full_path = os.path.join(self.upload_folder, file_path)
            
            # Delete file from filesystem
            if os.path.exists(full_path):
                os.remove(full_path)
            
            # Delete from database
            cursor.execute('DELETE FROM audio_files WHERE id = ? AND user_id = ?', (file_id, user_id))
            conn.commit()
            conn.close()
            
            return {'success': True}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
