"""
Database Utility Functions
Helper functions for database operations
"""
import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager


DB_PATH = 'database/voiceshield.db'


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
    finally:
        conn.close()


def get_user_by_email(email):
    """Get user by email"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id):
    """Get user by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_audio_file(file_id, user_id):
    """Get audio file by ID and user ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM audio_files WHERE id = ? AND user_id = ?',
            (file_id, user_id)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_audio_files(user_id, limit=100):
    """Get all audio files for a user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM audio_files 
            WHERE user_id = ? 
            ORDER BY uploaded_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_analysis_results(user_id, limit=100):
    """Get analysis results for a user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                ar.*,
                af.original_filename,
                af.uploaded_at as file_uploaded_at
            FROM analysis_results ar
            JOIN audio_files af ON ar.audio_file_id = af.id
            WHERE ar.user_id = ?
            ORDER BY ar.analyzed_at DESC
            LIMIT ?
        ''', (user_id, limit))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_analysis_by_id(result_id, user_id):
    """Get analysis result by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                ar.*,
                af.original_filename,
                af.file_path
            FROM analysis_results ar
            JOIN audio_files af ON ar.audio_file_id = af.id
            WHERE ar.id = ? AND ar.user_id = ?
        ''', (result_id, user_id))
        row = cursor.fetchone()
        return dict(row) if row else None


def save_analysis_result(audio_file_id, user_id, analysis_result):
    """Save analysis result to database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analysis_results 
            (audio_file_id, user_id, is_ai_generated, confidence_score, 
             scam_patterns, analysis_details, spectral_features)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            audio_file_id,
            user_id,
            1 if analysis_result['is_ai_generated'] else 0,
            analysis_result['confidence'],
            json.dumps(analysis_result.get('scam_patterns', [])),
            json.dumps(analysis_result.get('details', {})),
            json.dumps(analysis_result.get('details', {}).get('spectral_features', {}))
        ))
        conn.commit()
        return cursor.lastrowid


def get_statistics(user_id):
    """Get user statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Total files
        cursor.execute('SELECT COUNT(*) as count FROM audio_files WHERE user_id = ?', (user_id,))
        total_files = cursor.fetchone()['count']
        
        # Total analyses
        cursor.execute('SELECT COUNT(*) as count FROM analysis_results WHERE user_id = ?', (user_id,))
        total_analyses = cursor.fetchone()['count']
        
        # AI detected count
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM analysis_results 
            WHERE user_id = ? AND is_ai_generated = 1
        ''', (user_id,))
        ai_detected = cursor.fetchone()['count']
        
        # Average confidence
        cursor.execute('''
            SELECT AVG(confidence_score) as avg_confidence 
            FROM analysis_results 
            WHERE user_id = ?
        ''', (user_id,))
        avg_confidence = cursor.fetchone()['avg_confidence'] or 0
        
        return {
            'total_files': total_files,
            'total_analyses': total_analyses,
            'ai_detected': ai_detected,
            'average_confidence': float(avg_confidence) if avg_confidence else 0.0
        }
