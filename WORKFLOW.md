Complete User Flow for BrainVibe
Now that we have everything set up, let's walk through the complete user flow:
1. Project Setup and Initialization
Create a coding project: The user creates a new project folder
Initialize BrainVibe: Run brainvibe init in the project folder
This creates a .brainvibe directory with configuration
Connects the project to the backend database
Sets up git tracking if needed
2. Track Code Changes
Start tracking: Run brainvibe track in the project folder
This monitors file changes in real-time
When changes are detected, they're staged in git
The CLI creates temporary git commits to generate diffs
These diffs are sent to the backend for analysis
Write code: The user writes code normally (or uses AI tools like Cursor)
In our case, we created React components and utility files
The tracker detects these changes automatically
Gemini Analysis: The backend processes diffs with Gemini API
Gemini identifies programming topics from the code
Example topics from our React code might include:
React Hooks (useState, useEffect)
React Context API
JWT Authentication
Async/Await in JavaScript
Middleware patterns
Error handling
Caching strategies
3. Knowledge Graph Building
Topic Extraction: Gemini identifies topics and their relationships
Topics are stored in the database
Dependencies between topics are established (prerequisites)
Master Brain: All topics across all projects are aggregated
Duplicate topics are merged
A global knowledge graph is maintained
4. Learning Progress Tracking
View Topics: The user visits the web interface (http://localhost:5173)
Project-specific topics are shown on project pages
All topics are shown in the Master Brain view
Mark as Learned: The user marks topics they already know
This moves topics from "TO LEARN" to "COMPLETED LEARN"
Progress is tracked across all projects
Get Tutorials: For unfamiliar topics, the user can click "View Tutorial"
Gemini generates personalized tutorials
These tutorials reference code from the user's project
Prerequisites are suggested for topics that depend on others
5. Personalized Learning Journey
Complete Tutorials: The user works through tutorials
Mark Topics as Learned: As they learn, they update their progress
Knowledge Graph Growth: The Master Brain shows their growing expertise
Advantages of BrainVibe
Automated Detection: No need to manually track what you need to learn
Personalized Tutorials: Tutorials reference your own code, making them relevant
Knowledge Graph: Visualize the relationships between topics
Cross-Project Learning: Track progress across all your coding projects
AI-Powered Analysis: Leverage Gemini's understanding of programming concepts
This workflow allows developers to generate code quickly with AI assistants while ensuring they understand the underlying concepts, creating a powerful learning journey alongside their development work.