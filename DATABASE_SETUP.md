# Database Setup Guide

## Overview
VoiceShield uses SQLite database to store user accounts, uploaded audio files, and analysis results.

## Database Schema

### Tables

#### 1. `users` - User Accounts
Stores user authentication information.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Unique user ID |
| email | TEXT UNIQUE | User email address |
| password | TEXT | Hashed password |
| created_at | TIMESTAMP | Account creation date |
| last_login | TIMESTAMP | Last login timestamp |
| is_active | INTEGER | Account status (1=active, 0=inactive) |

#### 2. `audio_files` - Uploaded Audio Files
Stores metadata about uploaded audio files.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Unique file ID |
| user_id | INTEGER | Owner user ID (FK to users) |
| filename | TEXT | Stored filename |
| original_filename | TEXT | Original filename |
| file_path | TEXT | Relative path to file |
| file_size | INTEGER | File size in bytes |
| file_format | TEXT | Audio format (mp3, wav, etc.) |
| duration | REAL | Audio duration in seconds |
| sample_rate | INTEGER | Audio sample rate |
| uploaded_at | TIMESTAMP | Upload timestamp |

#### 3. `analysis_results` - Voice Analysis Results
Stores AI detection analysis results.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Unique result ID |
| audio_file_id | INTEGER | Analyzed file ID (FK to audio_files) |
| user_id | INTEGER | Owner user ID (FK to users) |
| is_ai_generated | INTEGER | 1 if AI detected, 0 if human |
| confidence_score | REAL | Detection confidence (0.0-1.0) |
| scam_patterns | TEXT | JSON array of detected patterns |
| analysis_details | TEXT | JSON object with analysis details |
| spectral_features | TEXT | JSON object with spectral features |
| analyzed_at | TIMESTAMP | Analysis timestamp |

## Indexes

The following indexes are created for performance:

- `idx_users_email` - Fast user lookup by email
- `idx_audio_files_user_id` - Fast file lookup by user
- `idx_audio_files_uploaded_at` - Sorting files by date
- `idx_analysis_results_user_id` - Fast analysis lookup by user
- `idx_analysis_results_audio_file_id` - Fast analysis lookup by file
- `idx_analysis_results_analyzed_at` - Sorting analyses by date

## Initialization

### First Time Setup

Run the database initialization script:

```bash
python init_database.py
```

This will:
1. Create the `database/` directory if it doesn't exist
2. Create the SQLite database file `voiceshield.db`
3. Create all tables with proper schema
4. Create indexes for performance
5. Display the database schema

### Reset Database (WARNING: Deletes all data)

```bash
python init_database.py --reset
```

## Database Location

- **Path**: `database/voiceshield.db`
- **Format**: SQLite 3
- **Backup**: Regularly backup this file for data safety

## Usage in Application

The database is automatically initialized when `app.py` starts. The `init_db()` function in `app.py` creates tables if they don't exist.

For advanced database operations, use the `database_utils.py` module which provides helper functions for common database operations.

## Data Relationships

```
users (1) ──< (many) audio_files
users (1) ──< (many) analysis_results
audio_files (1) ──< (many) analysis_results
```

- One user can have many audio files
- One user can have many analysis results
- One audio file can have many analysis results (re-analysis)

## Foreign Keys

Foreign key constraints are enabled with `ON DELETE CASCADE`:
- Deleting a user deletes their files and analyses
- Deleting an audio file deletes its analyses

## Notes

- All timestamps are stored in UTC
- Passwords are hashed using Werkzeug's password hashing
- JSON fields (scam_patterns, analysis_details, spectral_features) store serialized data
- The database uses SQLite, suitable for small to medium scale applications
- For production with high traffic, consider migrating to PostgreSQL
