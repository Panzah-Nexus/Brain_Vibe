#!/usr/bin/env python3
"""
Quick test to verify BrainVibe is working
Run this for a rapid sanity check
"""

import subprocess
import requests
import sys

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def quick_check():
    print("🧠 BrainVibe Quick Check\n")
    
    checks = {
        "Backend Running": False,
        "CLI Installed": False,
        "Frontend Available": False
    }
    
    # Check backend
    try:
        r = requests.get("http://localhost:8000/api/hello/", timeout=1)
        checks["Backend Running"] = r.status_code == 200
    except:
        pass
    
    # Check CLI
    try:
        result = subprocess.run(["which", "brainvibe"], capture_output=True)
        checks["CLI Installed"] = result.returncode == 0
    except:
        pass
    
    # Check frontend
    try:
        r = requests.get("http://localhost:5173", timeout=1)
        checks["Frontend Available"] = r.status_code == 200
    except:
        pass
    
    # Print results
    for check, passed in checks.items():
        status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"{status} {check}")
    
    print("\n" + "="*40)
    
    if not checks["Backend Running"]:
        print(f"{YELLOW}Start backend:{RESET}")
        print("  cd backend && source venv/bin/activate")
        print("  python manage.py runserver\n")
    
    if not checks["CLI Installed"]:
        print(f"{YELLOW}Install CLI:{RESET}")
        print("  cd cli && pip install -e .\n")
    
    if not checks["Frontend Available"]:
        print(f"{YELLOW}Start frontend:{RESET}")
        print("  cd frontend && npm run dev\n")
    
    if all(checks.values()):
        print(f"{GREEN}Everything is running! You can now:{RESET}")
        print("  1. Open http://localhost:5173 in browser")
        print("  2. Create a project")
        print("  3. Use: brainvibe init --project-id YOUR_ID")
        print("  4. Use: brainvibe track --watch")

if __name__ == "__main__":
    quick_check()
