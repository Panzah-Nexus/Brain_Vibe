Verbose Project Description
Below is a comprehensive system breakdown. Think of this as a “Technical Product Spec” you could hand off to a software engineer. It contains both an overview of the conceptual workflows and explicit requirements for each subsystem.

Overview
The project is a platform that:

Monitors AI-Generated Code Changes in near-real time (or via commits).

Identifies New Topics to learn based on these code changes.

Builds & Updates a “TO LEARN” Knowledge Graph that highlights how newly introduced topics relate to previously known ones.

Tracks Progress as users mark topics as “learned,” eventually moving them from “TO LEARN” to “COMPLETED LEARN.”

Visualizes each project’s learning topics in a graph-like interface, while also maintaining a master brain of all topics across all projects, merging duplicates.

The value proposition: People can quickly generate code with AI, yet keep track of the underlying principles and technologies they need to master (or are in the process of mastering).

Core Components
Integration with Code Generation / Editing Tools

The system should capture user prompts and AI responses.

Ideally, it ties into a version control layer (e.g., Git). After each generated chunk of code, the system detects “what changed” in the codebase.

The system must parse or store these changes (diffs) in a structured manner.

Topic Extraction & Dependency Analysis

Once code changes are captured, we send relevant context (code diffs, the entire project snippet, or both) to an AI endpoint called “Gemini API.”

Gemini’s job is to figure out the set of concepts / topics newly introduced (or significantly expanded) by these code changes. For example, “multithreading in C++,” “REST API calls with Axios,” “OAuth 2.0 in Python Flask,” etc.

The AI also identifies dependencies among topics. For instance, “Multithreading in C++” might depend on “Basic Threading Concepts” which in turn depends on “Memory Management in C++.”

The API returns data in a structured format (for instance, JSON) indicating:

A list of newly discovered topics.

Their prerequisite topics.

Potentially, a short description or summary of each.

Graph Storage

Each project has its own knowledge graph. The graph’s data structure is expected to be a DAG, though cycles are unlikely.

A topic node includes:

Topic ID (unique identifier, possibly a string like “C++:Multithreading:Basics”)

Display Name (e.g., “C++ Multithreading Basics”)

Status: “Not Learned,” “In Progress,” or “Learned”

Project Association: This node belongs to “Project ABC,” or “Global” if it’s in the master brain.

Dependencies: Other Topic IDs that must be learned first.

A “master brain” merges all topics from all projects, ensuring no duplicates. If two or more projects yield the same topic ID, we treat them as the same node in the master brain (and unify progress status accordingly).

TO LEARN and COMPLETED LEARN Lists

The system organizes topic nodes in two lists (or states):

TO LEARN: All topics recognized as not yet learned.

COMPLETED LEARN: All topics the user (or team) has indicated they understand.

If a topic node is moved to “COMPLETED,” it should visually appear with a different style (e.g., green highlight, or visually faded).

The user can always override or revert a topic’s status if they realize they need more study.

Version Control & Prompt Tracking

The system must link changes to the user’s prompts. For instance, each time the user types a prompt into Cursor (or whichever editor), that prompt plus the AI’s code output is stored.

When the user commits or when the system triggers on each generation, the code diff is analyzed by the Gemini API.

User Interface

Main UI for the knowledge graph:

Shows nodes as topics.

Arrows or lines indicate dependencies.

Nodes can be color-coded or styled by status.

Clicking a node can bring up short descriptions or references.

Project Overview:

For each project, a page or view that specifically shows the learning graph relevant to that codebase.

Summaries of the top-level newly introduced topics.

A toggle or search function to navigate or filter topics.

Master Brain / Global Graph:

An aggregate of all topics from all projects.

Duplicate topics (e.g., “Concurrency in C++”) are merged into a single node, so your “completed” status of concurrency is recognized across all codebases.

Topic Detail Page: (optional but valuable)

Might display more in-depth definitions or recommended resources for each topic.

Potentially includes references to the code lines that introduced the topic.

Marking a Topic Complete

The system must allow the user to indicate “I’ve learned this!” on any topic node.

Alternatively, if the user works heavily with code that references a topic, the system might suggest marking that topic as learned. But final confirmation remains with the user.

Collaboration & Team Workflow

If multiple users are on the same project, a shared knowledge graph is used.

The progress (which topics are learned) can be either per-user or for the entire team.

The system design should allow for future integration with user roles or multi-user assignment of tasks.

Master Brain Mechanics

Whenever a new topic node is created in any project’s graph, the system checks the master brain to see if an equivalent topic node already exists. If it does:

Merge them, or link them so that the user’s “learned” state is consistent.

The master brain can be viewed as a global reference library.

Each node in the master brain can hold aggregated information such as a universal summary or references, plus a list of projects where it appears.

Data Persistence

The project’s structure, all topics, and their dependencies must be stored in a database (SQL or NoSQL) or a suitable graph database (Neo4j, for instance).

Each time the code changes are analyzed, new topics might be appended or existing ones updated.

For each project, maintain:

A unique ID (repository name, path, or user-defined).

A pointer to that project’s knowledge graph or subgraph.

Snapshots or references to the code prompts.

Security & Privacy

Depending on the environment, code snippets could contain proprietary information. The system should have access control and potential encryption if needed.

Consider storing minimal diffs rather than entire code content, depending on compliance needs.

Edge Cases & Other Requirements

Topics that appear repeatedly in small ways. For instance, “Basic if-else statements” in many new code changes. The system should handle that gracefully (not duplicating infinite times).

Overlapping or general vs. specific topics. The AI might need to unify “Pointers in C++” and “Pointer basics in C++.” The exact approach to synonyms is up to Gemini’s design or a manual curation step.

Performance concerns if the user has a very large codebase or repeatedly triggers prompts. We’ll need caching or minimal diffs to keep overhead manageable.

Example Workflow (Illustrative)
User or Team starts new project

The system creates an empty graph.

User writes first prompt in Cursor: “Write a C++ Hello World program.”

AI returns code. The system sees new code lines referencing basic C++ syntax.

Gemini processes the diff: “Hello World in C++” → Topics: Basic I/O in C++ → no major dependencies.

The topic “Basic I/O in C++” is added to the graph in the “TO LEARN” state.

Master brain is updated if that topic doesn’t already exist.

Next prompt: “Now add concurrency using threads.”

AI code changes show <thread>, concurrency library usage.

Gemini identifies “multithreading in C++,” depends on “basic threading concepts,” possibly “memory management concurrency.”

The system updates the project graph with new nodes and dependencies, all in “TO LEARN.”

Master brain merges or adds these nodes as needed.

User notices they already know concurrency and sets “multithreading in C++” to “COMPLETED.”

The node in the project graph becomes completed (green).

The master brain marks concurrency as completed for that user (or globally, depending on design).

