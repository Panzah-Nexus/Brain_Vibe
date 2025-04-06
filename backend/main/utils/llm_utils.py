"""
Utility functions for interacting with LLMs (e.g., Gemini API)
"""
import logging
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# Set up logger
logger = logging.getLogger(__name__)

def analyze_diff(diff_text: str, project_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Analyze a Git diff using an LLM (e.g., Gemini) to extract learning topics.
    
    Args:
        diff_text: The Git diff to analyze
        project_context: Optional context about the project to improve topic extraction
        
    Returns:
        A list of dictionaries representing detected topics
    """
    logger.info("Analyzing diff with LLM")
    if not diff_text:
        logger.warning("Empty diff provided")
        return []
    
    # STUB: In the real implementation, we would call Gemini API here
    # Sample implementation would be:
    # api_key = os.environ.get("GEMINI_API_KEY")
    # if not api_key:
    #     logger.error("GEMINI_API_KEY environment variable not set")
    #     return []
    #
    # response = call_gemini_api(api_key, diff_text, project_context)
    # return parse_gemini_response(response)
    
    # For now, analyze the mock diff and return mock topics
    return extract_mock_topics(diff_text)


def extract_mock_topics(diff_text: str) -> List[Dict[str, Any]]:
    """
    Mock function to extract topics from a diff.
    In the real implementation, this would be done by Gemini API.
    
    Args:
        diff_text: The Git diff to analyze
        
    Returns:
        A list of dictionaries representing detected topics
    """
    # Analyze the diff content to find potential topics - this is just a mock implementation
    topics = []
    
    if "React" in diff_text:
        topics.append({
            "topic_id": "react-hooks-useState",
            "title": "React Hooks - useState",
            "description": "Using the useState hook in React for managing component state",
            "prerequisites": ["react-basics"]
        })
    
    if "axios" in diff_text:
        topics.append({
            "topic_id": "axios-http-client",
            "title": "Axios HTTP Client",
            "description": "Making HTTP requests with Axios in JavaScript applications",
            "prerequisites": ["javascript-promises", "async-await"]
        })
    
    if "jwt_decode" in diff_text:
        topics.append({
            "topic_id": "jwt-authentication",
            "title": "JWT Authentication",
            "description": "Implementing authentication using JSON Web Tokens",
            "prerequisites": ["web-security-basics", "http-authentication"]
        })
    
    if "router" in diff_text:
        topics.append({
            "topic_id": "react-router",
            "title": "React Router",
            "description": "Client-side routing in React applications",
            "prerequisites": ["react-basics"]
        })
    
    return topics


def call_gemini_api(api_key: str, diff_text: str, project_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Call the Gemini API to analyze a diff.
    This is a placeholder for the actual implementation.
    
    Args:
        api_key: The Gemini API key
        diff_text: The Git diff to analyze
        project_context: Optional context about the project
        
    Returns:
        The parsed JSON response from the Gemini API
    """
    # This would be implemented in the actual code
    # import requests
    # 
    # url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    # headers = {
    #     "Content-Type": "application/json",
    #     "x-goog-api-key": api_key
    # }
    # 
    # prompt = f"""
    # Analyze the following Git diff and identify learning topics:
    # 
    # {diff_text}
    # 
    # Extract programming concepts, libraries, patterns, or frameworks that someone would need to learn.
    # For each topic, provide:
    # 1. A unique topic_id
    # 2. A display title
    # 3. A brief description
    # 4. Any prerequisite topics
    # 
    # Return the result as a JSON array of topics.
    # """
    # 
    # data = {
    #     "contents": [
    #         {
    #             "parts": [
    #                 {
    #                     "text": prompt
    #                 }
    #             ]
    #         }
    #     ],
    #     "generationConfig": {
    #         "temperature": 0.2,
    #         "topP": 0.8,
    #         "topK": 40
    #     }
    # }
    # 
    # try:
    #     response = requests.post(url, headers=headers, json=data)
    #     response.raise_for_status()
    #     return response.json()
    # except Exception as e:
    #     logger.exception(f"Error calling Gemini API: {e}")
    #     return {"error": str(e)}
    
    # Return mock response
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(extract_mock_topics(diff_text))
                        }
                    ]
                }
            }
        ]
    }


def parse_gemini_response(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse the response from the Gemini API.
    This is a placeholder for the actual implementation.
    
    Args:
        response: The JSON response from the Gemini API
        
    Returns:
        A list of dictionaries representing detected topics
    """
    # This would be implemented in the actual code
    # try:
    #     if "error" in response:
    #         logger.error(f"Error in Gemini API response: {response['error']}")
    #         return []
    #     
    #     if "candidates" not in response or not response["candidates"]:
    #         logger.error("No candidates in Gemini API response")
    #         return []
    #     
    #     content = response["candidates"][0]["content"]
    #     if "parts" not in content or not content["parts"]:
    #         logger.error("No parts in Gemini API response content")
    #         return []
    #     
    #     text = content["parts"][0]["text"]
    #     # The response might be in a code block, so extract the JSON
    #     if "```json" in text:
    #         text = text.split("```json")[1].split("```")[0].strip()
    #     elif "```" in text:
    #         text = text.split("```")[1].split("```")[0].strip()
    #     
    #     topics = json.loads(text)
    #     return topics
    # except Exception as e:
    #     logger.exception(f"Error parsing Gemini API response: {e}")
    #     return []
    
    # Return mock topics
    if "candidates" in response and response["candidates"]:
        try:
            text = response["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
        except Exception as e:
            logger.exception(f"Error parsing mock response: {e}")
            
    return [] 