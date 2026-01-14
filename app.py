from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import jwt
from functools import wraps
import uuid

from voice_importer import VoiceImporter
from voice_detector import VoiceDetector
from config import config as app_config

app = Flask(__name__, static_folder='.')
CORS(app)

# Load configuration (defaults to development, override with FLASK_ENV in production)
env = os.environ.get('FLASK_ENV', 'development')
cfg_class = app_config.get(env, app_config['default'])
app.config.from_object(cfg_class)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('database', exist_ok=True)

# Initialize modules
voice_importer = VoiceImporter(app.config['UPLOAD_FOLDER'])
voice_detector = VoiceDetector()

# Database initialization
def init_db():
    conn = sqlite3.connect('database/voiceshield.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Audio files table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audio_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Analysis results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audio_file_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            is_ai_generated REAL NOT NULL,
            confidence_score REAL NOT NULL,
            scam_patterns TEXT,
            analysis_details TEXT,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (audio_file_id) REFERENCES audio_files(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# JWT token helper functions
def generate_token(user_id, email):
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow().timestamp() + 86400  # 24 hours
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        request.user_id = payload['user_id']
        request.user_email = payload['email']
        return f(*args, **kwargs)
    
    return decorated

# Helper function to check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Authentication Routes
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        conn = sqlite3.connect('database/voiceshield.db')
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'User already exists'}), 400
        
        # Create new user
        hashed_password = generate_password_hash(password)
        cursor.execute(
            'INSERT INTO users (email, password) VALUES (?, ?)',
            (email, hashed_password)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        token = generate_token(user_id, email)
        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': {'id': user_id, 'email': email}
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        conn = sqlite3.connect('database/voiceshield.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, password FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user_id, user_email, hashed_password = user
        if not check_password_hash(hashed_password, password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        token = generate_token(user_id, user_email)
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {'id': user_id, 'email': user_email}
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Voice Analysis Routes
@app.route('/api/voice/upload', methods=['POST'])
@token_required
def upload_voice():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: MP3, WAV, M4A, OGG, FLAC'}), 400
        
        # Save file using voice importer
        result = voice_importer.import_audio(file, request.user_id)
        
        if result['success']:
            return jsonify({
                'message': 'File uploaded successfully',
                'file_id': result['file_id'],
                'filename': result['filename']
            }), 201
        else:
            return jsonify({'error': result.get('error', 'Upload failed')}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/voice/analyze/<int:file_id>', methods=['POST'])
@token_required
def analyze_voice(file_id):
    try:
        conn = sqlite3.connect('database/voiceshield.db')
        cursor = conn.cursor()
        
        # Get audio file
        cursor.execute(
            'SELECT id, file_path, user_id FROM audio_files WHERE id = ? AND user_id = ?',
            (file_id, request.user_id)
        )
        audio_file = cursor.fetchone()
        
        if not audio_file:
            conn.close()
            return jsonify({'error': 'Audio file not found'}), 404
        
        file_path = audio_file[1]
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
        
        if not os.path.exists(full_path):
            conn.close()
            return jsonify({'error': 'File not found on server'}), 404
        
        # Analyze voice using voice detector
        analysis_result = voice_detector.detect_ai_voice(full_path)
        
        # Save analysis results
        cursor.execute('''
            INSERT INTO analysis_results 
            (audio_file_id, user_id, is_ai_generated, confidence_score, scam_patterns, analysis_details)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            file_id,
            request.user_id,
            analysis_result['is_ai_generated'],
            analysis_result['confidence'],
            str(analysis_result.get('scam_patterns', [])),
            str(analysis_result.get('details', {}))
        ))
        
        result_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Analysis completed',
            'result_id': result_id,
            'analysis': analysis_result
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/voice/history', methods=['GET'])
@token_required
def get_history():
    try:
        conn = sqlite3.connect('database/voiceshield.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                ar.id,
                af.original_filename,
                af.uploaded_at,
                ar.is_ai_generated,
                ar.confidence_score,
                ar.scam_patterns,
                ar.analyzed_at
            FROM analysis_results ar
            JOIN audio_files af ON ar.audio_file_id = af.id
            WHERE ar.user_id = ?
            ORDER BY ar.analyzed_at DESC
        ''', (request.user_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        history = []
        for row in results:
            history.append({
                'id': row[0],
                'filename': row[1],
                'uploaded_at': row[2],
                'is_ai_generated': bool(row[3]),
                'confidence_score': row[4],
                'scam_patterns': row[5],
                'analyzed_at': row[6]
            })
        
        return jsonify({'history': history}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/voice/files', methods=['GET'])
@token_required
def get_files():
    try:
        conn = sqlite3.connect('database/voiceshield.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, original_filename, file_size, uploaded_at
            FROM audio_files
            WHERE user_id = ?
            ORDER BY uploaded_at DESC
        ''', (request.user_id,))
        
        files = cursor.fetchall()
        conn.close()
        
        file_list = []
        for file in files:
            file_list.append({
                'id': file[0],
                'filename': file[1],
                'file_size': file[2],
                'uploaded_at': file[3]
            })
        
        return jsonify({'files': file_list}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve static files (HTML pages)
@app.route('/')
def index():
    return send_from_directory('.', 'mainpage.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', debug=debug, port=port)
