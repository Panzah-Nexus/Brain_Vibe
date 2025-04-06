"""
LLM Utilities for Code Analysis

This module provides utilities for analyzing code using large language models.
In the future, this will integrate with Gemini or other LLM APIs. For now, it provides
mock implementations and placeholders.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

def analyze_diff(diff_content: str, project_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Analyze a diff using LLM to extract relevant programming topics.
    
    Args:
        diff_content: The diff content to analyze
        project_context: Optional context about the project
        
    Returns:
        A list of topic dictionaries
    """
    # Check if we're running in a test environment
    if os.environ.get('DJANGO_SETTINGS_MODULE') == 'backend.settings.test':
        logger.info("Running in test environment, using mock analysis")
        return mock_topic_analysis()
    
    # In the future, this will call Gemini or other LLM APIs
    # For now, we return mock data
    logger.info("LLM API integration not yet implemented, using mock analysis")
    return mock_topic_analysis()

def format_llm_prompt(diff_content: str, project_context: Dict[str, Any] = None) -> str:
    """
    Format the prompt for the LLM.
    
    Args:
        diff_content: The diff content to analyze
        project_context: Optional context about the project
        
    Returns:
        A formatted prompt string
    """
    # Create a context string if project_context is provided
    context_str = ""
    if project_context:
        context_str = "Project context:\n"
        for key, value in project_context.items():
            if key == "existing_topics" and isinstance(value, list):
                context_str += f"Existing topics: {', '.join([t.get('title', 'Unknown') for t in value])}\n"
            else:
                context_str += f"{key}: {value}\n"
    
    # Format the prompt
    prompt = f"""
You are an expert programming educator tasked with analyzing code changes and identifying learning topics. 

{context_str}

Analyze the following Git diff and identify learning topics that someone would need to understand:

```diff
{diff_content}
```

Extract programming concepts, libraries, patterns, or frameworks that would be important to learn.
For each topic, provide:
1. A unique topic_id (lowercase, hyphenated)
2. A display title
3. A brief description (1-2 sentences)
4. Any prerequisite topics that should be learned first

Return the result as a JSON array of topics, with each topic having the following structure:
{{
  "topic_id": "example-topic",
  "title": "Example Topic",
  "description": "Brief description of the topic.",
  "prerequisites": ["prerequisite-topic-1", "prerequisite-topic-2"]
}}

Focus only on important concepts. Do not include basic programming knowledge that any developer would already know.
"""
    
    return prompt

def mock_topic_analysis() -> List[Dict[str, Any]]:
    """
    Return a mock analysis result for testing purposes.
    
    Returns:
        A list of topic dictionaries
    """
    return [
        {
            "topic_id": "react-hooks-useState",
            "title": "React Hooks - useState",
            "description": "Using the useState hook in React for managing component state",
            "prerequisites": ["react-basics"]
        },
        {
            "topic_id": "axios-http-client",
            "title": "Axios HTTP Client",
            "description": "Making HTTP requests with Axios in JavaScript applications",
            "prerequisites": ["javascript-promises", "async-await"]
        },
        {
            "topic_id": "jwt-authentication",
            "title": "JWT Authentication",
            "description": "Implementing authentication using JSON Web Tokens",
            "prerequisites": ["web-security-basics", "http-authentication"]
        }
    ]

def extract_topics_from_response(llm_response: str) -> List[Dict[str, Any]]:
    """
    Extract topics from the LLM response.
    
    Args:
        llm_response: The response from the LLM
        
    Returns:
        A list of topic dictionaries
    """
    # This is a placeholder for future implementation
    # In the future, this will parse the LLM response and extract topics
    try:
        # Try to parse the response as JSON
        # In a real implementation, we'd need to handle more complex parsing
        topics = json.loads(llm_response)
        return topics
    except json.JSONDecodeError:
        logger.error("Failed to parse LLM response as JSON")
        return []

def validate_topic(topic: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Validate a topic dictionary.
    
    Args:
        topic: The topic dictionary to validate
        
    Returns:
        The validated topic dictionary or None if invalid
    """
    required_fields = ['topic_id', 'title', 'description']
    for field in required_fields:
        if field not in topic:
            logger.warning(f"Topic missing required field: {field}")
            return None
    
    # Ensure topic_id is valid format (lowercase, hyphenated)
    topic_id = topic.get('topic_id', '')
    if not all(c.islower() or c.isdigit() or c == '-' for c in topic_id):
        logger.warning(f"Invalid topic_id format: {topic_id}")
        # Attempt to fix the topic_id
        fixed_topic_id = topic_id.lower().replace(' ', '-')
        topic['topic_id'] = fixed_topic_id
    
    # Ensure prerequisites is a list
    if 'prerequisites' in topic and not isinstance(topic['prerequisites'], list):
        logger.warning(f"Invalid prerequisites format for topic {topic_id}")
        topic['prerequisites'] = []
    
    return topic 