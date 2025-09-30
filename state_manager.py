# professorsulphite/sulphite_v1/sulphite_v1-e0f21b0d541b71aa42e22e2435a9b0b9f2caa2e4/state_manager.py
"""
Manages the application's state, including session, language, and permanent memory.
"""
from database import Database

class StateManager:
    def __init__(self, db: Database):
        self.db = db
        self.session_id: int = 1
        self.language_mode: str = "auto"
        self.permanent_memory: str = ""
        self.current_prompt: str = ""
        self.load_permanent_memory()

    def set_language_mode(self, mode: str):
        self.language_mode = mode.lower()

    def get_language_mode(self) -> str:
        return self.language_mode

    def get_session_id(self) -> int:
        return self.session_id

    def new_session(self, name: str) -> int:
        # Check if a session with this name already exists to avoid duplicates
        session_id = self.db.get_session(name)
        if session_id:
            self.session_id = session_id
        else:
            self.session_id = self.db.create_session(name)
        return self.session_id

    def load_permanent_memory(self):
        memory = self.db.get_permanent_memory()
        if memory:
            self.permanent_memory = memory
        else:
            default_note = "This user is new. Pay attention to their learning style and preferences."
            self.db.update_permanent_memory(default_note)
            self.permanent_memory = default_note

    def get_permanent_memory(self) -> str:
        return self.permanent_memory

    def update_permanent_memory(self, new_notes: str):
        self.permanent_memory = new_notes
        self.db.update_permanent_memory(new_notes)
        
    def set_current_prompt(self, prompt: str):
        self.current_prompt = prompt

    def get_current_prompt(self) -> str:
        return self.current_prompt