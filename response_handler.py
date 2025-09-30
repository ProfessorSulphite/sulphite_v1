# professorsulphite/sulphite_v1/sulphite_v1-e0f21b0d541b71aa42e22e2435a9b0b9f2caa2e4/response_handler.py
"""
Handles all logic related to generating AI responses, including prompt construction and model invocation.
"""
from typing import Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import config

class ResponseHandler:
    def __init__(self, model: ChatGoogleGenerativeAI):
        self.model = model

    def _build_final_prompt(self, system_prompt: str, context: str, user_query: str) -> Tuple[SystemMessage, HumanMessage]:
        """Constructs the final prompt with context and instructions."""
        final_system_prompt = SystemMessage(content=system_prompt)
        
        contextualized_query = (
            f"{context}\n\n"
            f"IMPORTANT: Now, focusing only on the user's LATEST message, respond to: {user_query}"
        )
        final_user_prompt = HumanMessage(content=contextualized_query)
        
        return final_system_prompt, final_user_prompt

    def generate_response(self, system_prompt: str, context: str, user_query: str) -> str:
        """Generates a standard response based on the provided context and prompt."""
        system_msg, user_msg = self._build_final_prompt(system_prompt, context, user_query)
        response = self.model.invoke([system_msg, user_msg])
        return response.content

    def answer_identity_question(self) -> str:
        """Provides a safe and consistent answer to 'who are you?'."""
        return config.get_prompt("identity_prompt")

    def summarize_note(self, note_text: str) -> str:
        """Summarizes text to be stored in permanent memory."""
        prompt = config.get_prompt("summarize_note_prompt").format(note_text=note_text)
        response = self.model.invoke([HumanMessage(content=prompt)])
        return response.content.strip()