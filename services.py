"""
Sulphite Learning Assistant - Chat Service Module

This module provides the core chat service functionality for the Sulphite system.
It integrates AI model interactions, query classification, session management,
and conversation memory. The service adapts its responses based on the classified
learning style (practical vs theoretical) and maintains context across conversations.

Features:
- Intelligent query classification and adaptive responses
- Session management with persistent conversation history
- Integration with Google Gemini AI models
- Comprehensive logging of all chat operations
- Context-aware responses based on conversation history
- Support for different learning prompts based on classification

Learning Adaptation:
- Practical queries: Focus on real-world applications and problem-solving
- Theoretical queries: Emphasize concepts, theories, and deep understanding
- General queries: Engage in friendly conversation while guiding to mathematics
- Irrelevant queries: Politely redirect to educational topics

Author: AI Assistant
Date: September 28, 2025
Version: 2.0
"""

import os
from typing import Dict, Any, Optional, Tuple
from database import Database
from classification import Classifier
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from logging_config import get_logger, sulphite_logger
import config


class ChatService:
    """
    Main chat service for the Sulphite Learning Assistant.
    
    This class orchestrates the entire conversation flow including query classification,
    appropriate response generation based on learning style, session management,
    and conversation memory. All operations are comprehensively logged.
    
    Attributes:
        db (Database): Database instance for session and memory management
        classifier (Classifier): AI classifier for query categorization
        session_id (Optional[int]): Current active session ID
        gemini_api_key (str): API key for Google Gemini AI
        model (ChatGoogleGenerativeAI): AI model for generating responses
        logger (logging.Logger): Logger for chat service operations
    
    Example:
        >>> db = Database()
        >>> chat_service = ChatService(db)
        >>> session_id = chat_service.start_new_session("user123")
        >>> response = chat_service.call_model("How do I solve equations?")
    """
    
    def __init__(self, db: Database):
        """
        Initialize the chat service with database and AI components.
        
        Args:
            db (Database): Database instance for data persistence
            
        Raises:
            ValueError: If GEMINI_API_KEY environment variable is not set
            Exception: If classifier or AI model initialization fails
        """
        self.logger = get_logger("chat_service")
        
        sulphite_logger.log_function_entry(self.logger, "__init__", db_name=db.db_name)
        
        try:
            self.db = db
            self.classifier = Classifier()
            self.session_id = None
            
            # Initialize Gemini AI
            self.gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set.")
            
            self.model = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash", 
                google_api_key=self.gemini_api_key
            )
            
            self.logger.info("Chat service initialized successfully with Gemini 2.0 Flash model")
            sulphite_logger.log_function_exit(self.logger, "__init__", "ChatService initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize chat service: {e}")
            raise

    def start_new_session(self, name: str = "default") -> int:
        """
        Start a new chat session or retrieve an existing one.
        
        Args:
            name (str): Name for the session (defaults to "default")
            
        Returns:
            int: The session ID of the new or existing session
            
        Raises:
            Exception: If session creation or retrieval fails
        """
        sulphite_logger.log_function_entry(self.logger, "start_new_session", session_name=name)
        
        try:
            # Check if session already exists
            session_id = self.db.get_session(name)
            if not session_id:
                # Create new session
                session_id = self.db.create_session(name)
                self.logger.info(f"Created new session: {name} (ID: {session_id})")
            else:
                self.logger.info(f"Retrieved existing session: {name} (ID: {session_id})")
            
            self.session_id = session_id
            
            sulphite_logger.log_query_processing(
                self.logger,
                f"Session: {name}",
                "SESSION_STARTED",
                {"session_id": session_id, "session_name": name}
            )
            
            sulphite_logger.log_function_exit(self.logger, "start_new_session", session_id)
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to start session '{name}': {e}")
            raise

    def call_model(self, prompt: str) -> str:
        """
        Process a user query through classification and generate an adaptive response.
        
        This is the main method that orchestrates the entire conversation flow:
        1. Validates active session
        2. Classifies the user query
        3. Retrieves conversation context
        4. Selects appropriate system prompt based on classification
        5. Generates AI response
        6. Stores conversation in memory
        7. Returns the response
        
        Args:
            prompt (str): User's input/query
            
        Returns:
            str: AI-generated response adapted to the query classification
            
        Raises:
            Exception: If no active session exists or processing fails
        """
        sulphite_logger.log_function_entry(
            self.logger, 
            "call_model",
            prompt_length=len(prompt),
            session_id=self.session_id
        )
        
        if not self.session_id:
            raise Exception("No active session. Start a new session first.")
        
        # Log query processing start
        sulphite_logger.log_query_processing(
            self.logger,
            prompt,
            "QUERY_RECEIVED",
            {"session_id": self.session_id}
        )
        
        try:
            # Step 1: Classify the user query
            classification_result = self._classify_query(prompt)
            
            # Step 2: Get conversation memory for context
            memory = self._get_conversation_context()
            
            # Step 3: Select appropriate system prompt based on classification
            system_prompt = self._select_system_prompt(classification_result)
            
            # Step 4: Build complete prompt with context
            full_prompt = self._build_contextual_prompt(prompt, memory, system_prompt)
            
            # Step 5: Get AI response
            response = self._generate_ai_response(full_prompt, prompt)
            
            # Step 6: Store conversation in memory
            self.db.add_message(self.session_id, prompt, response)
            
            sulphite_logger.log_query_processing(
                self.logger,
                prompt,
                "QUERY_COMPLETED",
                {
                    "response_length": len(response),
                    "classification": classification_result.get('classification', 'unknown')
                }
            )
            
            sulphite_logger.log_function_exit(self.logger, "call_model", f"Response generated ({len(response)} chars)")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to process query '{prompt[:50]}...': {e}")
            raise

    def _classify_query(self, query: str) -> Dict[str, Any]:
        """
        Classify the user query using the AI classifier.
        
        Args:
            query (str): User's query to classify
            
        Returns:
            Dict[str, Any]: Classification result with category and topics
        """
        sulphite_logger.log_function_entry(self.logger, "_classify_query", query_preview=query[:50])
        
        sulphite_logger.log_query_processing(
            self.logger,
            query,
            "CLASSIFICATION_START"
        )
        
        try:
            classification_result = self.classifier.classify(query)
            
            sulphite_logger.log_query_processing(
                self.logger,
                query,
                "CLASSIFICATION_COMPLETE",
                classification_result
            )
            
            sulphite_logger.log_function_exit(self.logger, "_classify_query", classification_result)
            return classification_result
            
        except Exception as e:
            self.logger.error(f"Query classification failed: {e}")
            # Return default classification on error
            default_result = {"classification": "general", "main_topic": None, "sub_topic": None}
            sulphite_logger.log_function_exit(self.logger, "_classify_query", default_result)
            return default_result

    def _get_conversation_context(self) -> str:
        """
        Retrieve and format conversation history for context.
        
        Returns:
            str: Formatted conversation history string
        """
        sulphite_logger.log_function_entry(self.logger, "_get_conversation_context", session_id=self.session_id)
        
        try:
            memory = self.db.get_memory(self.session_id)
            convo_str = "\n".join([f"User: {u}\nAssistant: {r}" for u, r in memory])
            
            self.logger.debug(f"Retrieved {len(memory)} conversation exchanges for context")
            
            sulphite_logger.log_function_exit(
                self.logger, 
                "_get_conversation_context", 
                f"{len(memory)} exchanges, {len(convo_str)} chars"
            )
            return convo_str
            
        except Exception as e:
            self.logger.error(f"Failed to get conversation context: {e}")
            return ""

    def _select_system_prompt(self, classification_result: Dict[str, Any]) -> str:
        """
        Select the appropriate system prompt based on query classification.
        
        Args:
            classification_result (Dict[str, Any]): Result from query classification
            
        Returns:
            str: Selected system prompt for the AI model
        """
        classification = classification_result.get('classification', 'general')
        
        sulphite_logger.log_function_entry(
            self.logger, 
            "_select_system_prompt", 
            classification=classification
        )
        
        # Map classification to system prompt
        prompt_mapping = {
            'practical': 'practical_learning_prompt',
            'theoretical': 'theoretical_learning_prompt', 
            'general': 'general_chitchat_prompt',
            'irrelevant': 'irrelevant_response_prompt'
        }
        
        prompt_key = prompt_mapping.get(classification, 'default_system_prompt')
        selected_prompt = config.prompts.get(prompt_key, config.prompts['default_system_prompt'])
        
        self.logger.info(f"Selected {prompt_key} for classification: {classification}")
        
        sulphite_logger.log_query_processing(
            self.logger,
            f"Classification: {classification}",
            "PROMPT_SELECTED",
            {"prompt_key": prompt_key}
        )
        
        sulphite_logger.log_function_exit(self.logger, "_select_system_prompt", prompt_key)
        return selected_prompt

    def _build_contextual_prompt(self, current_query: str, memory: str, system_prompt: str) -> Tuple[str, str]:
        """
        Build the complete prompt with conversation context.
        
        Args:
            current_query (str): Current user query
            memory (str): Formatted conversation history
            system_prompt (str): Selected system prompt
            
        Returns:
            Tuple[str, str]: (system_prompt, user_prompt_with_context)
        """
        sulphite_logger.log_function_entry(
            self.logger,
            "_build_contextual_prompt",
            query_length=len(current_query),
            memory_length=len(memory),
            has_context=bool(memory)
        )
        
        if memory:
            contextualized_query = f"Here is the conversation history:\n{memory}\n\nNow respond to: {current_query}"
            self.logger.debug("Built contextualized prompt with conversation history")
        else:
            contextualized_query = current_query
            self.logger.debug("Built prompt without conversation history (new session)")
        
        result = (system_prompt, contextualized_query)
        sulphite_logger.log_function_exit(
            self.logger, 
            "_build_contextual_prompt", 
            f"System prompt: {len(system_prompt)} chars, User prompt: {len(contextualized_query)} chars"
        )
        return result

    def _generate_ai_response(self, prompt_parts: Tuple[str, str], original_query: str) -> str:
        """
        Generate AI response using the Gemini model.
        
        Args:
            prompt_parts (Tuple[str, str]): (system_prompt, user_prompt)
            original_query (str): Original user query for logging
            
        Returns:
            str: Generated AI response
        """
        system_prompt, user_prompt = prompt_parts
        
        sulphite_logger.log_function_entry(
            self.logger,
            "_generate_ai_response",
            original_query_preview=original_query[:50]
        )
        
        sulphite_logger.log_query_processing(
            self.logger,
            original_query,
            "AI_GENERATION_START",
            {"model": "gemini-2.0-flash"}
        )
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.model.invoke(messages)
            response_text = response.content
            
            self.logger.info(f"Generated AI response ({len(response_text)} characters)")
            
            sulphite_logger.log_query_processing(
                self.logger,
                original_query,
                "AI_GENERATION_COMPLETE",
                {"response_length": len(response_text)}
            )
            
            sulphite_logger.log_function_exit(self.logger, "_generate_ai_response", f"{len(response_text)} chars")
            return response_text
            
        except Exception as e:
            self.logger.error(f"AI response generation failed: {e}")
            raise

    def clear_current_session_memory(self) -> None:
        """
        Clear conversation memory for the current session.
        
        Raises:
            Exception: If no active session or clearing fails
        """
        sulphite_logger.log_function_entry(self.logger, "clear_current_session_memory", session_id=self.session_id)
        
        if not self.session_id:
            raise Exception("No active session to clear memory from.")
        
        try:
            self.db.clear_memory(self.session_id)
            self.logger.info(f"Cleared memory for session {self.session_id}")
            
            sulphite_logger.log_query_processing(
                self.logger,
                f"Session {self.session_id}",
                "MEMORY_CLEARED"
            )
            
            sulphite_logger.log_function_exit(self.logger, "clear_current_session_memory", "Memory cleared")
            
        except Exception as e:
            self.logger.error(f"Failed to clear session memory: {e}")
            raise

    def show_info(self) -> str:
        """
        Get information about the current chat service state.
        
        Returns:
            str: Formatted information string about current session and database
        """
        sulphite_logger.log_function_entry(self.logger, "show_info", session_id=self.session_id)
        
        info = f"Current Session ID: {self.session_id}\nDatabase: {self.db.db_name}"
        
        self.logger.debug(f"Providing system info: Session {self.session_id}, DB {self.db.db_name}")
        
        sulphite_logger.log_function_exit(self.logger, "show_info", "Info retrieved")
        return info
