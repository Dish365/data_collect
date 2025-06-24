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
        
        # The main connection is not established here for threading safety.
        self.conn = None

    def get_db_connection(self):
        """Creates and returns a new database connection for the calling thread."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
        
    def init_database(self):
        """Initialize SQLite database with schema using a temporary connection."""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Projects table - add user_id for isolation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                created_by TEXT NOT NULL,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sync_status TEXT DEFAULT 'pending',
                cloud_id TEXT
            )
        ''')
        
        # Questions table - add user_id for isolation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                project_id TEXT REFERENCES projects(id),
                question_text TEXT NOT NULL,
                question_type TEXT NOT NULL,
                options TEXT,
                validation_rules TEXT,
                order_index INTEGER,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sync_status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Responses table - add user_id for isolation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id TEXT PRIMARY KEY,
                project_id TEXT REFERENCES projects(id),
                question_id TEXT REFERENCES questions(id),
                respondent_id TEXT,
                response_value TEXT,
                response_metadata TEXT,
                collected_by TEXT,
                user_id TEXT NOT NULL,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sync_status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Sync queue table - add user_id for isolation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                record_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                data TEXT,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                attempts INTEGER DEFAULT 0,
                last_attempt TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Add indexes for better performance with user filtering
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_questions_user_id ON questions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_responses_user_id ON responses(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_queue_user_id ON sync_queue(user_id)')
        
        conn.commit()
        conn.close()
    
    def clear_user_data(self, user_id):
        """Clears all data for a specific user from the database."""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            # Clear in order to respect foreign key constraints
            cursor.execute('DELETE FROM responses WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM questions WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM projects WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM sync_queue WHERE user_id = ?', (user_id,))
            conn.commit()
            print(f"Cleared all data for user {user_id}")
        except Exception as e:
            print(f"Error clearing user data: {e}")
        finally:
            conn.close()
    
    def clear_sync_queue(self):
        """Clears all entries from the sync_queue table."""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM sync_queue')
            conn.commit()
            print("Sync queue cleared.")
        except Exception as e:
            print(f"Error clearing sync queue: {e}")
        finally:
            conn.close()

    def close(self):
        # This method is no longer necessary for a shared connection.
        pass

    def migrate_existing_data(self):
        """Migrate existing data to include user_id fields for backward compatibility."""
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Check if user_id column exists in projects table
            cursor.execute("PRAGMA table_info(projects)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'user_id' not in columns:
                print("Migrating projects table...")
                cursor.execute("ALTER TABLE projects ADD COLUMN user_id TEXT")
                # For existing projects, we'll set user_id to 'unknown' since we can't determine the original user
                cursor.execute("UPDATE projects SET user_id = 'unknown' WHERE user_id IS NULL")
            
            # Check if user_id column exists in questions table
            cursor.execute("PRAGMA table_info(questions)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'user_id' not in columns:
                print("Migrating questions table...")
                cursor.execute("ALTER TABLE questions ADD COLUMN user_id TEXT")
                cursor.execute("UPDATE questions SET user_id = 'unknown' WHERE user_id IS NULL")
            
            # Check if user_id column exists in responses table
            cursor.execute("PRAGMA table_info(responses)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'user_id' not in columns:
                print("Migrating responses table...")
                cursor.execute("ALTER TABLE responses ADD COLUMN user_id TEXT")
                cursor.execute("UPDATE responses SET user_id = 'unknown' WHERE user_id IS NULL")
            
            # Check if user_id column exists in sync_queue table
            cursor.execute("PRAGMA table_info(sync_queue)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'user_id' not in columns:
                print("Migrating sync_queue table...")
                cursor.execute("ALTER TABLE sync_queue ADD COLUMN user_id TEXT")
                cursor.execute("UPDATE sync_queue SET user_id = 'unknown' WHERE user_id IS NULL")
            
            # Create indexes if they don't exist
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_user_id ON questions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_responses_user_id ON responses(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sync_queue_user_id ON sync_queue(user_id)")
            
            conn.commit()
            print("Database migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
        finally:
            conn.close()