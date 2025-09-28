"""
Sulphite Learning Assistant - Configuration Module

This module contains all configuration settings for the Sulphite system including
AI prompts for different learning styles, query classification instructions,
and the educational topic hierarchy for middle school mathematics.

The configuration supports adaptive learning by providing different system prompts
based on the classified learning preference (practical vs theoretical) and
maintains a structured curriculum hierarchy for topic identification.

Configuration Components:
- Learning-style specific prompts (practical, theoretical, general, irrelevant)
- Classification prompt with JSON output instructions
- Middle school mathematics topic hierarchy
- Default system prompt for fallback scenarios

Learning Styles:
- Practical: Focuses on real-world applications and problem-solving
- Theoretical: Emphasizes concepts, theories, and deep understanding  
- General: Friendly conversation that guides towards mathematics
- Irrelevant: Polite redirection to educational topics

Topic Coverage:
- Numbers and Operations (natural, whole, integers, rational, real)
- Arithmetic (operations, order, factors, primes)
- Basic Algebra (variables, equations, patterns, graphing)

Author: AI Assistant
Date: September 28, 2025
Version: 2.0
"""

from logging_config import get_logger

# Initialize logger for configuration access tracking
config_logger = get_logger("config")

def log_prompt_access(prompt_name: str) -> None:
    """
    Log when a specific prompt is accessed from the configuration.
    
    Args:
        prompt_name (str): Name of the prompt being accessed
    """
    config_logger.debug(f"Prompt accessed: {prompt_name}")

def log_hierarchy_access(topic: str = None) -> None:
    """
    Log when the topic hierarchy is accessed.
    
    Args:
        topic (str, optional): Specific topic being accessed
    """
    if topic:
        config_logger.debug(f"Topic hierarchy accessed for: {topic}")
    else:
        config_logger.debug("Full topic hierarchy accessed")

# Configuration for Adaptive Learning Prompts
prompts = {
    "general_chitchat_prompt": """You are a friendly and engaging AI assistant. You excel at casual conversations, making small talk, and keeping the interaction light-hearted and enjoyable. You can discuss a wide range of topics, share interesting facts, and respond to user inputs with humor and warmth. Your goal is to create a pleasant and entertaining experience for the user. Your main purpose is to answer the user questions in a friendly and engaging manner and bring them back to mathematics.""",
    
    "default_system_prompt": """You are an Adaptive, Socratic, Personalized Learning Assistant for Middle School Student. You adapt your teaching style to the student's learning preferences and pace. You ask thought-provoking questions to stimulate critical thinking and guide the student to discover answers on their own. You provide personalized explanations, examples, and resources based on the student's interests and needs. Your goal is to foster a deep understanding of concepts while making learning engaging and enjoyable.""",
    
    "practical_learning_prompt": """You are a Practical Learning Assistant. You focus on problem solving, real-world applications of concepts and provide hands-on examples and exercises. You encourage the student to apply what they learn through projects, experiments, and problem-solving activities. Your goal is to make learning relevant and practical, helping the student see the value of their education in everyday life. You explain and provoke critical thinking through practical scenarios.""",
    
    "theoretical_learning_prompt": """You are a Theoretical Learning Assistant. You focus on deep understanding of concepts, theories, and principles. You provide detailed explanations, explore abstract ideas, and encourage the student to think critically about the underlying concepts. You guide the student through complex topics, helping them build a strong foundation of knowledge. Your goal is to foster intellectual curiosity and a love for learning.""",
    
    "irrelevant_response_prompt": """The user's input is irrelevant to the current topic of discussion. Politely inform the user that their input does not pertain to the subject at hand and encourage them to stay focused on the topic. Maintain a respectful and understanding tone while guiding the conversation back to the relevant subject matter.""",
    
    "classification_prompt": """Input should focus on only Middle School Mathematics or General Knowledge. Classify the user's input into one of the following categories: 'general', 'practical', 'theoretical', or 'irrelevant'. 
If the query is 'practical' or 'theoretical', identify the main topic and sub-topic from the following hierarchy:
{
    "Numbers and Operations": [
        "Natural Numbers",
        "Whole Numbers",
        "Integers",
        "Rational Numbers and Irrational Numbers",
        "Real Numbers"
    ],
    "Arithmetic": [
        "Addition and Subtraction",
        "Multiplication and Division",
        "Order of Operations (PEMDAS)",
        "Factors and Multiples",
        "Prime Numbers and Composite Numbers"
    ],
    "Basic Algebra": [
        "Variables and Expressions",
        "Simple Equations and Inequalities",
        "Patterns and Sequences",
        "Coordinate Plane and Graphing",
        "Linear Equations and Systems"
    ]
}
If the query contains advanced topics not in the hierarchy, return an empty JSON {}.
Respond with a JSON object with the following format: {"classification": "category", "main_topic": "topic", "sub_topic": "subtopic"}.
For 'general' or 'irrelevant' classifications, the main_topic and sub_topic should be null.

Use the following criteria for classification:

- 'general': Input related to casual conversation, social interaction, or non-specific topics.
- 'practical': Input focused on real-world applications, problem-solving, or hands-on activities of middle school students.
- 'theoretical': Input centered around abstract concepts, theories, or in-depth explanations.
- 'irrelevant': Input that does not pertain to the current topic of discussion or is off-topic.

Respond with only the JSON object without any additional text.
"""
}

def get_prompt(prompt_name: str) -> str:
    """
    Safely retrieve a prompt from the configuration with logging.
    
    Args:
        prompt_name (str): Name of the prompt to retrieve
        
    Returns:
        str: The requested prompt text
        
    Raises:
        KeyError: If the prompt name doesn't exist
    """
    log_prompt_access(prompt_name)
    
    if prompt_name not in prompts:
        config_logger.error(f"Prompt not found: {prompt_name}")
        raise KeyError(f"Prompt '{prompt_name}' not found in configuration")
    
    return prompts[prompt_name]

# Middle School Mathematics Topic Hierarchy
# This hierarchy defines the educational scope for classification and topic identification
topics_hierarchy = {
    "Numbers and Operations": [
        "Natural Numbers",           # Counting numbers: 1, 2, 3, ...
        "Whole Numbers",            # Natural numbers plus zero: 0, 1, 2, 3, ...
        "Integers",                 # Whole numbers plus negative numbers: ..., -2, -1, 0, 1, 2, ...
        "Rational Numbers and Irrational Numbers",  # Fractions, decimals, and non-repeating decimals
        "Real Numbers"              # All rational and irrational numbers
    ],
    "Arithmetic": [
        "Addition and Subtraction",          # Basic operations with various number types
        "Multiplication and Division",       # Basic operations including long division
        "Order of Operations (PEMDAS)",      # Parentheses, Exponents, Multiplication/Division, Addition/Subtraction
        "Factors and Multiples",            # Finding factors, GCD, LCM
        "Prime Numbers and Composite Numbers"  # Number theory basics
    ],
    "Basic Algebra": [
        "Variables and Expressions",         # Using letters to represent unknown values
        "Simple Equations and Inequalities", # Solving for unknowns
        "Patterns and Sequences",           # Arithmetic and geometric sequences
        "Coordinate Plane and Graphing",    # Plotting points and basic graphing
        "Linear Equations and Systems"      # Linear relationships and solving systems
    ]   
}

def get_topic_hierarchy() -> dict:
    """
    Retrieve the complete topic hierarchy with logging.
    
    Returns:
        dict: The complete topics hierarchy dictionary
    """
    log_hierarchy_access()
    return topics_hierarchy

def get_subtopics(main_topic: str) -> list:
    """
    Get subtopics for a specific main topic with logging.
    
    Args:
        main_topic (str): The main topic to get subtopics for
        
    Returns:
        list: List of subtopics under the main topic
        
    Raises:
        KeyError: If the main topic doesn't exist
    """
    log_hierarchy_access(main_topic)
    
    if main_topic not in topics_hierarchy:
        config_logger.error(f"Main topic not found: {main_topic}")
        raise KeyError(f"Main topic '{main_topic}' not found in hierarchy")
    
    subtopics = topics_hierarchy[main_topic]
    config_logger.debug(f"Retrieved {len(subtopics)} subtopics for '{main_topic}'")
    return subtopics

def validate_topic_combination(main_topic: str, sub_topic: str) -> bool:
    """
    Validate that a main topic and sub-topic combination exists in the hierarchy.
    
    Args:
        main_topic (str): The main topic to validate
        sub_topic (str): The sub-topic to validate
        
    Returns:
        bool: True if the combination is valid, False otherwise
    """
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

# Configuration metadata
CONFIG_VERSION = "2.0"
SUPPORTED_LEARNING_STYLES = ["practical", "theoretical", "general", "irrelevant"]
SUPPORTED_MAIN_TOPICS = list(topics_hierarchy.keys())

def get_config_info() -> dict:
    """
    Get metadata about the configuration.
    
    Returns:
        dict: Configuration metadata
    """
    config_logger.debug("Configuration info requested")
    return {
        "version": CONFIG_VERSION,
        "supported_learning_styles": SUPPORTED_LEARNING_STYLES,
        "supported_main_topics": SUPPORTED_MAIN_TOPICS,
        "total_prompts": len(prompts),
        "total_main_topics": len(topics_hierarchy),
        "total_subtopics": sum(len(subtopics) for subtopics in topics_hierarchy.values())
    }
