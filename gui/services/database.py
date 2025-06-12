import sqlite3
import json
from datetime import datetime
from pathlib import Path
from kivy.utils import platform

class DatabaseService:
    def __init__(self):
        if platform == 'android':
            from android.storage import app_storage_path
            self.db_path = Path(app_storage_path()) / 'research_data.db'
        else:
            self.db_path = Path.home() / 'research_data.db'
        
        self.conn = None
        
    def init_database(self):
        """Initialize SQLite database with schema"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        # Create tables
        self._create_tables()
        
    def _create_tables(self):
        """Create all necessary tables"""
        cursor = self.conn.cursor()
        
        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sync_status TEXT DEFAULT 'pending',
                cloud_id TEXT
            )
        ''')
        
        # Questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                project_id TEXT REFERENCES projects(id),
                question_text TEXT NOT NULL,
                question_type TEXT NOT NULL,
                options TEXT,
                validation_rules TEXT,
                order_index INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sync_status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Responses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id TEXT PRIMARY KEY,
                project_id TEXT REFERENCES projects(id),
                question_id TEXT REFERENCES questions(id),
                respondent_id TEXT,
                response_value TEXT,
                response_metadata TEXT,
                collected_by TEXT,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sync_status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Sync queue table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                record_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                attempts INTEGER DEFAULT 0,
                last_attempt TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        self.conn.commit()
    
    def close(self):
        if self.conn:
            self.conn.close() 