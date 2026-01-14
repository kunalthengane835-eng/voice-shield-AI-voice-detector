# VoiceShield Backend

Python backend for VoiceShield - AI Voice Fraud Detection System

## Features

- User authentication (signup, login with JWT tokens)
- Voice file upload and storage
- AI voice detection using audio analysis
- Scam pattern detection
- Analysis history tracking
- RESTful API endpoints

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Authentication

- `POST /api/auth/signup` - Register a new user
- `POST /api/auth/login` - Login and get JWT token

### Voice Analysis

- `POST /api/voice/upload` - Upload an audio file (requires authentication)
- `POST /api/voice/analyze/<file_id>` - Analyze an uploaded audio file (requires authentication)
- `GET /api/voice/history` - Get analysis history (requires authentication)
- `GET /api/voice/files` - Get list of uploaded files (requires authentication)

## Usage

### Signup
```bash
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

Response includes a JWT token that should be used in the Authorization header:
```
Authorization: Bearer <token>
```

### Upload Audio File
```bash
POST /api/voice/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <audio_file>
```

### Analyze Audio
```bash
POST /api/voice/analyze/<file_id>
Authorization: Bearer <token>
```

## Project Structure

- `app.py` - Main Flask application with API routes
- `voice_importer.py` - Module for handling audio file imports
- `voice_detector.py` - Module for AI voice detection and analysis
- `database/` - SQLite database storage
- `uploads/` - Uploaded audio files storage

## Notes

- Audio files are stored in user-specific directories
- Maximum file size: 50MB
- Supported formats: MP3, WAV, M4A, OGG, FLAC
- The AI detection uses audio feature analysis (spectral features, MFCC, etc.)
- For production, consider:
  - Using a more secure secret key
  - Implementing proper speech-to-text for scam pattern detection
  - Using a production-grade database (PostgreSQL)
  - Adding file validation and virus scanning
  - Implementing rate limiting
