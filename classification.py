"""
Sulphite Learning Assistant - Query Classification Module

This module handles intelligent classification of user queries into different
learning categories. It uses Google's Gemini AI to classify queries as 'general',
'practical', 'theoretical', or 'irrelevant', and identifies main topics and
subtopics from a predefined educational hierarchy for middle school mathematics.

Features:
- AI-powered query classification using Gemini 2.0 Flash
- JSON-structured output with classification, main topic, and subtopic
- Support for middle school mathematics topic hierarchy
- Advanced topic detection and filtering
- Comprehensive logging of classification process
- Error handling for malformed AI responses

Classification Categories:
- general: Casual conversation, social interaction, non-specific topics
- practical: Real-world applications, problem-solving, hands-on activities
- theoretical: Abstract concepts, theories, in-depth explanations  
- irrelevant: Off-topic or unrelated content

Author: AI Assistant
Date: September 28, 2025
Version: 2.0
"""

import json
import os
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from logging_config import get_logger, sulphite_logger
import config

# Load environment variables
load_dotenv()

# Get Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

# Initialize Google AI model
google_ai = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=GEMINI_API_KEY)


class Classifier:
    """
    AI-powered query classifier for the Sulphite Learning Assistant.
    
    This class uses Google's Gemini AI model to classify user queries into
    educational categories and identify relevant topics from the middle school
    mathematics curriculum hierarchy. All classification operations are logged
    in detail for monitoring and debugging purposes.
    
    Attributes:
        classifier_prompt (str): System prompt for the AI classification model
        classification_model (ChatGoogleGenerativeAI): The AI model instance
        logger (logging.Logger): Logger for classification operations
    
    Example:
        >>> classifier = Classifier()
        >>> result = classifier.classify("How do I solve 2x + 3 = 7?")
        >>> print(result)
        {
            "classification": "practical",
            "main_topic": "Basic Algebra", 
            "sub_topic": "Simple Equations and Inequalities"
        }
    """
    
    def __init__(self):
        """
        Initialize the classifier with AI model and logging.
        
        Sets up the classification prompt from config and initializes
        the Google AI model for processing queries.
        """
        self.logger = get_logger("classification")
        
        sulphite_logger.log_function_entry(self.logger, "__init__")
        
        try:
            self.classifier_prompt = config.prompts["classification_prompt"]
            self.classification_model = google_ai
            
            self.logger.info("Classifier initialized successfully with Gemini 1.5 Flash model")
            sulphite_logger.log_function_exit(self.logger, "__init__", "Classifier initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize classifier: {e}")
            raise

    def classify(self, user_input: str) -> Dict[str, Any]:
        """
        Classify a user query into educational categories with topic identification.
        
        This method sends the user query to the Gemini AI model along with
        classification instructions and parses the returned JSON response.
        It handles various response formats and provides fallback for errors.
        
        Args:
            user_input (str): The user's query to classify
            
        Returns:
            Dict[str, Any]: Classification result containing:
                - classification (str): Category ('general', 'practical', 'theoretical', 'irrelevant')
                - main_topic (str|None): Main topic from hierarchy or None
                - sub_topic (str|None): Subtopic from hierarchy or None
                Returns empty dict {} for advanced topics or parsing errors
                
        Example:
            >>> classifier = Classifier()
            >>> result = classifier.classify("What are prime numbers?")
            >>> result
            {
                "classification": "theoretical",
                "main_topic": "Arithmetic",
                "sub_topic": "Prime Numbers and Composite Numbers"
            }
        """
        sulphite_logger.log_function_entry(
            self.logger, 
            "classify", 
            query_length=len(user_input),
            query_preview=user_input[:100]
        )
        
        # Log the start of query processing
        sulphite_logger.log_query_processing(
            self.logger,
            user_input,
            "CLASSIFICATION_START",
            {"model": "gemini-1.5-flash"}
        )
        
        try:
            # Prepare messages for the AI model
            messages = [
                SystemMessage(content=self.classifier_prompt),
                HumanMessage(content=user_input),
            ]
            
            self.logger.debug(f"Sending classification request to AI model")
            
            # Get response from AI model
            response = self.classification_model.invoke(messages)
            
            sulphite_logger.log_query_processing(
                self.logger,
                user_input,
                "AI_RESPONSE_RECEIVED",
                {"response_length": len(response.content)}
            )
            
            # Parse the AI response
            result = self._parse_ai_response(response.content, user_input)
            
            # Log the final classification result
            sulphite_logger.log_classification_result(self.logger, user_input, result)
            
            sulphite_logger.log_function_exit(self.logger, "classify", result)
            return result
            
        except Exception as e:
            self.logger.error(f"Classification failed for query '{user_input[:50]}...': {e}")
            
            # Return empty dict on any error
            error_result = {}
            sulphite_logger.log_classification_result(self.logger, user_input, error_result)
            sulphite_logger.log_function_exit(self.logger, "classify", error_result)
            return error_result

    def _parse_ai_response(self, response_content: str, original_query: str) -> Dict[str, Any]:
        """
        Parse the AI model's response content into a structured dictionary.
        
        Handles various response formats including markdown-wrapped JSON,
        plain JSON, and malformed responses. Provides detailed logging
        of the parsing process.
        
        Args:
            response_content (str): Raw response content from AI model
            original_query (str): Original user query for logging context
            
        Returns:
            Dict[str, Any]: Parsed classification result or empty dict on error
        """
        sulphite_logger.log_function_entry(
            self.logger, 
            "_parse_ai_response",
            content_length=len(response_content),
            query_preview=original_query[:50]
        )
        
        try:
            # Log the raw response for debugging
            self.logger.debug(f"Raw AI response: {response_content[:200]}...")
            
            # Clean the response content
            content = response_content.strip()
            
            # Handle markdown-wrapped JSON
            if content.startswith("```json"):
                self.logger.debug("Detected markdown-wrapped JSON response")
                # Extract content between ```json and ```
                start_marker = "```json"
                end_marker = "```"
                start_idx = content.find(start_marker) + len(start_marker)
                end_idx = content.rfind(end_marker)
                
                if start_idx > len(start_marker) - 1 and end_idx > start_idx:
                    content = content[start_idx:end_idx].strip()
                    self.logger.debug("Successfully extracted JSON from markdown")
                else:
                    self.logger.warning("Malformed markdown JSON wrapper detected")
            
            # Parse JSON content
            json_response = json.loads(content)
            
            # Validate the response structure
            if not isinstance(json_response, dict):
                self.logger.warning("AI response is not a dictionary")
                return {}
            
            # Log successful parsing
            self.logger.debug(f"Successfully parsed JSON response: {json_response}")
            
            # Validate required fields
            classification = json_response.get('classification', '')
            if classification not in ['general', 'practical', 'theoretical', 'irrelevant']:
                self.logger.warning(f"Invalid classification category: {classification}")
                return {}
            
            sulphite_logger.log_query_processing(
                self.logger,
                original_query,
                "JSON_PARSING_SUCCESS",
                {"classification": classification}
            )
            
            sulphite_logger.log_function_exit(self.logger, "_parse_ai_response", json_response)
            return json_response
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing failed: {e}")
            self.logger.error(f"Problematic content: {content[:500]}...")
            
            sulphite_logger.log_query_processing(
                self.logger,
                original_query,
                "JSON_PARSING_FAILED",
                {"error": str(e)}
            )
            
        except Exception as e:
            self.logger.error(f"Unexpected error parsing AI response: {e}")
            
        # Return empty dict for any parsing error
        sulphite_logger.log_function_exit(self.logger, "_parse_ai_response", {})
        return {}

    def validate_topic_hierarchy(self, main_topic: Optional[str], sub_topic: Optional[str]) -> bool:
        """
        Validate that the identified topics exist in the predefined hierarchy.
        
        Args:
            main_topic (Optional[str]): The main topic to validate
            sub_topic (Optional[str]): The subtopic to validate
            
        Returns:
            bool: True if topics are valid according to hierarchy, False otherwise
        """
        sulphite_logger.log_function_entry(
            self.logger,
            "validate_topic_hierarchy",
            main_topic=main_topic,
            sub_topic=sub_topic
        )
        
        if not main_topic:
            sulphite_logger.log_function_exit(self.logger, "validate_topic_hierarchy", True)
            return True
        
        # Check if main topic exists in hierarchy
        if main_topic not in config.topics_hierarchy:
            self.logger.warning(f"Main topic '{main_topic}' not found in hierarchy")
            sulphite_logger.log_function_exit(self.logger, "validate_topic_hierarchy", False)
            return False
        
        # Check if subtopic exists under the main topic
        if sub_topic and sub_topic not in config.topics_hierarchy[main_topic]:
            self.logger.warning(f"Sub topic '{sub_topic}' not found under '{main_topic}'")
            sulphite_logger.log_function_exit(self.logger, "validate_topic_hierarchy", False)
            return False
        
        self.logger.debug(f"Topic hierarchy validation passed: {main_topic} -> {sub_topic}")
        sulphite_logger.log_function_exit(self.logger, "validate_topic_hierarchy", True)
        return True
