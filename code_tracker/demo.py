import os
import sys
import time
from pathlib import Path
import subprocess
from .management.commands.init_project import init_project
from .cursor_integration import CursorIntegration

def run_demo():
    print("🚀 Starting BrainVibe Demo 🚀")
    print("This demo will show how BrainVibe tracks code changes and builds learning graphs.")
    
    # Create a temporary demo project
    demo_dir = Path("brainvibe_demo")
    if demo_dir.exists():
        print("Removing existing demo directory...")
        subprocess.run(["rm", "-rf", str(demo_dir)])
    
    demo_dir.mkdir()
    print(f"Created demo directory at {demo_dir.absolute()}")
    
    # Initialize the project
    print("\n1️⃣ Initializing project with BrainVibe...")
    if not init_project(str(demo_dir)):
        print("Failed to initialize project")
        sys.exit(1)
    
    # Set up Cursor integration
    print("\n2️⃣ Setting up Cursor integration...")
    integration = CursorIntegration(str(demo_dir))
    if not integration.setup_cursor_integration():
        print("Failed to set up Cursor integration")
        sys.exit(1)
    
    # Create some sample code files
    print("\n3️⃣ Creating sample code files...")
    
    # Python file with basic concepts
    python_code = """import threading
import time

def worker():
    print("Thread started")
    time.sleep(1)
    print("Thread finished")

# Create and start threads
threads = []
for i in range(3):
    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()

# Wait for all threads to complete
for t in threads:
    t.join()
"""
    
    # JavaScript file with async concepts
    js_code = """const fetch = require('node-fetch');

async function getData() {
    try {
        const response = await fetch('https://api.example.com/data');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error:', error);
    }
}

// Using the async function
getData().then(data => console.log(data));
"""
    
    # Write the files
    (demo_dir / "python_threading.py").write_text(python_code)
    (demo_dir / "js_async.js").write_text(js_code)
    
    print("\n4️⃣ Tracking initial code changes...")
    integration.track_changes(str(demo_dir / "python_threading.py"), python_code)
    integration.track_changes(str(demo_dir / "js_async.js"), js_code)
    
    print("\n5️⃣ Making some changes to demonstrate tracking...")
    time.sleep(2)  # Simulate time passing
    
    # Modify the Python file to add more concepts
    modified_python = python_code + """
# Adding some error handling
try:
    for t in threads:
        t.start()
except Exception as e:
    print(f"Error starting threads: {e}")
"""
    
    integration.track_changes(str(demo_dir / "python_threading.py"), modified_python)
    
    print("\n🎉 Demo Complete! 🎉")
    print("\nWhat happened:")
    print("1. Created a new project with BrainVibe integration")
    print("2. Set up Cursor integration for tracking changes")
    print("3. Created sample code files with different programming concepts")
    print("4. Tracked initial code changes")
    print("5. Made modifications to demonstrate change tracking")
    
    print("\nNext steps:")
    print("1. Check the .brainvibe directory for configuration")
    print("2. Look at the git history to see tracked changes")
    print("3. The analyze_diff command should have run automatically")
    print("4. Your learning graph should be updated with new topics")
    
    print("\nTo clean up:")
    print(f"rm -rf {demo_dir}")

if __name__ == "__main__":
    run_demo() 