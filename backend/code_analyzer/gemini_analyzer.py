"""
Google Gemini API Client for BrainVibe
Analyzes code diffs to extract programming topics
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
import google.generativeai as genai
from google.api_core import retry

logger = logging.getLogger(__name__)

# Template for the prompt to Gemini
GEMINI_PROMPT_TEMPLATE = """
You are an expert programming topic analyzer. Analyze the provided code diff to identify new programming concepts, technologies, libraries, patterns, or methodologies that would be valuable for a programmer to learn.

CODE DIFF:
{code_diff}

USER'S ALREADY COMPLETED TOPICS:
{completed_topics}

USER'S ALREADY IDENTIFIED TO-LEARN TOPICS:
{to_learn_topics}

INSTRUCTIONS:
1. Identify programming concepts, technologies, or patterns evident in the code diff that represent discrete learning topics.
2. EXCLUDE any topics that appear in the COMPLETED or TO-LEARN lists above.
3. Merge any synonyms or near-duplicates (e.g., "React Hooks Basics" and "Using React Hooks" should be unified).
4. For each new topic, identify any direct prerequisites that should be learned first.

RESPONSE FORMAT:
Respond with a list of new topics only. For each topic:
- Title: Concise, specific name for the topic (e.g., "React Context API" not just "React")
- Description: 1-2 sentence explanation of what this topic involves
- Prerequisites: List any prerequisite topics that should be learned first (if any)
- Code_References: Brief mention of where/how this appears in the diff

No introduction or conclusion text is needed. Only analyze actual code—ignore comments, documentation, or configuration changes unless they introduce new programming concepts.
"""

class GeminiTopicAnalyzer:
    """
    Uses Google Gemini AI to analyze code diffs and extract programming topics
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini client with API key
        
        Args:
            api_key: Google Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not provided and GEMINI_API_KEY environment variable not set")
        
        # Initialize the Gemini client
        genai.configure(api_key=self.api_key)
        
        # Get the model
        self.model = genai.GenerativeModel('gemini-pro')
    
    @retry.Retry(predicate=retry.if_transient_error)
    def analyze_diff(self, 
                    code_diff: str, 
                    completed_topics: List[str] = None, 
                    to_learn_topics: List[str] = None,
                    temperature: float = 0.1) -> Dict[str, Any]:
        """
        Analyze a code diff to extract programming topics
        
        Args:
            code_diff: The code diff to analyze
            completed_topics: List of topics the user has already completed
            to_learn_topics: List of topics the user already knows they need to learn
            temperature: Sampling temperature (0.0-1.0), lower = more deterministic
            
        Returns:
            Dictionary containing extracted topics and their metadata
        """
        if not code_diff:
            logger.warning("Empty code diff provided, skipping analysis")
            return {"topics": []}
        
        # Format the lists for the prompt
        completed_topics_str = "\n".join([f"- {topic}" for topic in (completed_topics or [])])
        to_learn_topics_str = "\n".join([f"- {topic}" for topic in (to_learn_topics or [])])
        
        # Format the prompt
        prompt = GEMINI_PROMPT_TEMPLATE.format(
            code_diff=code_diff,
            completed_topics=completed_topics_str or "None",
            to_learn_topics=to_learn_topics_str or "None"
        )
        
        try:
            # Call the Gemini API
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
            )
            
            # Process the response
            response_text = response.text
            
            # Parse the response into a structured format
            # This is a simple parser that expects the format described in the prompt
            topics = self._parse_gemini_response(response_text)
            
            return {
                "topics": topics,
                "raw_response": response_text
            }
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            raise
    
    def _parse_gemini_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse the response from Gemini into a structured format
        
        Args:
            response_text: The raw text response from Gemini
            
        Returns:
            List of topics with their metadata
        """
        topics = []
        current_topic = None
        
        # Split by lines and process
        lines = response_text.strip().split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for a new topic (starting with "- Title:" or just "Title:")
            if line.startswith("- Title:") or line.startswith("Title:"):
                # Save the previous topic if it exists
                if current_topic:
                    topics.append(current_topic)
                
                # Extract the title
                title = line.split(":", 1)[1].strip()
                current_topic = {
                    "title": title,
                    "description": "",
                    "prerequisites": [],
                    "code_references": ""
                }
            
            # Check for description
            elif current_topic and (line.startswith("- Description:") or line.startswith("Description:")):
                current_topic["description"] = line.split(":", 1)[1].strip()
            
            # Check for prerequisites
            elif current_topic and (line.startswith("- Prerequisites:") or line.startswith("Prerequisites:")):
                prereq_text = line.split(":", 1)[1].strip()
                if prereq_text and prereq_text.lower() != "none":
                    # Handle comma-separated prerequisites
                    prereqs = [p.strip() for p in prereq_text.split(",")]
                    current_topic["prerequisites"] = prereqs
            
            # Check for code references
            elif current_topic and (line.startswith("- Code_References:") or line.startswith("Code_References:")):
                current_topic["code_references"] = line.split(":", 1)[1].strip()
            
            # If we're in a topic but the line doesn't start with a known field,
            # it might be a continuation of the previous field
            elif current_topic:
                # Try to append to the appropriate field
                if current_topic["description"] and not current_topic["prerequisites"] and not current_topic["code_references"]:
                    current_topic["description"] += " " + line
                elif current_topic["code_references"]:
                    current_topic["code_references"] += " " + line
        
        # Add the last topic if it exists
        if current_topic:
            topics.append(current_topic)
        
        return topics

# Usage example:
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python gemini_analyzer.py <diff_file>")
        sys.exit(1)
    
    # Read the diff from a file
    with open(sys.argv[1], "r") as f:
        diff_content = f.read()
    
    # Sample completed and to-learn topics
    completed = ["Python Basics", "Git Version Control"]
    to_learn = ["React Hooks", "GraphQL Queries"]
    
    # Initialize the analyzer
    analyzer = GeminiTopicAnalyzer()
    
    # Analyze the diff
    result = analyzer.analyze_diff(diff_content, completed, to_learn)
    
    # Print the results
    print(json.dumps(result, indent=2)) 