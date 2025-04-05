# Brain Vibe - AI-Facilitated Code & Learning Graph System

Brain Vibe is a system that monitors code changes, analyzes them using Google Gemini, and maintains knowledge graphs to track your learning journey as a programmer.

## Features

- Monitor code changes via Git
- Analyze code diffs using Google Gemini AI
- Build and maintain per-project learning graphs
- Consolidate knowledge in a global "Master Brain"
- Track learning progress by marking topics as learned
- Visualize learning graphs with search and zoom capabilities

## Architecture

The project consists of two main components:

1. **Backend (Python/FastAPI)**
   - RESTful API endpoints for projects, topics, and the master brain
   - Integration with local Git repositories
   - Google Gemini API integration for code analysis
   - Graph management using NetworkX
   - Data persistence using SQLite

2. **Frontend (React)**
   - Interactive graph visualization using Cytoscape.js
   - Project management interface
   - Code diff analysis submission
   - Topic learning status tracking
   - Search functionality for finding topics

## Setup

### Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn
- Git
- Google Gemini API key

### Backend Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/brain-vibe.git
   cd brain-vibe
   ```

2. Set up the backend:
   ```
   cd backend
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the backend directory with your Gemini API key:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. Start the backend server:
   ```
   uvicorn app.main:app --reload
   ```

   The API will be available at http://localhost:8000

### Frontend Setup

1. Open a new terminal and set up the frontend:
   ```
   cd frontend
   npm install
   ```

2. Start the frontend development server:
   ```
   npm start
   ```

   The web application will be available at http://localhost:3000

## Usage

### Creating a Project

1. Open the web application
2. Click "New Project" and fill in the project details
3. Click "Create Project"

### Analyzing Code

1. Navigate to your project
2. Click "Analyze Code"
3. Paste your Git diff or code changes
4. Optionally add the prompt you gave to AI and its response
5. Click "Analyze Diff"
6. View the new topics identified in your code

### Viewing Learning Graphs

1. Navigate to your project to see its specific learning graph
2. Go to the "Master Brain" to see your consolidated knowledge graph
3. Use the search bar to find specific topics
4. Click on a topic node to view its details

### Marking Topics as Learned

1. Click on a topic node in any graph
2. In the topic detail panel, click "Mark as Learned"
3. The node will change color to indicate it's been learned
4. This status is synchronized across all projects using that topic

## API Endpoints

### Projects

- `GET /api/v1/projects` - Get all projects
- `POST /api/v1/projects` - Create a new project
- `GET /api/v1/projects/{project_id}` - Get a specific project
- `POST /api/v1/projects/{project_id}/analyze-diff` - Analyze code diff for a project
- `GET /api/v1/projects/{project_id}/topics` - Get all topics for a project
- `GET /api/v1/projects/{project_id}/graph` - Get the graph data for a project

### Topics

- `GET /api/v1/topics` - Get all topics
- `GET /api/v1/topics/{topic_id}` - Get a specific topic
- `POST /api/v1/topics/{topic_id}/complete` - Mark a topic as learned/not learned
- `GET /api/v1/topics/{topic_id}/projects` - Get all projects that contain a topic

### Master Brain

- `GET /api/v1/master-graph` - Get the master brain graph data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- FastAPI for the backend framework
- React for the frontend framework
- Cytoscape.js for graph visualization
- Google Gemini for AI-powered code analysis
