"""
Sulphite Learning Assistant - Logging Configuration Module

This module provides centralized logging configuration for the entire Sulphite system.
It tracks query processing, classification results, database operations, model interactions,
and detailed execution flow including file names, function names, and line numbers.

Features:
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Detailed formatting with timestamps, file/function/line information
- Separate loggers for different components (database, classification, chat, main)
- File and console output options
- Query processing flow tracking

Author: AI Assistant
Date: September 28, 2025
Version: 1.0
"""

import logging
import inspect
import os
from datetime import datetime
from typing import Any, Dict, Optional

class SulphiteLogger:
    """
    Centralized logging system for Sulphite Learning Assistant.
    
    This class provides detailed logging capabilities that track the execution flow
    across all components of the system, including file names, function names,
    line numbers, and detailed processing information.
    
    Attributes:
        log_dir (str): Directory where log files are stored
        log_file (str): Main log file path
        loggers (Dict): Dictionary of component-specific loggers
    """
    
    def __init__(self, log_dir: str = "logs", log_level: int = logging.INFO):
        """
        Initialize the Sulphite logging system.
        
        Args:
            log_dir (str): Directory to store log files
            log_level (int): Default logging level
        """
        self.log_dir = log_dir
        self.log_level = log_level
        self.log_file = os.path.join(log_dir, f"sulphite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        self.loggers = {}
        
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Setup logging configuration
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """
        Configure the logging system with formatters and handlers.
        
        Sets up both file and console logging with detailed formatting
        that includes caller information (file, function, line number).
        """
        # Create custom formatter that includes caller information
        detailed_formatter = logging.Formatter(
            fmt='%(asctime)s | %(name)s | %(levelname)-8s | %(filename)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Create console formatter (less verbose for console output)
        console_formatter = logging.Formatter(
            fmt='%(asctime)s | %(name)-12s | %(levelname)-5s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get or create a logger for a specific component.
        
        Args:
            name (str): Name of the component (e.g., 'database', 'classification', 'chat')
        
        Returns:
            logging.Logger: Configured logger for the component
        """
        if name not in self.loggers:
            logger = logging.getLogger(f"sulphite.{name}")
            logger.setLevel(self.log_level)
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def log_function_entry(self, logger: logging.Logger, function_name: str, **kwargs) -> None:
        """
        Log function entry with parameters.
        
        Args:
            logger (logging.Logger): Logger instance to use
            function_name (str): Name of the function being entered
            **kwargs: Function parameters to log
        """
        caller_frame = inspect.currentframe().f_back
        filename = os.path.basename(caller_frame.f_code.co_filename)
        line_number = caller_frame.f_lineno
        
        params = ", ".join([f"{k}={v}" for k, v in kwargs.items() if not k.startswith('_')])
        logger.debug(f"ENTRY: {filename}:{function_name}:{line_number} | Parameters: {params}")
    
    def log_function_exit(self, logger: logging.Logger, function_name: str, result: Any = None) -> None:
        """
        Log function exit with return value.
        
        Args:
            logger (logging.Logger): Logger instance to use
            function_name (str): Name of the function being exited
            result (Any): Return value of the function
        """
        caller_frame = inspect.currentframe().f_back
        filename = os.path.basename(caller_frame.f_code.co_filename)
        line_number = caller_frame.f_lineno
        
        result_str = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
        logger.debug(f"EXIT: {filename}:{function_name}:{line_number} | Result: {result_str}")
    
    def log_query_processing(self, logger: logging.Logger, query: str, stage: str, details: Dict[str, Any] = None) -> None:
        """
        Log query processing stages with detailed information.
        
        Args:
            logger (logging.Logger): Logger instance to use
            query (str): The user query being processed
            stage (str): Current processing stage
            details (Dict): Additional details about the processing stage
        """
        caller_frame = inspect.currentframe().f_back
        filename = os.path.basename(caller_frame.f_code.co_filename)
        line_number = caller_frame.f_lineno
        
        query_preview = query[:100] + "..." if len(query) > 100 else query
        details_str = f" | Details: {details}" if details else ""
        
        logger.info(f"QUERY_PROCESSING: {filename}:{line_number} | Stage: {stage} | Query: '{query_preview}'{details_str}")
    
    def log_classification_result(self, logger: logging.Logger, query: str, result: Dict[str, Any]) -> None:
        """
        Log classification results in detail.
        
        Args:
            logger (logging.Logger): Logger instance to use
            query (str): The classified query
            result (Dict): Classification result dictionary
        """
        caller_frame = inspect.currentframe().f_back
        filename = os.path.basename(caller_frame.f_code.co_filename)
        line_number = caller_frame.f_lineno
        
        query_preview = query[:50] + "..." if len(query) > 50 else query
        
        logger.info(f"CLASSIFICATION: {filename}:{line_number} | Query: '{query_preview}' | Result: {result}")
    
    def log_database_operation(self, logger: logging.Logger, operation: str, details: Dict[str, Any] = None) -> None:
        """
        Log database operations with details.
        
        Args:
            logger (logging.Logger): Logger instance to use
            operation (str): Type of database operation
            details (Dict): Operation details
        """
        caller_frame = inspect.currentframe().f_back
        filename = os.path.basename(caller_frame.f_code.co_filename)
        line_number = caller_frame.f_lineno
        
        details_str = f" | Details: {details}" if details else ""
        logger.info(f"DB_OPERATION: {filename}:{line_number} | Operation: {operation}{details_str}")

# Global logger instance
sulphite_logger = SulphiteLogger()

def get_logger(component_name: str) -> logging.Logger:
    """
    Convenience function to get a logger for a specific component.
    
    Args:
        component_name (str): Name of the component
    
    Returns:
        logging.Logger: Configured logger instance
    """
    return sulphite_logger.get_logger(component_name)