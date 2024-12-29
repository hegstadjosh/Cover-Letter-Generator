import sqlite3
from typing import List, Optional, Dict, Tuple
import os
from datetime import datetime

class DocumentDB:
    def __init__(self, db_path: str = "documents.db"):
        """Initialize database connection and create tables if they don't exist."""
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create resumes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS resumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create cover letters table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cover_letters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create job descriptions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_descriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    content TEXT NOT NULL,
                    company TEXT,
                    position TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create biography versions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS biography_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            ''')
            
            # Create AI prompts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    content TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()

    def save_document(self, doc_type: str, name: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """Save a document to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # First check if document exists
                if doc_type == "resume":
                    cursor.execute('SELECT id FROM resumes WHERE name = ?', (name,))
                    if cursor.fetchone():
                        cursor.execute('''
                            UPDATE resumes 
                            SET content = ?, updated_at = ?
                            WHERE name = ?
                        ''', (content, now, name))
                    else:
                        cursor.execute('''
                            INSERT INTO resumes (name, content, created_at, updated_at)
                            VALUES (?, ?, ?, ?)
                        ''', (name, content, now, now))
                
                elif doc_type == "cover_letter":
                    cursor.execute('SELECT id FROM cover_letters WHERE name = ?', (name,))
                    if cursor.fetchone():
                        cursor.execute('''
                            UPDATE cover_letters 
                            SET content = ?, updated_at = ?
                            WHERE name = ?
                        ''', (content, now, name))
                    else:
                        cursor.execute('''
                            INSERT INTO cover_letters (name, content, created_at, updated_at)
                            VALUES (?, ?, ?, ?)
                        ''', (name, content, now, now))
                
                elif doc_type == "job_description":
                    company = metadata.get('company', '') if metadata else ''
                    position = metadata.get('position', '') if metadata else ''
                    cursor.execute('SELECT id FROM job_descriptions WHERE name = ?', (name,))
                    if cursor.fetchone():
                        cursor.execute('''
                            UPDATE job_descriptions 
                            SET content = ?, company = ?, position = ?, updated_at = ?
                            WHERE name = ?
                        ''', (content, company, position, now, name))
                    else:
                        cursor.execute('''
                            INSERT INTO job_descriptions 
                            (name, content, company, position, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (name, content, company, position, now, now))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        except Exception as e:
            print(f"Error saving document: {e}")
            return False

    def get_document(self, doc_type: str, name: str) -> Optional[Dict]:
        """Retrieve a document by name and type."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if doc_type == "resume":
                    cursor.execute('SELECT * FROM resumes WHERE name = ?', (name,))
                elif doc_type == "cover_letter":
                    cursor.execute('SELECT * FROM cover_letters WHERE name = ?', (name,))
                elif doc_type == "job_description":
                    cursor.execute('SELECT * FROM job_descriptions WHERE name = ?', (name,))
                
                result = cursor.fetchone()
                if result:
                    if doc_type == "job_description":
                        return {
                            "id": result[0],
                            "name": result[1],
                            "content": result[2],
                            "company": result[3],
                            "position": result[4],
                            "created_at": result[5],
                            "updated_at": result[6]
                        }
                    else:
                        return {
                            "id": result[0],
                            "name": result[1],
                            "content": result[2],
                            "created_at": result[3],
                            "updated_at": result[4]
                        }
                return None
        except Exception as e:
            print(f"Error retrieving document: {e}")
            return None

    def list_documents(self, doc_type: str) -> List[Dict]:
        """List all documents of a specific type."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if doc_type == "resume":
                    cursor.execute('SELECT name, created_at FROM resumes ORDER BY name')
                elif doc_type == "cover_letter":
                    cursor.execute('SELECT name, created_at FROM cover_letters ORDER BY name')
                elif doc_type == "job_description":
                    cursor.execute('SELECT name, company, position, created_at FROM job_descriptions ORDER BY name')
                
                results = cursor.fetchall()
                if doc_type == "job_description":
                    return [{"name": r[0], "company": r[1], "position": r[2], "created_at": r[3]} for r in results]
                else:
                    return [{"name": r[0], "created_at": r[1]} for r in results]
        except Exception as e:
            print(f"Error listing documents: {e}")
            return []

    def delete_document(self, doc_type: str, name: str) -> bool:
        """Delete a document by name and type."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if doc_type == "resume":
                    cursor.execute('DELETE FROM resumes WHERE name = ?', (name,))
                elif doc_type == "cover_letter":
                    cursor.execute('DELETE FROM cover_letters WHERE name = ?', (name,))
                elif doc_type == "job_description":
                    cursor.execute('DELETE FROM job_descriptions WHERE name = ?', (name,))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

    def save_biography(self, content: str, notes: Optional[str] = None) -> bool:
        """Save a new version of the biography."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get the latest version number
                cursor.execute('SELECT MAX(version) FROM biography_versions')
                result = cursor.fetchone()
                next_version = (result[0] or 0) + 1
                
                # Insert new version
                cursor.execute('''
                    INSERT INTO biography_versions (version, content, notes)
                    VALUES (?, ?, ?)
                ''', (next_version, content, notes))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving biography: {e}")
            return False

    def get_biography(self, version: Optional[int] = None) -> Optional[Dict]:
        """Get a specific version of the biography or the latest version if no version specified."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if version is None:
                    cursor.execute('SELECT * FROM biography_versions ORDER BY version DESC LIMIT 1')
                else:
                    cursor.execute('SELECT * FROM biography_versions WHERE version = ?', (version,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "version": result[1],
                        "content": result[2],
                        "created_at": result[3],
                        "notes": result[4]
                    }
                return None
        except Exception as e:
            print(f"Error retrieving biography: {e}")
            return None

    def list_biography_versions(self) -> List[Dict]:
        """List all biography versions."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM biography_versions ORDER BY version DESC')
                
                versions = []
                for row in cursor.fetchall():
                    versions.append({
                        "id": row[0],
                        "version": row[1],
                        "content": row[2],
                        "created_at": row[3],
                        "notes": row[4]
                    })
                return versions
        except Exception as e:
            print(f"Error listing biography versions: {e}")
            return []

    def delete_biography(self) -> bool:
        """Delete all biography versions."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM biography_versions')
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting biography: {e}")
            return False

    def save_prompt(self, name: str, content: str, description: str = None) -> bool:
        """Save or update an AI prompt."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                cursor.execute('SELECT id FROM ai_prompts WHERE name = ?', (name,))
                if cursor.fetchone():
                    cursor.execute('''
                        UPDATE ai_prompts 
                        SET content = ?, description = ?, updated_at = ?
                        WHERE name = ?
                    ''', (content, description, now, name))
                else:
                    cursor.execute('''
                        INSERT INTO ai_prompts (name, content, description, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (name, content, description, now, now))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving prompt: {e}")
            return False

    def get_prompt(self, name: str) -> Optional[Dict]:
        """Get an AI prompt by name."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM ai_prompts WHERE name = ?', (name,))
                result = cursor.fetchone()
                if result:
                    return {
                        "id": result[0],
                        "name": result[1],
                        "content": result[2],
                        "description": result[3],
                        "created_at": result[4],
                        "updated_at": result[5]
                    }
                return None
        except Exception as e:
            print(f"Error retrieving prompt: {e}")
            return None

    def list_prompts(self) -> List[Dict]:
        """List all AI prompts."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM ai_prompts ORDER BY name')
                prompts = []
                for row in cursor.fetchall():
                    prompts.append({
                        "id": row[0],
                        "name": row[1],
                        "content": row[2],
                        "description": row[3],
                        "created_at": row[4],
                        "updated_at": row[5]
                    })
                return prompts
        except Exception as e:
            print(f"Error listing prompts: {e}")
            return []

    def delete_prompt(self, name: str) -> bool:
        """Delete an AI prompt."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM ai_prompts WHERE name = ?', (name,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting prompt: {e}")
            return False 