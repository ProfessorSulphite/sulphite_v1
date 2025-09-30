# professorsulphite/sulphite_v1/sulphite_v1-e0f21b0d541b71aa42e22e2435a9b0b9f2caa2e4/chat_manager.py
import os
from typing import Dict, List
from database import Database
from classification import Classifier
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from logging_config import get_logger
import config
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from state_manager import StateManager
from response_handler import ResponseHandler

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

class ChatManager:
    def __init__(self, db: Database, state: StateManager):
        self.logger = get_logger("chat_manager")
        self.db = db
        self.state = state
        self.classifier = Classifier()
        
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        
        self.model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=gemini_api_key)
        self.response_handler = ResponseHandler(self.model)
        
        self.session_memory_texts: List[str] = []
        self.memory_index: faiss.Index | None = None
        self.initialize_session_memory()

    def initialize_session_memory(self):
        self.session_memory_texts = []
        embedding_dim = embedding_model.get_sentence_embedding_dimension()
        self.memory_index = faiss.IndexFlatL2(embedding_dim)
        
        past_messages = self.db.get_memory(self.state.get_session_id(), limit=100)
        for user_input, model_response in past_messages:
            self.session_memory_texts.append(f"User asked: {user_input}")
            self.session_memory_texts.append(f"AI answered: {model_response}")

        if self.session_memory_texts:
            embeddings = embedding_model.encode(self.session_memory_texts)
            self.memory_index.add(np.array(embeddings, dtype=np.float32))
        self.logger.info(f"Initialized semantic memory for session {self.state.get_session_id()} with {len(self.session_memory_texts)} entries.")

    def _add_to_semantic_memory(self, user_input: str, model_response: str):
        new_texts = [f"User asked: {user_input}", f"AI answered: {model_response}"]
        self.session_memory_texts.extend(new_texts)
        new_embeddings = embedding_model.encode(new_texts)
        if self.memory_index:
            self.memory_index.add(np.array(new_embeddings, dtype=np.float32))

    def _get_conversation_context(self, query: str, k: int = 3) -> str:
        if not self.session_memory_texts or not self.memory_index or self.memory_index.ntotal == 0:
            return "No conversation history yet."
        query_embedding = embedding_model.encode([query])
        _, I = self.memory_index.search(np.array(query_embedding, dtype=np.float32), k)
        relevant_snippets = [self.session_memory_texts[i] for i in I[0]]
        return "\n".join(reversed(relevant_snippets))

    def _detect_language(self, query: str) -> str:
        try:
            prompt = config.get_prompt("language_detection_prompt").format(user_input=query)
            response = self.model.invoke([HumanMessage(content=prompt)])
            return response.content.strip().lower()
        except Exception:
            return "other"

    def _get_query_type(self, user_input: str) -> str:
        last_exchange = self.db.get_memory(self.state.get_session_id(), limit=1)
        if not last_exchange or "?" not in last_exchange[0][1]:
            return "new_question"
        
        _, last_ai_message = last_exchange[0]
        prompt = config.get_prompt("query_type_prompt").format(last_ai_message=last_ai_message, user_input=user_input)
        response = self.model.invoke([HumanMessage(content=prompt)])
        return response.content.strip().lower()

    def call_model(self) -> str:
        prompt = self.state.get_current_prompt()
        language_mode = self.state.get_language_mode()
        
        if "who are you" in prompt.lower() or "what is your name" in prompt.lower():
            return self.response_handler.answer_identity_question()

        if language_mode != "auto":
            detected_lang = self._detect_language(prompt)
            if detected_lang != "other" and detected_lang != language_mode:
                if language_mode == "english": return "Language mode is set to English. Please type in English."
                if language_mode == "urdu": return "Language mode Urdu par set hai. Baraye meharbani Urdu mein likhein."

        query_type = self._get_query_type(prompt)
        classification_result = self.classifier.classify(prompt) if query_type == "new_question" else {"classification": "practical"}

        context = self._get_conversation_context(prompt)
        permanent_memory = self.state.get_permanent_memory()
        full_context = f"PERMANENT USER NOTES:\n{permanent_memory}\n\nCONVERSATION HISTORY:\n{context}"

        system_prompt = self._select_system_prompt(classification_result)
        if language_mode == "english": system_prompt += "\n\nIMPORTANT: You must respond in English."
        elif language_mode == "urdu": system_prompt += "\n\nIMPORTANT: You must respond in Roman Urdu."

        response = self.response_handler.generate_response(system_prompt, full_context, prompt)
        
        self.db.add_message(self.state.get_session_id(), prompt, response)
        self._add_to_semantic_memory(prompt, response)
        
        return response
    
    def _select_system_prompt(self, classification_result: Dict) -> str:
        classification = classification_result.get('classification', 'general')
        prompt_mapping = {
            'practical': 'practical_learning_prompt',
            'theoretical': 'theoretical_learning_prompt', 
            'general': 'general_chitchat_prompt',
            'irrelevant': 'irrelevant_response_prompt'
        }
        prompt_key = prompt_mapping.get(classification, 'default_system_prompt')
        return config.get_prompt(prompt_key)

    def summarize_and_save_note(self, note_text: str):
        summary = self.response_handler.summarize_note(note_text)
        self.state.update_permanent_memory(summary)