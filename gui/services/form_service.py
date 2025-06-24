import uuid
import json
from datetime import datetime
import time

class FormService:
    def __init__(self, auth_service, db_service, sync_service):
        self.auth_service = auth_service
        self.db_service = db_service
        self.sync_service = sync_service

    def _safe_db_write(self, db_func, *args, **kwargs):
        """Executes a database write operation with retry logic for locked databases."""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                return db_func(*args, **kwargs)
            except Exception as e:
                if 'database is locked' in str(e):
                    time.sleep(0.2)
                else:
                    raise
        raise Exception("Database is locked after several retries.")

    def load_questions(self, project_id):
        """Loads questions for a project, from API if online, otherwise from local DB."""
        # Try fetching from API first - use the correct endpoint
        response = self.auth_service.make_authenticated_request(f'api/v1/questions/?project_id={project_id}')

        conn = self.db_service.get_db_connection()
        try:
            if 'error' not in response:
                # Sync with local DB
                api_questions = response if isinstance(response, list) else response.get('results', [])
                self._sync_local_questions(conn, project_id, api_questions)

            # Always return from local DB to have a single source of truth for the UI
            # Add user filtering to ensure only user-specific data
            user_id = self.auth_service.get_user_data().get('id')
            cursor = conn.cursor()
            if user_id:
                cursor.execute("SELECT * FROM questions WHERE project_id = ? AND user_id = ? ORDER BY order_index", (project_id, user_id))
            else:
                cursor.execute("SELECT * FROM questions WHERE project_id = ? ORDER BY order_index", (project_id,))
            questions_data = [dict(row) for row in cursor.fetchall()]
            return questions_data, None
        except Exception as e:
            return [], str(e)
        finally:
            if conn:
                conn.close()
    
    def _sync_local_questions(self, conn, project_id, api_questions):
        """Syncs local questions for a project with data from the API."""
        def db_write():
            cursor = conn.cursor()
            user_id = self.auth_service.get_user_data().get('id')
            # Clear existing non-pending questions for this project and user
            if user_id:
                cursor.execute("DELETE FROM questions WHERE project_id = ? AND user_id = ? AND sync_status != 'pending'", (project_id, user_id))
            else:
                cursor.execute("DELETE FROM questions WHERE project_id = ? AND sync_status != 'pending'", (project_id,))
            
            for q in api_questions:
                cursor.execute("""
                    INSERT OR REPLACE INTO questions 
                    (id, project_id, question_text, question_type, options, validation_rules, order_index, user_id, sync_status) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (q.get('id'), project_id, q.get('question_text'), q.get('question_type'),
                      json.dumps(q.get('options')), json.dumps(q.get('validation_rules')),
                      q.get('order_index'), user_id, 'synced'))
            conn.commit()
        
        self._safe_db_write(db_write)

    def save_questions(self, project_id, questions_to_save):
        """Saves the full list of questions for a project, handling online/offline sync."""
        # Try online save first
        is_online = self.auth_service.is_authenticated()
        if is_online:
            # Prepare payload for bulk create
            payload = []
            for index, q_data in enumerate(questions_to_save):
                payload.append({
                    'project': project_id,
                    'question_text': q_data['question_text'],
                    'question_type': q_data['question_type'],
                    'options': q_data.get('options'),
                    'validation_rules': q_data.get('validation_rules'),
                    'order_index': index
                })
            response = self.auth_service.make_authenticated_request(
                'api/v1/questions/',
                method='POST',
                data=payload
            )
            if 'error' not in response:
                # Save returned questions to local DB as synced
                def db_write():
                    conn = self.db_service.get_db_connection()
                    try:
                        cursor = conn.cursor()
                        user_id = self.auth_service.get_user_data().get('id')
                        if user_id:
                            cursor.execute("DELETE FROM questions WHERE project_id = ? AND user_id = ?", (project_id, user_id))
                        else:
                            cursor.execute("DELETE FROM questions WHERE project_id = ?", (project_id,))
                        conn.commit()
                        # The response may be a list or dict with 'results'
                        questions = response if isinstance(response, list) else response.get('results', [])
                        for q in questions:
                            cursor.execute("""
                                INSERT OR REPLACE INTO questions 
                                (id, project_id, question_text, question_type, options, validation_rules, order_index, user_id, sync_status) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                q.get('id'), project_id, q.get('question_text'), q.get('question_type'),
                                json.dumps(q.get('options')), json.dumps(q.get('validation_rules')),
                                q.get('order_index'), user_id, 'synced'))
                        conn.commit()
                        return {'message': 'Form saved to backend!', 'reload': True}
                    finally:
                        if conn:
                            conn.close()
                return self._safe_db_write(db_write)
            # If error, fall through to offline logic
        # Offline or failed online save: fallback to local save and queue for sync
        def db_write():
            conn = self.db_service.get_db_connection()
            try:
                cursor = conn.cursor()
                user_id = self.auth_service.get_user_data().get('id')
                # First, clear all existing questions for this project from the local DB
                if user_id:
                    cursor.execute("DELETE FROM questions WHERE project_id = ? AND user_id = ?", (project_id, user_id))
                else:
                    cursor.execute("DELETE FROM questions WHERE project_id = ?", (project_id,))
                conn.commit()

                # Now, insert the new set of questions
                for index, q_data in enumerate(questions_to_save):
                    q_data['order_index'] = index
                    self._save_single_question(conn, project_id, q_data)
                return {'message': 'Form saved locally (offline mode)', 'reload': True}
            finally:
                if conn:
                    conn.close()
        return self._safe_db_write(db_write)

    def _save_single_question(self, conn, project_id, q_data):
        """Saves a single question and queues it for sync if needed."""
        api_data = {
            'project': project_id,
            'question_text': q_data['question_text'],
            'question_type': q_data['question_type'],
            'options': q_data.get('options'),
            'validation_rules': q_data.get('validation_rules'),
            'order_index': q_data['order_index']
        }

        # We assume saving the whole form is an "all or nothing" action.
        # For simplicity, we create new questions locally with a 'pending' status
        # and queue them for creation. A more complex sync would be needed for updates/deletes here.
        
        question_id = str(uuid.uuid4())
        user_id = self.auth_service.get_user_data().get('id')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO questions (id, project_id, question_text, question_type, options, validation_rules, order_index, user_id, sync_status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (question_id, project_id, q_data['question_text'], q_data['question_type'],
              json.dumps(q_data.get('options')), json.dumps(q_data.get('validation_rules')),
              q_data['order_index'], user_id, 'pending'))
        conn.commit()
        
        # Queue for sync
        self.sync_service.queue_sync('questions', question_id, 'create', api_data) 