# professorsulphite/sulphite_v1/sulphite_v1-e0f21b0d541b71aa42e22e2435a9b0b9f2caa2e4/main.py
import sys
from dotenv import load_dotenv
from database import Database
from chat_manager import ChatManager
from logging_config import get_logger
from state_manager import StateManager

load_dotenv()

class SulphiteApp:
    def __init__(self):
        self.logger = get_logger("main")
        try:
            self.db = Database()
            self.state = StateManager(self.db)
            self.chat_manager = ChatManager(self.db, self.state)
            self.running = True
            self.logger.info(f"Sulphite application initialized successfully on session {self.state.get_session_id()}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Sulphite application: {e}")
            raise

    def print_help(self) -> None:
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                    SULPHITE LEARNING ASSISTANT               ║
╠══════════════════════════════════════════════════════════════╣
║  /lang <mode>     - Set language ('english', 'urdu', 'auto') ║
║  /addnote <text>  - Add a permanent note about the user      ║
║  /new [name]      - Start a new session (optional name)      ║
║  /clear           - Clear current session's memory           ║
║  /quit            - Quit the application                     ║
║  /help            - Show this help message                   ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(help_text)

    def process_command(self, user_input: str) -> bool:
        try:
            if user_input.startswith('/'):
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:]
                arg_str = " ".join(args)
                
                if command == '/quit': return False
                elif command == '/help': self.print_help()
                elif command == '/lang': self._handle_lang_command(args)
                elif command == '/addnote': self._handle_addnote_command(arg_str)
                elif command == '/new': self._handle_new_session_command(arg_str)
                elif command == '/clear': self._handle_clear_command()
                else: print(f"❌ Unknown command: {command}. Type /help for commands.")
            else:
                self._process_ai_interaction(user_input)
            return True
        except Exception as e:
            self.logger.error(f"Error processing command '{user_input}': {e}")
            print(f"An error occurred: {e}")
            return True

    def _handle_lang_command(self, args: list):
        if not args or args[0].lower() not in ["english", "urdu", "auto"]:
            print("⚠️ Usage: /lang <english|urdu|auto>")
            return
        
        mode = args[0].lower()
        self.state.set_language_mode(mode)
        new_session_name = f"session_{mode}_{self.state.get_session_id() + 1}"
        self.state.new_session(new_session_name)
        self.chat_manager.initialize_session_memory()
        print(f"✓ Language mode set to: {mode}. Started a new session.")

    def _handle_addnote_command(self, note_text: str):
        if not note_text:
            print("⚠️ Usage: /addnote <your note here>")
            return
        if len(note_text) > 300:
            print("⚠️ Note too long (max 300 words).")
            return
        self.chat_manager.summarize_and_save_note(note_text)
        print("✓ Permanent memory updated.")

    def _handle_new_session_command(self, session_name: str):
        name = session_name if session_name else f"session_{self.state.get_session_id() + 1}"
        self.state.new_session(name)
        self.chat_manager.initialize_session_memory()
        print(f"✓ Started new session: '{name}' (ID: {self.state.get_session_id()})")

    def _handle_clear_command(self):
        self.db.clear_memory(self.state.get_session_id())
        self.chat_manager.initialize_session_memory()
        print("✓ Current session memory cleared.")

    def _process_ai_interaction(self, message: str):
        self.state.set_current_prompt(message)
        response = self.chat_manager.call_model()
        print(f"\n🤖 Assistant: {response}\n")

    def run(self):
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║              🎓 SULPHITE LEARNING ASSISTANT 🎓               ║")
        print("║        Your Adaptive AI Tutor for Middle School Math         ║")
        print("║              Type /help for available commands               ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        
        while self.running:
            try:
                user_input = input("💭 > ").strip()
                if not user_input: continue
                self.running = self.process_command(user_input)
            except (KeyboardInterrupt, EOFError):
                self.running = False
        print("\n👋 Goodbye!")

def main():
    try:
        app = SulphiteApp()
        app.run()
    except Exception as e:
        print(f"❌ A fatal error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()