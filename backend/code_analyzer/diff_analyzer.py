"""
Diff Analyzer for BrainVibe
Processes Git diffs and extracts programming topics using Gemini AI
"""

import os
import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .gemini_analyzer import GeminiTopicAnalyzer
from ..models.topic import Topic
from ..models.project import Project

logger = logging.getLogger(__name__)

class DiffAnalyzer:
    """
    Analyzes code diffs to extract programming topics
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize the diff analyzer
        
        Args:
            gemini_api_key: Google Gemini API key (optional)
        """
        self.gemini_analyzer = GeminiTopicAnalyzer(api_key=gemini_api_key)
    
    def analyze_diff(self, 
                    project_id: str, 
                    diff_content: str, 
                    file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a code diff to extract programming topics
        
        Args:
            project_id: The ID of the project
            diff_content: The content of the git diff
            file_path: The path of the file being analyzed (optional)
            
        Returns:
            Dictionary containing extracted topics
        """
        if not diff_content:
            logger.warning("Empty diff provided, skipping analysis")
            return {"topics_extracted": 0, "topics": []}
        
        # Filter the diff to remove irrelevant parts (if needed)
        filtered_diff = self._filter_diff(diff_content)
        
        # Get the project and its existing topics
        project = Project.get_by_id(project_id)
        if not project:
            logger.error(f"Project {project_id} not found")
            return {"error": "Project not found", "topics_extracted": 0, "topics": []}
        
        # Get existing topics for the project
        completed_topics = [t.title for t in Topic.get_by_project_and_status(project_id, "learned")]
        to_learn_topics = [t.title for t in Topic.get_by_project_and_status(project_id, "to_learn")]
        
        # Call the Gemini analyzer
        analysis_result = self.gemini_analyzer.analyze_diff(
            filtered_diff,
            completed_topics=completed_topics,
            to_learn_topics=to_learn_topics
        )
        
        # Process the extracted topics
        extracted_topics = []
        for topic_data in analysis_result["topics"]:
            # Create or update the topic in the database
            topic = self._save_topic(project_id, topic_data)
            
            # Add the topic to the result
            extracted_topics.append({
                "id": topic.id,
                "title": topic.title,
                "description": topic.description,
                "prerequisites": topic.prerequisites,
                "status": topic.status
            })
        
        return {
            "topics_extracted": len(extracted_topics),
            "topics": extracted_topics,
            "file_path": file_path
        }
    
    def _filter_diff(self, diff_content: str) -> str:
        """
        Filter the diff to remove irrelevant parts
        
        Args:
            diff_content: The content of the git diff
            
        Returns:
            Filtered diff content
        """
        # Remove binary files
        filtered_lines = []
        skip_current_file = False
        
        for line in diff_content.split('\n'):
            # Check if this is a binary file
            if "Binary files" in line or "diff --git" in line and any(ext in line for ext in ['.jpg', '.png', '.gif', '.pdf', '.zip']):
                skip_current_file = True
                continue
            
            # Check if we're starting a new file
            if line.startswith('diff --git'):
                skip_current_file = False
            
            # Skip lines in binary files
            if skip_current_file:
                continue
            
            # Skip node_modules, dist folders, etc.
            if any(pattern in line for pattern in [
                'node_modules/', 
                '/dist/', 
                '/build/', 
                '/.git/', 
                '/__pycache__/',
                '/venv/',
                '.min.js',
                '.lock'
            ]):
                skip_current_file = True
                continue
            
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _save_topic(self, project_id: str, topic_data: Dict[str, Any]) -> Topic:
        """
        Save a topic to the database
        
        Args:
            project_id: The ID of the project
            topic_data: Data for the topic
            
        Returns:
            The saved Topic object
        """
        # Check if the topic already exists
        existing_topics = Topic.get_by_title_and_project(topic_data["title"], project_id)
        
        if existing_topics:
            # Update the existing topic
            topic = existing_topics[0]
            # Only update the description if it's not empty
            if topic_data["description"] and not topic.description:
                topic.description = topic_data["description"]
            
            # Update prerequisites if they're provided
            if topic_data["prerequisites"]:
                # Convert prerequisite names to IDs
                prereq_ids = []
                for prereq_name in topic_data["prerequisites"]:
                    prereq_topics = Topic.get_by_title_and_project(prereq_name, project_id)
                    if not prereq_topics:
                        # Create the prerequisite topic if it doesn't exist
                        prereq_topic = Topic(
                            title=prereq_name,
                            description="",
                            project_id=project_id,
                            status="to_learn",
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        prereq_topic.save()
                        prereq_ids.append(prereq_topic.id)
                    else:
                        prereq_ids.append(prereq_topics[0].id)
                
                # Set prerequisites
                topic.prerequisites = prereq_ids
            
            # Save the updated topic
            topic.updated_at = datetime.now()
            topic.save()
            
        else:
            # Create a new topic
            topic = Topic(
                title=topic_data["title"],
                description=topic_data["description"],
                project_id=project_id,
                status="to_learn",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Save the topic to get an ID
            topic.save()
            
            # Handle prerequisites
            if topic_data["prerequisites"]:
                prereq_ids = []
                for prereq_name in topic_data["prerequisites"]:
                    # Check if the prerequisite already exists
                    prereq_topics = Topic.get_by_title_and_project(prereq_name, project_id)
                    if not prereq_topics:
                        # Create the prerequisite topic
                        prereq_topic = Topic(
                            title=prereq_name,
                            description="",
                            project_id=project_id,
                            status="to_learn",
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        prereq_topic.save()
                        prereq_ids.append(prereq_topic.id)
                    else:
                        prereq_ids.append(prereq_topics[0].id)
                
                # Update prerequisites and save again
                topic.prerequisites = prereq_ids
                topic.save()
        
        return topic 