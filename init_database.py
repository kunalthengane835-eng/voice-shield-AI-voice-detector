"""
Database Initialization Script
Creates and initializes the VoiceShield database with all necessary tables
Run this script to set up the database before starting the application
"""
import sqlite3
import os


def init_database():
    """Initialize the VoiceShield database with all tables"""
    
    # Ensure database directory exists
    os.makedirs('database', exist_ok=True)
    
    # Connect to database (creates if doesn't exist)
    db_path = 'database/voiceshield.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Initializing VoiceShield Database...")
    print(f"Database location: {os.path.abspath(db_path)}")
    
    # Enable foreign keys
    cursor.execute('PRAGMA foreign_keys = ON')
    
    # Users table - stores user account information
    print("\nCreating users table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Audio files table - stores uploaded audio file metadata
    print("Creating audio_files table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audio_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER,
            file_format TEXT,
            duration REAL,
            sample_rate INTEGER,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Analysis results table - stores voice analysis results
    print("Creating analysis_results table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audio_file_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            is_ai_generated INTEGER NOT NULL,
            confidence_score REAL NOT NULL,
            scam_patterns TEXT,
            analysis_details TEXT,
            spectral_features TEXT,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (audio_file_id) REFERENCES audio_files(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create indexes for better query performance
    print("Creating indexes...")
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audio_files_user_id ON audio_files(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audio_files_uploaded_at ON audio_files(uploaded_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_results_user_id ON analysis_results(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_results_audio_file_id ON analysis_results(audio_file_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_results_analyzed_at ON analysis_results(analyzed_at)')
    
    # Commit changes
    conn.commit()
    
    # Verify tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\n[SUCCESS] Database initialized successfully!")
    print(f"Tables created: {[table[0] for table in tables]}")
    
    # Show table structures
    print("\nDatabase Schema:")
    for table in tables:
        table_name = table[0]
        if table_name != 'sqlite_sequence':
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"\n{table_name}:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
    print("\n" + "="*50)
    print("Database setup complete!")
    print("="*50)


def reset_database():
    """Reset the database (WARNING: Deletes all data)"""
    db_path = 'database/voiceshield.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Deleted existing database: {db_path}")
    init_database()
    print("Database reset complete!")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        confirm = input("⚠️  WARNING: This will delete all data. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            reset_database()
        else:
            print("Reset cancelled.")
    else:
        init_database()
