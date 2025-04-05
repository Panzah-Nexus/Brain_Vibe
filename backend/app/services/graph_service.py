from typing import Dict, List, Any, Optional, Tuple, Set
import networkx as nx
from app.database import db
from app.services.gemini_service import normalize_topic_id, find_similar_topic
from app.models.models import Topic


def process_topics_from_gemini(project_id: str, gemini_response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process topics from Gemini response and add them to the project and master graphs.
    
    Args:
        project_id: The project ID to add topics to
        gemini_response: The response from Gemini containing new topics
    
    Returns:
        List[Dict[str, Any]]: List of processed topics
    """
    new_topics = []
    
    # Get existing topics
    existing_topics = db.get_all_topics()
    
    # Process each topic from Gemini response
    for topic_data in gemini_response.get("new_topics", []):
        # Normalize the topic ID
        original_topic_id = topic_data.get("topic_id", "")
        if not original_topic_id:
            continue
        
        topic_id = normalize_topic_id(original_topic_id)
        
        # Check if a similar topic already exists
        similar_topic_id = find_similar_topic(topic_id, existing_topics)
        
        if similar_topic_id:
            # Use the existing topic ID
            topic_id = similar_topic_id
            topic = existing_topics[similar_topic_id]
            
            # Update the topic with any new information
            if "short_description" in topic_data and not topic.get("short_description"):
                topic["short_description"] = topic_data["short_description"]
            
            # Add the project to the topic's projects list if not already there
            if project_id not in topic.get("projects", []):
                projects = topic.get("projects", [])
                projects.append(project_id)
                topic["projects"] = projects
                
                # Save the updated topic
                db.save_topic(topic_id, topic)
            
            # Add the topic to the project if not already there
            db.add_topic_to_project(project_id, topic_id)
            
            # Add the topic to the result list
            new_topics.append(topic)
        else:
            # Create a new topic
            new_topic = {
                "topic_id": topic_id,
                "display_name": topic_data.get("display_name", topic_id),
                "status": "NOT_LEARNED",
                "prerequisites": [],
                "short_description": topic_data.get("short_description", ""),
                "projects": [project_id]
            }
            
            # Process prerequisites
            for prereq_id in topic_data.get("prerequisites", []):
                if not prereq_id:
                    continue
                
                normalized_prereq_id = normalize_topic_id(prereq_id)
                similar_prereq_id = find_similar_topic(normalized_prereq_id, existing_topics)
                
                if similar_prereq_id:
                    # Use the existing prerequisite topic
                    if similar_prereq_id not in new_topic["prerequisites"]:
                        new_topic["prerequisites"].append(similar_prereq_id)
                    
                    # Add the prerequisite to the project if not already there
                    db.add_topic_to_project(project_id, similar_prereq_id)
                else:
                    # Create a placeholder prerequisite topic
                    prereq_topic = {
                        "topic_id": normalized_prereq_id,
                        "display_name": prereq_id.replace("_", " ").title(),
                        "status": "NOT_LEARNED",
                        "prerequisites": [],
                        "short_description": "",
                        "projects": [project_id]
                    }
                    
                    # Save the prerequisite topic
                    db.save_topic(normalized_prereq_id, prereq_topic)
                    
                    # Add the prerequisite to the project
                    db.add_topic_to_project(project_id, normalized_prereq_id)
                    
                    # Add the prerequisite to the new topic's prerequisites
                    if normalized_prereq_id not in new_topic["prerequisites"]:
                        new_topic["prerequisites"].append(normalized_prereq_id)
                    
                    # Update existing topics dictionary
                    existing_topics[normalized_prereq_id] = prereq_topic
            
            # Save the new topic
            db.save_topic(topic_id, new_topic)
            
            # Add the topic to the project
            db.add_topic_to_project(project_id, topic_id)
            
            # Add the topic to the result list
            new_topics.append(new_topic)
            
            # Update existing topics dictionary
            existing_topics[topic_id] = new_topic
    
    # Update the graph structures
    update_graph_structures(project_id)
    
    return new_topics


def update_graph_structures(project_id: str):
    """
    Update the graph structures for a project and the master brain.
    
    Args:
        project_id: The project ID to update graphs for
    """
    # Get the project topics
    project_topics = db.get_project_topics(project_id)
    
    # Update the project graph
    project_graph = nx.DiGraph()
    
    for topic in project_topics:
        topic_id = topic["topic_id"]
        project_graph.add_node(topic_id, **topic)
        
        # Add edges for prerequisites
        for prereq_id in topic.get("prerequisites", []):
            if prereq_id in [t["topic_id"] for t in project_topics]:
                project_graph.add_edge(prereq_id, topic_id)
    
    # Save the project graph
    db.project_graphs[project_id] = project_graph
    
    # Update the master brain
    all_topics = db.get_all_topics()
    master_brain = nx.DiGraph()
    
    for topic_id, topic in all_topics.items():
        master_brain.add_node(topic_id, **topic)
        
        # Add edges for prerequisites
        for prereq_id in topic.get("prerequisites", []):
            if prereq_id in all_topics:
                master_brain.add_edge(prereq_id, topic_id)
    
    # Save the master brain
    db.master_brain = master_brain 