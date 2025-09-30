# professorsulphite/sulphite_v1/sulphite_v1-e0f21b0d541b71aa42e22e2435a9b0b9f2caa2e4/database.py
import sqlite3
from typing import List, Tuple, Optional
from logging_config import get_logger, sulphite_logger

class Database:
    def __init__(self, db_name: str = "sulphite.db"):
        self.logger = get_logger("database")
        sulphite_logger.log_function_entry(self.logger, "__init__", db_name=db_name)
        self.db_name = db_name
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.logger.info(f"Database connection established: {db_name}")
            self.create_tables()
        except sqlite3.Error as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise

    def create_tables(self) -> None:
        sulphite_logger.log_function_entry(self.logger, "create_tables")
        try:
            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER NOT NULL,
                        user_input TEXT NOT NULL,
                        model_response TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES sessions (id)
                    )
                """)
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS permanent_memory (
                        id INTEGER PRIMARY KEY CHECK (id = 1),
                        notes TEXT NOT NULL
                    )
                """)
        except sqlite3.Error as e:
            self.logger.error(f"Failed to create tables: {e}")
            raise

    def create_session(self, name: str) -> int:
        try:
            with self.conn:
                cursor = self.conn.execute("INSERT INTO sessions (name) VALUES (?)", (name,))
                return cursor.lastrowid
        except sqlite3.Error as e:
            self.logger.error(f"Failed to create session '{name}': {e}")
            raise

    def get_session(self, name: str) -> Optional[int]:
        try:
            with self.conn:
                cursor = self.conn.execute("SELECT id FROM sessions WHERE name = ?", (name,))
                row = cursor.fetchone()
                return row[0] if row else None
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get session '{name}': {e}")
            raise

    def add_message(self, session_id: int, user_input: str, model_response: str) -> None:
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO memory (session_id, user_input, model_response) VALUES (?, ?, ?)",
                    (session_id, user_input, model_response)
                )
        except sqlite3.Error as e:
            self.logger.error(f"Failed to add message to session {session_id}: {e}")
            raise

    def get_memory(self, session_id: int, limit: int = 5) -> List[Tuple[str, str]]:
        try:
            with self.conn:
                cursor = self.conn.execute(
                    "SELECT user_input, model_response FROM memory WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                    (session_id, limit)
                )
                return cursor.fetchall()[::-1]
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get memory for session {session_id}: {e}")
            raise

    def clear_memory(self, session_id: int) -> None:
        try:
            with self.conn:
                self.conn.execute("DELETE FROM memory WHERE session_id = ?", (session_id,))
        except sqlite3.Error as e:
            self.logger.error(f"Failed to clear memory for session {session_id}: {e}")
            raise
    
    def get_permanent_memory(self) -> Optional[str]:
        try:
            with self.conn:
                cursor = self.conn.execute("SELECT notes FROM permanent_memory WHERE id = 1")
                row = cursor.fetchone()
                return row[0] if row else None
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get permanent memory: {e}")
            return None

    def update_permanent_memory(self, notes: str) -> None:
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT OR REPLACE INTO permanent_memory (id, notes) VALUES (1, ?)", (notes,)
                )
                self.logger.info("Permanent memory updated.")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to update permanent memory: {e}")
            raise