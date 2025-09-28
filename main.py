"""
Sulphite Learning Assistant - Main Application Module

This is the main entry point for the Sulphite Learning Assistant, an intelligent
tutoring system for middle school mathematics. The application provides an
interactive command-line interface that supports adaptive learning through
AI-powered query classification and personalized responses.

Features:
- Interactive command-line interface with intuitive commands
- AI-powered query classification (practical, theoretical, general, irrelevant)
- Adaptive learning responses based on classification results
- Session management with persistent conversation history
- Comprehensive logging of all user interactions and system operations
- Support for multiple concurrent sessions
- Memory management with conversation context

Available Commands:
- /chat <message>: Send a message to the AI tutor
- /show_info: Display current session and system information
- /new [name]: Start a new session (optional name parameter)
- /clear: Clear current session's conversation memory
- /quit: Exit the application
- /help: Show command help

The system automatically classifies each query and adapts its teaching style:
- Practical queries → Real-world applications and problem-solving focus
- Theoretical queries → Conceptual understanding and deep explanations
- General queries → Friendly conversation that guides toward mathematics
- Irrelevant queries → Polite redirection to educational content

Author: AI Assistant
Date: September 28, 2025
Version: 2.0
"""

import sys
from typing import List, Optional
from dotenv import load_dotenv
from database import Database
from services import ChatService
from logging_config import get_logger, sulphite_logger

# Load environment variables
load_dotenv()

class SulphiteApp:
    """
    Main application class for the Sulphite Learning Assistant.
    
    This class manages the application lifecycle, user interface,
    command processing, and coordinates all system components.
    All user interactions and system operations are logged comprehensively.
    
    Attributes:
        db (Database): Database instance for data persistence
        chat_service (ChatService): Chat service for AI interactions
        logger (logging.Logger): Logger for main application events
        running (bool): Flag indicating if application is running
    
    Example:
        >>> app = SulphiteApp()
        >>> app.run()
    """
    
    def __init__(self):
        """
        Initialize the Sulphite application with all required components.
        
        Sets up database connection, chat service, and logging infrastructure.
        Automatically starts a default session for immediate use.
        
        Raises:
            Exception: If initialization of any component fails
        """
        self.logger = get_logger("main")
        
        sulphite_logger.log_function_entry(self.logger, "__init__")
        
        try:
            self.logger.info("Starting Sulphite Learning Assistant v2.0")
            
            # Initialize core components
            self.db = Database()
            self.chat_service = ChatService(self.db)
            self.running = False
            
            # Start default session
            self.chat_service.start_new_session()
            
            self.logger.info("Sulphite application initialized successfully")
            
            sulphite_logger.log_query_processing(
                self.logger,
                "Application Startup",
                "INITIALIZATION_COMPLETE",
                {"database": self.db.db_name, "default_session_started": True}
            )
            
            sulphite_logger.log_function_exit(self.logger, "__init__", "Application ready")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Sulphite application: {e}")
            raise

    def print_help(self) -> None:
        """
        Display help information about available commands.
        
        Shows comprehensive information about all supported commands
        and their usage patterns. Logged for usage analytics.
        """
        sulphite_logger.log_function_entry(self.logger, "print_help")
        
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                    SULPHITE LEARNING ASSISTANT               ║
║                      Available Commands                      ║
╠══════════════════════════════════════════════════════════════╣
║  /chat <message>  - Chat with the AI tutor                   ║
║  /show_info       - Show system information                  ║
║  /new [name]      - Start a new session (optional name)      ║
║  /clear           - Clear current session's memory           ║
║  /quit            - Quit the application                     ║
║  /help            - Show this help message                   ║
╠══════════════════════════════════════════════════════════════╣
║  You can also type messages directly without /chat           ║
║                                                              ║
║ The system automatically adapts to your learning style:      ║
║  • Practical: Real-world applications & problem-solving      ║
║  • Theoretical: Concepts, theories & deep understanding      ║
║  • General: Friendly conversation guiding to mathematics     ║
╚══════════════════════════════════════════════════════════════╝
        """
        
        print(help_text)
        
        self.logger.info("Help information displayed to user")
        
        sulphite_logger.log_query_processing(
            self.logger,
            "Help Request",
            "HELP_DISPLAYED"
        )
        
        sulphite_logger.log_function_exit(self.logger, "print_help", "Help displayed")

    def process_command(self, user_input: str) -> bool:
        """
        Process a user command and execute the appropriate action.
        
        Parses user input to identify commands and their arguments,
        then executes the corresponding functionality. All commands
        and their outcomes are logged in detail.
        
        Args:
            user_input (str): Raw user input string
            
        Returns:
            bool: True to continue running, False to exit application
        """
        sulphite_logger.log_function_entry(
            self.logger, 
            "process_command",
            input_length=len(user_input),
            is_command=user_input.startswith('/')
        )
        
        try:
            if user_input.startswith('/'):
                # Parse command and arguments
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                arg_str = " ".join(args)
                
                self.logger.debug(f"Processing command: {command} with args: {args}")
                
                # Process specific commands
                if command == '/quit':
                    return self._handle_quit_command()
                elif command == '/help':
                    return self._handle_help_command()
                elif command == '/new':
                    return self._handle_new_session_command(arg_str)
                elif command == '/clear':
                    return self._handle_clear_command()
                elif command == '/show_info':
                    return self._handle_show_info_command()
                elif command == '/chat':
                    return self._handle_chat_command(arg_str)
                else:
                    return self._handle_unknown_command(command)
            else:
                # Direct message without command prefix
                return self._handle_direct_message(user_input)
                
        except Exception as e:
            self.logger.error(f"Error processing command '{user_input}': {e}")
            print(f"An error occurred while processing your command: {e}")
            return True  # Continue running despite error

    def _handle_quit_command(self) -> bool:
        """Handle the /quit command to exit the application."""
        sulphite_logger.log_function_entry(self.logger, "_handle_quit_command")
        
        self.logger.info("User initiated application quit")
        print("Goodbye! Thank you for using Sulphite Learning Assistant.")
        
        sulphite_logger.log_query_processing(
            self.logger,
            "/quit",
            "APPLICATION_EXIT"
        )
        
        sulphite_logger.log_function_exit(self.logger, "_handle_quit_command", "Application exiting")
        return False

    def _handle_help_command(self) -> bool:
        """Handle the /help command to show available commands."""
        sulphite_logger.log_function_entry(self.logger, "_handle_help_command")
        
        self.print_help()
        
        sulphite_logger.log_function_exit(self.logger, "_handle_help_command", "Help shown")
        return True

    def _handle_new_session_command(self, session_name: str) -> bool:
        """
        Handle the /new command to start a new session.
        
        Args:
            session_name (str): Name for the new session
        """
        sulphite_logger.log_function_entry(
            self.logger, 
            "_handle_new_session_command",
            session_name=session_name or "default"
        )
        
        try:
            name = session_name if session_name else "default"
            session_id = self.chat_service.start_new_session(name)
            print(f"✓ Started new session: '{name}' (ID: {session_id})")
            
            self.logger.info(f"New session started: '{name}' (ID: {session_id})")
            
            sulphite_logger.log_query_processing(
                self.logger,
                f"/new {name}",
                "NEW_SESSION_STARTED",
                {"session_name": name, "session_id": session_id}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to start new session '{session_name}': {e}")
            print(f"Failed to start new session: {e}")
        
        sulphite_logger.log_function_exit(self.logger, "_handle_new_session_command", "Session command processed")
        return True

    def _handle_clear_command(self) -> bool:
        """Handle the /clear command to clear session memory."""
        sulphite_logger.log_function_entry(self.logger, "_handle_clear_command")
        
        try:
            self.chat_service.clear_current_session_memory()
            print("✓ Current session memory cleared.")
            
            self.logger.info("Session memory cleared by user")
            
            sulphite_logger.log_query_processing(
                self.logger,
                "/clear",
                "MEMORY_CLEARED_BY_USER"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to clear session memory: {e}")
            print(f"Failed to clear session memory: {e}")
        
        sulphite_logger.log_function_exit(self.logger, "_handle_clear_command", "Clear command processed")
        return True

    def _handle_show_info_command(self) -> bool:
        """Handle the /show_info command to display system information."""
        sulphite_logger.log_function_entry(self.logger, "_handle_show_info_command")
        
        try:
            info = self.chat_service.show_info()
            print(f"📊 System Information:\n{info}")
            
            self.logger.info("System information displayed to user")
            
            sulphite_logger.log_query_processing(
                self.logger,
                "/show_info",
                "SYSTEM_INFO_DISPLAYED"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to show system info: {e}")
            print(f"Failed to retrieve system information: {e}")
        
        sulphite_logger.log_function_exit(self.logger, "_handle_show_info_command", "Info command processed")
        return True

    def _handle_chat_command(self, message: str) -> bool:
        """
        Handle the /chat command to send a message to the AI.
        
        Args:
            message (str): The message to send to the AI
        """
        sulphite_logger.log_function_entry(
            self.logger,
            "_handle_chat_command",
            message_length=len(message)
        )
        
        if not message:
            print("⚠️  Please provide a message for the chat.")
            self.logger.warning("Empty chat command received")
            return True
        
        return self._process_ai_interaction(message)

    def _handle_direct_message(self, message: str) -> bool:
        """
        Handle direct messages (without command prefix).
        
        Args:
            message (str): The direct message to process
        """
        sulphite_logger.log_function_entry(
            self.logger,
            "_handle_direct_message", 
            message_length=len(message)
        )
        
        return self._process_ai_interaction(message)

    def _handle_unknown_command(self, command: str) -> bool:
        """
        Handle unknown commands by showing an error and help.
        
        Args:
            command (str): The unknown command
        """
        sulphite_logger.log_function_entry(self.logger, "_handle_unknown_command", command=command)
        
        print(f"❌ Unknown command: {command}")
        print("💡 Type /help to see available commands.")
        
        self.logger.warning(f"Unknown command received: {command}")
        
        sulphite_logger.log_query_processing(
            self.logger,
            command,
            "UNKNOWN_COMMAND",
            {"command": command}
        )
        
        sulphite_logger.log_function_exit(self.logger, "_handle_unknown_command", "Unknown command handled")
        return True

    def _process_ai_interaction(self, message: str) -> bool:
        """
        Process a message through the AI system and display the response.
        
        Args:
            message (str): User message to process
            
        Returns:
            bool: True to continue running
        """
        sulphite_logger.log_function_entry(
            self.logger,
            "_process_ai_interaction",
            message_length=len(message),
            message_preview=message[:50]
        )
        
        try:
            # Log the start of AI interaction
            sulphite_logger.log_query_processing(
                self.logger,
                message,
                "AI_INTERACTION_START"
            )
            
            # Get AI response through chat service (includes classification)
            response = self.chat_service.call_model(message)
            
            # Display response to user
            print(f"\n🤖 Assistant: {response}\n")
            
            self.logger.info(f"AI interaction completed successfully (response: {len(response)} chars)")
            
            sulphite_logger.log_query_processing(
                self.logger,
                message,
                "AI_INTERACTION_COMPLETE",
                {"response_length": len(response)}
            )
            
            sulphite_logger.log_function_exit(self.logger, "_process_ai_interaction", "Interaction successful")
            return True
            
        except Exception as e:
            self.logger.error(f"AI interaction failed for message '{message[:50]}...': {e}")
            print(f"❌ An error occurred while processing your message: {e}")
            
            sulphite_logger.log_query_processing(
                self.logger,
                message,
                "AI_INTERACTION_FAILED",
                {"error": str(e)}
            )
            
            return True  # Continue running despite error

    def run(self) -> None:
        """
        Main application loop that handles user input and coordinates system operations.
        
        Provides an interactive command-line interface with comprehensive error handling
        and logging of all user interactions. Continues running until user exits
        or an unrecoverable error occurs.
        """
        sulphite_logger.log_function_entry(self.logger, "run")
        
        self.running = True
        
        # Display welcome message
        print("""
╔══════════════════════════════════════════════════════════════╗
║              🎓 SULPHITE LEARNING ASSISTANT 🎓               ║
║                                                              ║
║        Your Adaptive AI Tutor for Middle School Math         ║
║                                                              ║
║              Type /help for available commands               ║
║          or just start chatting with your questions!         ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        self.logger.info("Application started, entering main loop")
        
        sulphite_logger.log_query_processing(
            self.logger,
            "Application Start",
            "MAIN_LOOP_STARTED"
        )
        
        try:
            while self.running:
                try:
                    # Get user input
                    user_input = input("💭 > ").strip()
                    
                    # Skip empty input
                    if not user_input:
                        continue
                    
                    # Process the input and get continuation flag
                    self.running = self.process_command(user_input)
                    
                except KeyboardInterrupt:
                    # Handle Ctrl+C gracefully
                    self.logger.info("Application interrupted by user (Ctrl+C)")
                    print("\n\n👋 Goodbye! Thank you for using Sulphite Learning Assistant.")
                    break
                    
                except EOFError:
                    # Handle Ctrl+D gracefully
                    self.logger.info("Application terminated by EOF")
                    print("\n\n👋 Goodbye! Thank you for using Sulphite Learning Assistant.")
                    break
                    
        except Exception as e:
            self.logger.error(f"Unhandled error in main loop: {e}")
            print(f"\n❌ An unexpected error occurred: {e}")
            print("The application will now exit.")
        
        finally:
            self.logger.info("Application shutting down")
            
            sulphite_logger.log_query_processing(
                self.logger,
                "Application Shutdown",
                "MAIN_LOOP_ENDED"
            )
            
            sulphite_logger.log_function_exit(self.logger, "run", "Application terminated")


def main() -> None:
    """
    Main entry point for the Sulphite Learning Assistant application.
    
    Initializes and runs the main application loop with comprehensive
    error handling and logging setup.
    
    Exit Codes:
        0: Normal termination
        1: Initialization error
        2: Runtime error
    """
    logger = get_logger("startup")
    
    sulphite_logger.log_function_entry(logger, "main")
    
    try:
        # Initialize and run the application
        app = SulphiteApp()
        app.run()
        
        logger.info("Application terminated normally")
        sulphite_logger.log_function_exit(logger, "main", "Normal exit")
        sys.exit(0)
        
    except KeyboardInterrupt:
        logger.info("Application interrupted during startup")
        print("\n👋 Goodbye!")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error during application startup: {e}")
        print(f"❌ Failed to start Sulphite Learning Assistant: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()