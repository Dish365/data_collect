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
                sync_status TEXT DEFAULT 'pending',
                is_required BOOLEAN DEFAULT 1
            )
        ''')
        
        # Migration: Add is_required column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE questions ADD COLUMN is_required BOOLEAN DEFAULT 1")
            print("Added is_required column to questions table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                print(f"Migration warning: {e}")
            # Column already exists, continue
        
        # Respondents table - tracks individual survey participants
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS respondents (
                id TEXT PRIMARY KEY,
                respondent_id TEXT UNIQUE NOT NULL,
                project_id TEXT REFERENCES projects(id),
                name TEXT,
                email TEXT,
                phone TEXT,
                demographics TEXT,
                location_data TEXT,
                is_anonymous INTEGER DEFAULT 1,
                consent_given INTEGER DEFAULT 0,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_response_at TIMESTAMP,
                sync_status TEXT DEFAULT 'pending',
                user_id TEXT NOT NULL
            )
        ''')
        
        # Responses table - add user_id for isolation and link to respondents
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                response_id TEXT PRIMARY KEY,
                project_id TEXT REFERENCES projects(id),
                question_id TEXT REFERENCES questions(id),
                respondent_id TEXT REFERENCES respondents(respondent_id),
                response_value TEXT,
                response_metadata TEXT,
                location_data TEXT,
                device_info TEXT,
                collected_by TEXT,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sync_status TEXT DEFAULT 'pending',
                user_id TEXT NOT NULL
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
                status TEXT DEFAULT 'pending',
                priority INTEGER DEFAULT 1
            )
        ''')
        
        # Migration: Add priority column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE sync_queue ADD COLUMN priority INTEGER DEFAULT 1")
            print("Added priority column to sync_queue table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                print(f"Migration warning: {e}")
            # Column already exists, continue
        
        conn.commit()
        conn.close()
        
        # Run migration to ensure backward compatibility
        self.migrate_existing_data()
        
        # Now create indexes after migration
        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            # Add indexes for better performance with user filtering
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_questions_user_id ON questions(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_respondents_user_id ON respondents(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_respondents_project_id ON respondents(project_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_responses_user_id ON responses(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_responses_respondent_id ON responses(respondent_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_queue_user_id ON sync_queue(user_id)')
            conn.commit()
        except Exception as e:
            print(f"Warning: Could not create indexes: {e}")
        finally:
            conn.close()
    
    def set_current_user(self, user_id):
        """Set the current user for this database session"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Create a simple user session table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_session (
                    id INTEGER PRIMARY KEY,
                    current_user_id TEXT,
                    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Clear previous session data
            cursor.execute('DELETE FROM user_session')
            
            # Set current user
            if user_id:
                cursor.execute(
                    'INSERT INTO user_session (current_user_id) VALUES (?)',
                    (user_id,)
                )
                print(f"Database session set for user: {user_id}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error setting current user in database: {e}")

    def get_current_user(self):
        """Get the current user from database session"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT current_user_id FROM user_session ORDER BY session_start DESC LIMIT 1')
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            return None
            
        except Exception as e:
            print(f"Error getting current user from database: {e}")
            return None

    def ensure_user_context(self, expected_user_id):
        """Ensure the database context matches the expected user"""
        try:
            current_user = self.get_current_user()
            if current_user != expected_user_id:
                print(f"Database user context mismatch. Expected: {expected_user_id}, Found: {current_user}")
                self.set_current_user(expected_user_id)
                return False
            return True
        except Exception as e:
            print(f"Error ensuring user context: {e}")
            return False

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
            
            # Also clear user session if it matches
            cursor.execute('DELETE FROM user_session WHERE current_user_id = ?', (user_id,))
            
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
            
            # Check if projects table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
            if cursor.fetchone():
                # Check if user_id column exists in projects table
                cursor.execute("PRAGMA table_info(projects)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'user_id' not in columns:
                    print("Migrating projects table...")
                    cursor.execute("ALTER TABLE projects ADD COLUMN user_id TEXT")
                    # For existing projects, we'll set user_id to 'unknown' since we can't determine the original user
                    cursor.execute("UPDATE projects SET user_id = 'unknown' WHERE user_id IS NULL")
            
            # Check if questions table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'")
            if cursor.fetchone():
                # Check if user_id column exists in questions table
                cursor.execute("PRAGMA table_info(questions)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'user_id' not in columns:
                    print("Migrating questions table...")
                    cursor.execute("ALTER TABLE questions ADD COLUMN user_id TEXT")
                    cursor.execute("UPDATE questions SET user_id = 'unknown' WHERE user_id IS NULL")
            
            # Check if responses table exists and migrate its structure
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='responses'")
            if cursor.fetchone():
                # Check current responses table structure
                cursor.execute("PRAGMA table_info(responses)")
                columns = {col[1]: col for col in cursor.fetchall()}
                
                # Check if we need to migrate from old schema (id -> response_id)
                if 'id' in columns and 'response_id' not in columns:
                    print("Migrating responses table structure...")
                    self._migrate_responses_table_structure(cursor, conn)
                elif 'user_id' not in columns:
                    print("Adding user_id to responses table...")
                    cursor.execute("ALTER TABLE responses ADD COLUMN user_id TEXT")
                    cursor.execute("UPDATE responses SET user_id = 'unknown' WHERE user_id IS NULL")
                
                # Add missing columns if needed
                required_columns = ['location_data', 'device_info']
                for col in required_columns:
                    if col not in columns:
                        print(f"Adding {col} column to responses table...")
                        cursor.execute(f"ALTER TABLE responses ADD COLUMN {col} TEXT")
            
            # Check if sync_queue table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sync_queue'")
            if cursor.fetchone():
                # Check if user_id column exists in sync_queue table
                cursor.execute("PRAGMA table_info(sync_queue)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'user_id' not in columns:
                    print("Migrating sync_queue table...")
                    cursor.execute("ALTER TABLE sync_queue ADD COLUMN user_id TEXT")
                    cursor.execute("UPDATE sync_queue SET user_id = 'unknown' WHERE user_id IS NULL")
            
            conn.commit()
            print("Database migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            # If migration fails, we'll continue anyway
        finally:
            conn.close()

    def _migrate_responses_table_structure(self, cursor, conn):
        """Migrate responses table from old schema (id) to new schema (response_id)"""
        try:
            print("Migrating responses table to new structure...")
            
            # Create new responses table with correct schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS responses_new (
                    response_id TEXT PRIMARY KEY,
                    project_id TEXT REFERENCES projects(id),
                    question_id TEXT REFERENCES questions(id),
                    respondent_id TEXT,
                    response_value TEXT,
                    response_metadata TEXT,
                    location_data TEXT,
                    device_info TEXT,
                    collected_by TEXT,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sync_status TEXT DEFAULT 'pending',
                    user_id TEXT NOT NULL
                )
            ''')
            
            # Copy data from old table to new table, generating new response_ids
            cursor.execute('''
                INSERT INTO responses_new 
                (response_id, project_id, question_id, respondent_id, response_value, 
                 response_metadata, collected_by, collected_at, sync_status, user_id)
                SELECT 
                    COALESCE(id, hex(randomblob(16))) as response_id,
                    project_id,
                    question_id,
                    respondent_id,
                    response_value,
                    COALESCE(response_metadata, '{}') as response_metadata,
                    collected_by,
                    COALESCE(collected_at, datetime('now')) as collected_at,
                    COALESCE(sync_status, 'pending') as sync_status,
                    COALESCE(user_id, 'unknown') as user_id
                FROM responses
            ''')
            
            # Drop old table and rename new one
            cursor.execute('DROP TABLE responses')
            cursor.execute('ALTER TABLE responses_new RENAME TO responses')
            
            conn.commit()
            print("Successfully migrated responses table structure")
            
        except Exception as e:
            print(f"Error migrating responses table structure: {e}")
            # If this fails, the init_database will recreate the table with correct schema

    def clear_all_sessions(self):
        """Clear all user sessions - useful for complete logout"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM user_session')
            conn.commit()
            conn.close()
            print("All user sessions cleared")
        except Exception as e:
            print(f"Error clearing sessions: {e}")

    def get_user_specific_stats(self, user_id):
        """Get user-specific statistics from local database"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Projects count
            cursor.execute(
                "SELECT COUNT(*) FROM projects WHERE user_id = ? AND sync_status != 'pending_delete'", 
                (user_id,)
            )
            projects = cursor.fetchone()[0]
            
            # Responses count
            cursor.execute(
                "SELECT COUNT(*) FROM responses WHERE user_id = ?", 
                (user_id,)
            )
            responses = cursor.fetchone()[0]
            
            # Sync queue stats
            cursor.execute(
                "SELECT COUNT(*) FROM sync_queue WHERE user_id = ? AND status = 'pending'", 
                (user_id,)
            )
            pending_sync = cursor.fetchone()[0]
            
            cursor.execute(
                "SELECT COUNT(*) FROM sync_queue WHERE user_id = ? AND status = 'failed'", 
                (user_id,)
            )
            failed_sync = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'projects': projects,
                'responses': responses,
                'pending_sync': pending_sync,
                'failed_sync': failed_sync
            }
            
        except Exception as e:
            print(f"Error getting user-specific stats: {e}")
            return {
                'projects': 0,
                'responses': 0,
                'pending_sync': 0,
                'failed_sync': 0
            }

    def cleanup_stale_sync_data(self):
        """Clean up sync queue items with unknown or null user_id"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Count items to be cleaned
            cursor.execute("SELECT COUNT(*) FROM sync_queue WHERE user_id IS NULL OR user_id = 'unknown'")
            stale_count = cursor.fetchone()[0]
            
            if stale_count > 0:
                print(f"Cleaning up {stale_count} stale sync queue items")
                # Remove items with unknown or null user_id
                cursor.execute("DELETE FROM sync_queue WHERE user_id IS NULL OR user_id = 'unknown'")
                conn.commit()
                print(f"Cleaned up {stale_count} stale sync queue items")
            else:
                print("No stale sync queue items to clean up")
            
            conn.close()
            
        except Exception as e:
            print(f"Error cleaning up stale sync data: {e}")

    def ensure_user_data_integrity(self, user_id):
        """Ensure data integrity for a specific user"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Check for any data that might not be properly associated with the user
            cursor.execute("SELECT COUNT(*) FROM projects WHERE user_id != ? AND user_id != 'unknown'", (user_id,))
            other_projects = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sync_queue WHERE user_id != ? AND user_id != 'unknown'", (user_id,))
            other_sync = cursor.fetchone()[0]
            
            if other_projects > 0 or other_sync > 0:
                print(f"Warning: Found data belonging to other users (Projects: {other_projects}, Sync: {other_sync})")
            
            # Get user-specific counts
            cursor.execute("SELECT COUNT(*) FROM projects WHERE user_id = ?", (user_id,))
            user_projects = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sync_queue WHERE user_id = ?", (user_id,))
            user_sync = cursor.fetchone()[0]
            
            print(f"User {user_id} data integrity check: Projects={user_projects}, Sync={user_sync}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error checking user data integrity: {e}")
            return False