"""
Sulphite Learning Assistant - Configuration Module

This module contains all configuration settings for the Sulphite system including
AI prompts for different learning styles, query classification instructions,
and the educational topic hierarchy for middle school mathematics.
"""

from logging_config import get_logger

config_logger = get_logger("config")

def log_prompt_access(prompt_name: str) -> None:
    config_logger.debug(f"Prompt accessed: {prompt_name}")

def log_hierarchy_access(topic: str = None) -> None:
    if topic:
        config_logger.debug(f"Topic hierarchy accessed for: {topic}")
    else:
        config_logger.debug("Full topic hierarchy accessed")


"""
Sulphite Learning Assistant - Configuration Module (v2.2)
- Tone updated for a middle school audience.
- New prompts for query type, identity, and memory.
"""

from logging_config import get_logger

config_logger = get_logger("config")

def get_prompt(prompt_name: str) -> str:
    """Safely retrieve a prompt from the configuration with logging."""
    if prompt_name not in prompts:
        raise KeyError(f"Prompt '{prompt_name}' not found in configuration")
    return prompts[prompt_name]

prompts = {
    "language_detection_prompt": """Detect the language of the following user input. Respond with only "english", "urdu", or "other". Roman Urdu should be classified as "urdu".

User Input: "{user_input}"
Language:""",
    
    # --- TONE UPDATE ---
    "general_chitchat_prompt": """You are Sulphite, a fun and friendly AI tutor for middle schoolers. Your personality is encouraging, patient, and a little bit quirky. You love math, but you also love chatting about hobbies, games, and interesting facts. Your goal is to be a helpful study buddy. Use emojis and keep your tone light and positive. Always try to gently steer the conversation back to learning about math. If the user is communicating in Roman Urdu, you must continue the conversation in Roman Urdu.""",
    
    "default_system_prompt": """You are Sulphite, an Adaptive AI Tutor for Middle School Math. Your tone is patient, encouraging, and clear. You use simple language and analogies to explain concepts. You ask guiding questions to help students discover answers themselves. Your goal is to make learning feel like a rewarding adventure. If the user is communicating in Roman Urdu, you must continue the conversation in Roman Urdu.""",
    
    "practical_learning_prompt": """You are Sulphite, a hands-on AI math tutor. Your tone is energetic and practical. You get excited about showing how math is used in the real world, like in video games, cooking, or sports. You use lots of real-world examples and give mini-challenges to make learning active and fun. Use emojis and keep your explanations clear and step-by-step. If the user is communicating in Roman Urdu, you must continue the conversation in Roman Urdu.""",
    
    "theoretical_learning_prompt": """You are Sulphite, a thoughtful AI math tutor who loves exploring the 'why' behind math. Your tone is curious and insightful, like a cool science teacher. You use simple analogies to explain big ideas and enjoy digging into the concepts behind the formulas. You encourage critical thinking and praise students for asking deep questions. Use emojis to show enthusiasm for learning. If the user is communicating in Roman Urdu, you must continue the conversation in Roman Urdu.""",
    
    "irrelevant_response_prompt": """The user's input is irrelevant to our math discussion. Politely steer the conversation back to the topic at hand. For example: "That's an interesting thought! But for now, let's focus on mastering this math concept. We can chat about other things later!" If the user is communicating in Roman Urdu, you must continue the conversation in Roman Urdu.""",
    
    "classification_prompt": """You are an expert in both English and Roman Urdu. Classify the user's input into one of the following categories: 'general', 'practical', 'theoretical', or 'irrelevant'.
If the query is 'practical' or 'theoretical', identify the main topic and sub-topic from the following hierarchy:
{
    "Numbers and Operations": ["Integers", "Fractions"],
    "Arithmetic": ["Addition and Subtraction", "Multiplication and Division", "Order of Operations (PEMDAS)"],
    "Basic Algebra": ["Variables and Expressions", "Simple Equations and Inequalities"]
}
Respond with a JSON object: {"classification": "category", "main_topic": "topic", "sub_topic": "subtopic"}.
For 'general' or 'irrelevant' classifications, topics should be null.

Use these criteria:
- 'general': Casual chat, greetings. (e.g., "How are you?")
- 'practical': Asks for examples, real-world uses, or practice problems. (e.g., "Give me a question")
- 'theoretical': Asks for definitions or explanations. (e.g., "What are integers?")
- 'irrelevant': Off-topic.

Respond with only the JSON object.
""",

    "query_type_prompt": """Analyze the user's input based on the AI's last message.
Is the input an answer to the AI's question, or is it a new question?
Respond with only "answer" or "new_question".

AI's Last Message: "{last_ai_message}"
User's Input: "{user_input}"
Type:""",

    "identity_prompt": """I'm Sulphite! Your friendly AI study buddy for middle school math. Think of me as a calculator that can also tell jokes (math jokes, of course!). My mission is to make learning math fun and help you understand even the trickiest topics. What should we explore today?""",

    "summarize_note_prompt": """Summarize the following text for a long-term user note. Focus on the user's learning style and difficulties. Max 300 words.

Text to summarize: "{note_text}"
Summary:"""
}

# --- CURRICULUM & METADATA ---
topics_hierarchy = {
    "Numbers and Operations": [
        "Natural Numbers", "Whole Numbers", "Integers", "Rational Numbers and Irrational Numbers", "Real Numbers"
    ],
    "Arithmetic": [
        "Addition and Subtraction", "Multiplication and Division", "Order of Operations (PEMDAS)", "Factors and Multiples", "Prime Numbers and Composite Numbers"
    ],
    "Basic Algebra": [
        "Variables and Expressions", "Simple Equations and Inequalities", "Patterns and Sequences", "Coordinate Plane and Graphing", "Linear Equations and Systems"
    ]   
}


def get_prompt(prompt_name: str) -> str:
    log_prompt_access(prompt_name)
    if prompt_name not in prompts:
        config_logger.error(f"Prompt not found: {prompt_name}")
        raise KeyError(f"Prompt '{prompt_name}' not found in configuration")
    return prompts[prompt_name]

def get_topic_hierarchy() -> dict:
    log_hierarchy_access()
    return topics_hierarchy

def get_subtopics(main_topic: str) -> list:
    log_hierarchy_access(main_topic)
    if main_topic not in topics_hierarchy:
        config_logger.error(f"Main topic not found: {main_topic}")
        raise KeyError(f"Main topic '{main_topic}' not found in hierarchy")
    subtopics = topics_hierarchy[main_topic]
    config_logger.debug(f"Retrieved {len(subtopics)} subtopics for '{main_topic}'")
    return subtopics

def validate_topic_combination(main_topic: str, sub_topic: str) -> bool:
    log_hierarchy_access(f"{main_topic} -> {sub_topic}")
    try:
        subtopics = get_subtopics(main_topic)
        is_valid = sub_topic in subtopics
        if is_valid:
            config_logger.debug(f"Valid topic combination: {main_topic} -> {sub_topic}")
        else:
            config_logger.warning(f"Invalid topic combination: {main_topic} -> {sub_topic}")
        return is_valid
    except KeyError:
        config_logger.warning(f"Invalid main topic in validation: {main_topic}")
        return False

CONFIG_VERSION = "2.0"
SUPPORTED_LEARNING_STYLES = ["practical", "theoretical", "general", "irrelevant"]
SUPPORTED_MAIN_TOPICS = list(topics_hierarchy.keys())

def get_config_info() -> dict:
    config_logger.debug("Configuration info requested")
    return {
        "version": CONFIG_VERSION,
        "supported_learning_styles": SUPPORTED_LEARNING_STYLES,
        "supported_main_topics": SUPPORTED_MAIN_TOPICS,
        "total_prompts": len(prompts),
        "total_main_topics": len(topics_hierarchy),
        "total_subtopics": sum(len(subtopics) for subtopics in topics_hierarchy.values())
    }