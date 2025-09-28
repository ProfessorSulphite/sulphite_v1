"""
Sulphite Learning Assistant - Database Management Module

This module handles all database operations for the Sulphite system including
session management, conversation memory storage, and data persistence.
It uses SQLite as the backend database and provides comprehensive logging
of all database operations.

Features:
- Session management (create, retrieve, delete sessions)
- Conversation memory storage with sliding window
- Database connection management
- Comprehensive logging of all operations
- Error handling and transaction management

Database Schema:
- sessions: Stores user session information
- memory: Stores conversation history linked to sessions

Author: AI Assistant  
Date: September 28, 2025
Version: 2.0
"""

import sqlite3
from typing import List, Tuple, Optional
from logging_config import get_logger, sulphite_logger

class Database:
    """
    Database management class for Sulphite Learning Assistant.
    
    This class provides all database functionality including session management,
    conversation memory storage, and data persistence. All operations are logged
    in detail to track system behavior and debugging.
    
    Attributes:
        db_name (str): Name of the SQLite database file
        conn (sqlite3.Connection): Database connection object
        logger (logging.Logger): Logger instance for database operations
    
    Example:
        >>> db = Database("test.db")
        >>> session_id = db.create_session("user123")
        >>> db.add_message(session_id, "Hello", "Hi there!")
        >>> history = db.get_memory(session_id)
    """
    
    def __init__(self, db_name: str = "sulphite.db"):
        """
        Initialize the database connection and create necessary tables.
        
        Args:
            db_name (str): Name of the SQLite database file to use
            
        Raises:
            sqlite3.Error: If database connection or table creation fails
        """
        self.logger = get_logger("database")
        
        sulphite_logger.log_function_entry(self.logger, "__init__", db_name=db_name)
        
        self.db_name = db_name
        
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.logger.info(f"Database connection established: {db_name}")
            self.create_tables()
            sulphite_logger.log_function_exit(self.logger, "__init__", "Database initialized successfully")
        except sqlite3.Error as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise

    def create_tables(self) -> None:
        """
        Create the necessary database tables if they don't exist.
        
        Creates two main tables:
        - sessions: For storing session information
        - memory: For storing conversation history
        
        Raises:
            sqlite3.Error: If table creation fails
        """
        sulphite_logger.log_function_entry(self.logger, "create_tables")
        
        try:
            with self.conn:
                # Create sessions table
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create memory table  
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
                
                sulphite_logger.log_database_operation(
                    self.logger, 
                    "CREATE_TABLES", 
                    {"tables": ["sessions", "memory"]}
                )
                
                sulphite_logger.log_function_exit(self.logger, "create_tables", "Tables created successfully")
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to create tables: {e}")
            raise

    def create_session(self, name: str) -> int:
        """
        Create a new session with the given name.
        
        Args:
            name (str): Unique name for the session
            
        Returns:
            int: The ID of the newly created session
            
        Raises:
            sqlite3.IntegrityError: If session name already exists
            sqlite3.Error: If session creation fails
        """
        sulphite_logger.log_function_entry(self.logger, "create_session", name=name)
        
        try:
            with self.conn:
                cursor = self.conn.execute("INSERT INTO sessions (name) VALUES (?)", (name,))
                session_id = cursor.lastrowid
                
                sulphite_logger.log_database_operation(
                    self.logger,
                    "CREATE_SESSION",
                    {"session_name": name, "session_id": session_id}
                )
                
                sulphite_logger.log_function_exit(self.logger, "create_session", session_id)
                return session_id
                
        except sqlite3.IntegrityError as e:
            self.logger.warning(f"Session '{name}' already exists: {e}")
            raise
        except sqlite3.Error as e:
            self.logger.error(f"Failed to create session '{name}': {e}")
            raise

    def get_session(self, name: str) -> Optional[int]:
        """
        Retrieve session ID by session name.
        
        Args:
            name (str): Name of the session to retrieve
            
        Returns:
            Optional[int]: Session ID if found, None otherwise
            
        Raises:
            sqlite3.Error: If database query fails
        """
        sulphite_logger.log_function_entry(self.logger, "get_session", name=name)
        
        try:
            with self.conn:
                cursor = self.conn.execute("SELECT id FROM sessions WHERE name = ?", (name,))
                row = cursor.fetchone()
                session_id = row[0] if row else None
                
                sulphite_logger.log_database_operation(
                    self.logger,
                    "GET_SESSION", 
                    {"session_name": name, "found": session_id is not None}
                )
                
                sulphite_logger.log_function_exit(self.logger, "get_session", session_id)
                return session_id
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get session '{name}': {e}")
            raise

    def add_message(self, session_id: int, user_input: str, model_response: str) -> None:
        """
        Add a conversation message pair to the session's memory.
        
        Args:
            session_id (int): ID of the session to add message to
            user_input (str): The user's input message
            model_response (str): The model's response message
            
        Raises:
            sqlite3.Error: If message insertion fails
        """
        sulphite_logger.log_function_entry(
            self.logger, 
            "add_message", 
            session_id=session_id,
            user_input_length=len(user_input),
            response_length=len(model_response)
        )
        
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO memory (session_id, user_input, model_response) VALUES (?, ?, ?)",
                    (session_id, user_input, model_response)
                )
                
                sulphite_logger.log_database_operation(
                    self.logger,
                    "ADD_MESSAGE",
                    {
                        "session_id": session_id,
                        "user_input_preview": user_input[:50] + "..." if len(user_input) > 50 else user_input,
                        "response_preview": model_response[:50] + "..." if len(model_response) > 50 else model_response
                    }
                )
                
                sulphite_logger.log_function_exit(self.logger, "add_message", "Message added successfully")
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to add message to session {session_id}: {e}")
            raise

    def get_memory(self, session_id: int, limit: int = 5) -> List[Tuple[str, str]]:
        """
        Retrieve conversation memory for a session with sliding window.
        
        Args:
            session_id (int): ID of the session to get memory from
            limit (int): Maximum number of recent messages to retrieve
            
        Returns:
            List[Tuple[str, str]]: List of (user_input, model_response) tuples
                                  in chronological order
            
        Raises:
            sqlite3.Error: If memory retrieval fails
        """
        sulphite_logger.log_function_entry(
            self.logger, 
            "get_memory", 
            session_id=session_id, 
            limit=limit
        )
        
        try:
            with self.conn:
                cursor = self.conn.execute(
                    "SELECT user_input, model_response FROM memory WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                    (session_id, limit)
                )
                
                # Reverse to get chronological order
                memory = cursor.fetchall()[::-1]
                
                sulphite_logger.log_database_operation(
                    self.logger,
                    "GET_MEMORY",
                    {
                        "session_id": session_id,
                        "limit": limit,
                        "messages_retrieved": len(memory)
                    }
                )
                
                sulphite_logger.log_function_exit(self.logger, "get_memory", f"{len(memory)} messages")
                return memory
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get memory for session {session_id}: {e}")
            raise

    def clear_memory(self, session_id: int) -> None:
        """
        Clear all conversation memory for a specific session.
        
        Args:
            session_id (int): ID of the session to clear memory for
            
        Raises:
            sqlite3.Error: If memory clearing fails
        """
        sulphite_logger.log_function_entry(self.logger, "clear_memory", session_id=session_id)
        
        try:
            with self.conn:
                cursor = self.conn.execute("DELETE FROM memory WHERE session_id = ?", (session_id,))
                deleted_count = cursor.rowcount
                
                sulphite_logger.log_database_operation(
                    self.logger,
                    "CLEAR_MEMORY",
                    {"session_id": session_id, "messages_deleted": deleted_count}
                )
                
                sulphite_logger.log_function_exit(self.logger, "clear_memory", f"{deleted_count} messages cleared")
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to clear memory for session {session_id}: {e}")
            raise

    def delete_session(self, session_id: int) -> None:
        """
        Delete a session and all its associated memory.
        
        Args:
            session_id (int): ID of the session to delete
            
        Raises:
            sqlite3.Error: If session deletion fails
        """
        sulphite_logger.log_function_entry(self.logger, "delete_session", session_id=session_id)
        
        try:
            with self.conn:
                # Delete memory first (foreign key constraint)
                memory_cursor = self.conn.execute("DELETE FROM memory WHERE session_id = ?", (session_id,))
                memory_deleted = memory_cursor.rowcount
                
                # Delete session
                session_cursor = self.conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
                session_deleted = session_cursor.rowcount
                
                sulphite_logger.log_database_operation(
                    self.logger,
                    "DELETE_SESSION",
                    {
                        "session_id": session_id,
                        "session_deleted": session_deleted > 0,
                        "messages_deleted": memory_deleted
                    }
                )
                
                sulphite_logger.log_function_exit(
                    self.logger, 
                    "delete_session", 
                    f"Session deleted: {session_deleted > 0}, Messages deleted: {memory_deleted}"
                )
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to delete session {session_id}: {e}")
            raise

    def __del__(self):
        """
        Clean up database connection on object destruction.
        """
        if hasattr(self, 'conn'):
            self.conn.close()
            if hasattr(self, 'logger'):
                self.logger.info("Database connection closed")
