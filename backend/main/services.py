"""
Service functions for the Brain Vibe application.
These services coordinate between the models, utils, and views.
"""
import logging
from typing import Dict, List, Any, Optional
from .models import Project, Topic, CodeChange
from .utils import git_utils, llm_utils

# Set up logger
logger = logging.getLogger(__name__)

def analyze_project_changes(project_id: str, repo_path: str) -> Dict[str, Any]:
    """
    Analyze changes in a project's repository and extract learning topics.
    
    Args:
        project_id: The ID of the project
        repo_path: Path to the project's Git repository
        
    Returns:
        A dictionary with the analysis results
    """
    logger.info(f"Analyzing changes for project {project_id} at {repo_path}")
    
    # Get project
    try:
        project = Project.objects.get(project_id=project_id)
    except Project.DoesNotExist:
        logger.error(f"Project with ID {project_id} not found")
        return {"error": f"Project with ID {project_id} not found"}
    
    # Get diff
    diff_text = git_utils.get_repo_diffs(repo_path)
    if not diff_text:
        logger.warning(f"No changes found in repository {repo_path}")
        return {"warning": "No changes found in repository"}
    
    # Prepare project context
    project_context = {
        "project_id": project.project_id,
        "name": project.name,
        "existing_topics": list(Topic.objects.filter(project=project).values('topic_id', 'title', 'status'))
    }
    
    # Analyze diff and extract topics
    extracted_topics = llm_utils.analyze_diff(diff_text, project_context)
    if not extracted_topics:
        logger.info(f"No new topics extracted from changes in repository {repo_path}")
        return {
            "message": "No new topics extracted",
            "changes_found": True,
            "topics_extracted": 0
        }
    
    # In the future, we'll save these topics to the database
    # For now, just return them
    return {
        "message": "Successfully analyzed changes",
        "changes_found": True,
        "topics_extracted": len(extracted_topics),
        "topics": extracted_topics
    }


def process_and_save_topics(project_id: str, topics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process and save extracted topics to the database.
    This is a placeholder for future implementation.
    
    Args:
        project_id: The ID of the project
        topics: List of topic dictionaries extracted from the LLM
        
    Returns:
        A dictionary with the results
    """
    logger.info(f"Processing and saving {len(topics)} topics for project {project_id}")
    
    # This is a placeholder for the actual implementation
    # In the future, we would:
    # 1. Check for existing topics
    # 2. Create new topics
    # 3. Update existing topics
    # 4. Set up prerequisites relationships
    
    try:
        project = Project.objects.get(project_id=project_id)
        
        # New topics to be created
        new_topics = []
        # Existing topics to be updated
        updated_topics = []
        
        for topic_data in topics:
            topic_id = topic_data.get("topic_id")
            if not topic_id:
                logger.warning(f"Topic without ID: {topic_data}")
                continue
                
            # Check if topic already exists
            try:
                topic = Topic.objects.get(topic_id=topic_id)
                # Update existing topic (in the future)
                updated_topics.append(topic)
            except Topic.DoesNotExist:
                # Create new topic
                topic = Topic(
                    topic_id=topic_id,
                    title=topic_data.get("title", ""),
                    description=topic_data.get("description", ""),
                    project=project,
                    status="not_learned"
                )
                # We'll save after setting up prerequisites
                new_topics.append(topic)
        
        # Now, save all the new topics
        # Topic.objects.bulk_create(new_topics)
        
        # And set up prerequisites (future implementation)
        # for topic_data in topics:
        #     if "prerequisites" in topic_data and topic_data["prerequisites"]:
        #         topic = Topic.objects.get(topic_id=topic_data["topic_id"])
        #         for prereq_id in topic_data["prerequisites"]:
        #             try:
        #                 prereq = Topic.objects.get(topic_id=prereq_id)
        #                 topic.prerequisites.add(prereq)
        #             except Topic.DoesNotExist:
        #                 logger.warning(f"Prerequisite topic {prereq_id} not found")
        
        return {
            "message": "Topics processed successfully",
            "new_topics": len(new_topics),
            "updated_topics": len(updated_topics)
        }
        
    except Project.DoesNotExist:
        logger.error(f"Project with ID {project_id} not found")
        return {"error": f"Project with ID {project_id} not found"}
    except Exception as e:
        logger.exception(f"Error processing topics: {e}")
        return {"error": str(e)}

def analyze_code_change(
    project_id: str, 
    file_path: str, 
    diff_content: str, 
    change_source: str = 'manual_edit'
) -> Dict[str, Any]:
    """
    Analyze a code change and extract learning topics.
    
    Args:
        project_id: The ID of the project
        file_path: Path to the file that was changed
        diff_content: The diff content to analyze
        change_source: Source of the change (e.g., manual_edit, git_commit, scheduled_scan)
        
    Returns:
        A dictionary with the analysis results
    """
    logger.info(f"Analyzing code change for project {project_id}, file {file_path}, source {change_source}")
    
    try:
        # Get the project
        project = Project.objects.get(project_id=project_id)
        
        # Generate a unique ID for this change
        import hashlib
        import time
        hash_input = f"{project_id}_{file_path}_{time.time()}"
        change_id = hashlib.sha256(hash_input.encode()).hexdigest()[:24]
        
        # Create metadata
        from datetime import datetime
        metadata = {
            "file_path": file_path,
            "timestamp": datetime.now().isoformat(),
            "change_source": change_source
        }
        
        # Create a CodeChange record
        code_change = CodeChange.objects.create(
            project=project,
            change_source=change_source,
            change_id=change_id,
            summary=f"Changes to {file_path}",
            diff_content=diff_content,
            metadata=metadata,
            is_analyzed=False
        )
        
        # Prepare project context
        project_context = {
            "project_id": project.project_id,
            "name": project.name,
            "existing_topics": list(Topic.objects.filter(project=project).values('topic_id', 'title', 'status'))
        }
        
        # Analyze the diff and extract topics
        extracted_topics = llm_utils.analyze_diff(diff_content, project_context)
        
        if not extracted_topics:
            logger.info(f"No topics extracted from code change for {file_path}")
            code_change.is_analyzed = True
            code_change.save()
            return {
                "status": "success",
                "change_id": change_id,
                "message": "No new topics extracted",
                "topics_extracted": 0
            }
        
        # Process and save the extracted topics
        result = process_and_save_topics(project_id, extracted_topics)
        
        # Update the CodeChange record to mark it as analyzed
        code_change.is_analyzed = True
        code_change.save()
        
        # Add the extracted topics to the CodeChange record
        for topic_data in extracted_topics:
            topic_id = topic_data.get("topic_id")
            if topic_id:
                try:
                    topic = Topic.objects.get(topic_id=topic_id)
                    code_change.extracted_topics.add(topic)
                except Topic.DoesNotExist:
                    logger.warning(f"Topic with ID {topic_id} not found")
        
        return {
            "status": "success",
            "change_id": change_id,
            "topics_extracted": len(extracted_topics),
            "topics": extracted_topics
        }
        
    except Project.DoesNotExist:
        logger.error(f"Project with ID {project_id} not found")
        return {
            "status": "error",
            "message": f"Project with ID {project_id} not found"
        }
    except Exception as e:
        logger.exception(f"Error analyzing code change: {e}")
        return {
            "status": "error",
            "message": str(e)
        } 