import os
import json
import google.generativeai as genai
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API with the API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("Warning: GEMINI_API_KEY not found in environment variables")


def analyze_code_diff(git_diff: str, prompt: Optional[str] = None, ai_output: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze a code diff using Gemini to identify new topics and their prerequisites.
    
    Args:
        git_diff: The git diff to analyze
        prompt: The user's prompt to the AI, if available
        ai_output: The AI's output to the user, if available
    
    Returns:
        Dict[str, Any]: A dictionary containing the analysis results
    """
    # Construct the prompt for Gemini
    context = ""
    if prompt:
        context += f"User prompt: {prompt}\n\n"
    if ai_output:
        context += f"AI output: {ai_output}\n\n"
    
    gemini_prompt = f"""
    {context}
    Identify newly introduced programming concepts or technologies in the following code diff.
    
    CODE DIFF:
    ```
    {git_diff}
    ```
    
    Even though you might not see changes to node_modules or package.json in the diff (they may have been filtered out),
    if you detect that the project involves npm, Node.js or similar JavaScript package management,
    include them as relevant topics for learning.
    
    Return a JSON structure with the following format:
    
    {{
      "new_topics": [
        {{
          "topic_id": "unique_string_identifier",
          "display_name": "Human-readable name",
          "short_description": "Brief description of the topic",
          "prerequisites": ["prerequisite_topic_id_1", "prerequisite_topic_id_2"]
        }}
      ]
    }}
    
    Notes:
    1. Make sure to generate a unique topic_id for each topic (use snake_case).
    2. Prerequisites should be other topic_ids. If they're new, include them as separate topics.
    3. Include no commentary or explanations outside the JSON structure.
    4. Consider both the code itself and the project structure when identifying topics.
    5. Evaluate both the user-specific coding topics and the underlying technologies/frameworks.
    """
    
    try:
        # Generate content using Gemini
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(gemini_prompt)
        
        # Extract the JSON from the response
        try:
            # Try to parse the response text as JSON directly
            raw_text = response.text
            
            # Find JSON block between ```json and ```
            if "```json" in raw_text:
                start_idx = raw_text.find("```json") + 7
                end_idx = raw_text.find("```", start_idx)
                json_str = raw_text[start_idx:end_idx].strip()
            else:
                # Find JSON block between ``` and ```
                start_idx = raw_text.find("```") + 3
                if start_idx >= 3:  # Found the opening ```
                    end_idx = raw_text.find("```", start_idx)
                    if end_idx != -1:
                        json_str = raw_text[start_idx:end_idx].strip()
                    else:
                        json_str = raw_text[start_idx:].strip()
                else:
                    # Try to use the entire response as JSON
                    json_str = raw_text
            
            # Parse the JSON
            result = json.loads(json_str)
            
            # Ensure the response has the expected structure
            if "new_topics" not in result:
                result = {"new_topics": []}
            
            return result
        
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON object from the text
            print("Error: Could not parse Gemini response as JSON")
            return {"new_topics": []}
        
    except Exception as e:
        print(f"Error calling Gemini API: {str(e)}")
        return {"new_topics": []}


def normalize_topic_id(topic_id: str) -> str:
    """
    Normalize a topic ID to a consistent format.
    
    Args:
        topic_id: The topic ID to normalize
    
    Returns:
        str: The normalized topic ID
    """
    # Convert to lowercase and replace spaces with underscores
    normalized = topic_id.lower().replace(" ", "_")
    
    # Remove any special characters
    normalized = "".join(c for c in normalized if c.isalnum() or c == "_")
    
    return normalized


def find_similar_topic(topic_id: str, existing_topics: Dict[str, Any]) -> Optional[str]:
    """
    Find a similar topic in the existing topics.
    
    Args:
        topic_id: The topic ID to find
        existing_topics: Dictionary of existing topics keyed by topic_id
    
    Returns:
        Optional[str]: The similar topic ID if found, None otherwise
    """
    # Normalize the target topic ID
    normalized_id = normalize_topic_id(topic_id)
    
    # Check for exact match
    if normalized_id in existing_topics:
        return normalized_id
    
    # Check for similar topics based on substring matching
    for existing_id in existing_topics:
        # If the normalized IDs have substantial overlap, consider them similar
        if normalized_id in existing_id or existing_id in normalized_id:
            # Check if display names are also similar
            target_display = topic_id.replace("_", " ").lower()
            existing_display = existing_topics[existing_id]["display_name"].lower()
            
            if target_display in existing_display or existing_display in target_display:
                return existing_id
    
    return None 