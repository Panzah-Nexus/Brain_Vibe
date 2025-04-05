import os
import json
import networkx as nx
from sqlitedict import SqliteDict
from typing import Dict, List, Optional, Set, Any

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

# Initialize SQLite databases for persistent storage
projects_db = SqliteDict('./data/projects.sqlite', autocommit=True)
topics_db = SqliteDict('./data/topics.sqlite', autocommit=True)

# In-memory graphs
project_graphs: Dict[str, nx.DiGraph] = {}
master_brain = nx.DiGraph()


def load_graphs():
    """Load all graphs from persistent storage on startup."""
    # Load topics
    for topic_id, topic_data in topics_db.items():
        topic_dict = json.loads(topic_data)
        master_brain.add_node(topic_id, **topic_dict)
        
        # Add edges for prerequisites
        for prereq_id in topic_dict.get("prerequisites", []):
            if prereq_id in master_brain:
                master_brain.add_edge(prereq_id, topic_id)
    
    # Load projects and their topics
    for project_id, project_data in projects_db.items():
        project_dict = json.loads(project_data)
        
        # Create project graph
        project_graphs[project_id] = nx.DiGraph()
        
        # Add topics to project graph
        for topic_id in project_dict.get("topic_ids", []):
            if topic_id in topics_db:
                topic_dict = json.loads(topics_db[topic_id])
                project_graphs[project_id].add_node(topic_id, **topic_dict)
                
                # Add edges for prerequisites
                for prereq_id in topic_dict.get("prerequisites", []):
                    if prereq_id in project_graphs[project_id]:
                        project_graphs[project_id].add_edge(prereq_id, topic_id)


def save_project(project_id: str, project_data: dict):
    """Save project data to persistent storage."""
    projects_db[project_id] = json.dumps(project_data)


def save_topic(topic_id: str, topic_data: dict):
    """Save topic data to persistent storage."""
    topics_db[topic_id] = json.dumps(topic_data)


def add_topic_to_project(project_id: str, topic_id: str):
    """Add a topic to a project."""
    if project_id not in projects_db:
        return False
    
    project_data = json.loads(projects_db[project_id])
    if topic_id not in project_data.get("topic_ids", []):
        topic_ids = project_data.get("topic_ids", [])
        topic_ids.append(topic_id)
        project_data["topic_ids"] = topic_ids
        projects_db[project_id] = json.dumps(project_data)
        
        # Update topic's projects list
        if topic_id in topics_db:
            topic_data = json.loads(topics_db[topic_id])
            if project_id not in topic_data.get("projects", []):
                projects = topic_data.get("projects", [])
                projects.append(project_id)
                topic_data["projects"] = projects
                topics_db[topic_id] = json.dumps(topic_data)
    
    return True


def get_all_projects():
    """Get all projects."""
    return {project_id: json.loads(project_data) for project_id, project_data in projects_db.items()}


def get_project(project_id: str):
    """Get a project by ID."""
    if project_id in projects_db:
        return json.loads(projects_db[project_id])
    return None


def get_all_topics():
    """Get all topics."""
    return {topic_id: json.loads(topic_data) for topic_id, topic_data in topics_db.items()}


def get_topic(topic_id: str):
    """Get a topic by ID."""
    if topic_id in topics_db:
        return json.loads(topics_db[topic_id])
    return None


def get_project_topics(project_id: str):
    """Get all topics for a project."""
    project = get_project(project_id)
    if not project:
        return []
    
    return [get_topic(topic_id) for topic_id in project.get("topic_ids", []) if topic_id in topics_db]


def update_topic_status(topic_id: str, status: str):
    """Update a topic's status."""
    if topic_id not in topics_db:
        return False
    
    topic_data = json.loads(topics_db[topic_id])
    topic_data["status"] = status
    topics_db[topic_id] = json.dumps(topic_data)
    
    # Update the topic in the master brain
    if topic_id in master_brain:
        master_brain.nodes[topic_id]["status"] = status
    
    # Update the topic in all project graphs
    for project_id in topic_data.get("projects", []):
        if project_id in project_graphs and topic_id in project_graphs[project_id]:
            project_graphs[project_id].nodes[topic_id]["status"] = status
    
    return True


def get_master_brain_data():
    """Get the master brain data as a dict for JSON serialization."""
    nodes = []
    edges = []
    
    for node_id in master_brain.nodes():
        node_data = master_brain.nodes[node_id]
        nodes.append({
            "id": node_id,
            **node_data
        })
    
    for source, target in master_brain.edges():
        edges.append({
            "source": source,
            "target": target
        })
    
    return {
        "nodes": nodes,
        "edges": edges
    }


def get_project_graph_data(project_id: str):
    """Get a project's graph data as a dict for JSON serialization."""
    if project_id not in project_graphs:
        if project_id in projects_db:
            # Initialize the project graph if it exists but hasn't been loaded
            project_graphs[project_id] = nx.DiGraph()
            project_data = json.loads(projects_db[project_id])
            
            for topic_id in project_data.get("topic_ids", []):
                if topic_id in topics_db:
                    topic_dict = json.loads(topics_db[topic_id])
                    project_graphs[project_id].add_node(topic_id, **topic_dict)
                    
                    # Add edges for prerequisites
                    for prereq_id in topic_dict.get("prerequisites", []):
                        if prereq_id in project_graphs[project_id]:
                            project_graphs[project_id].add_edge(prereq_id, topic_id)
        else:
            return {"nodes": [], "edges": []}
    
    nodes = []
    edges = []
    
    for node_id in project_graphs[project_id].nodes():
        node_data = project_graphs[project_id].nodes[node_id]
        nodes.append({
            "id": node_id,
            **node_data
        })
    
    for source, target in project_graphs[project_id].edges():
        edges.append({
            "source": source,
            "target": target
        })
    
    return {
        "nodes": nodes,
        "edges": edges
    }


# Initialize graphs on module load
load_graphs() 