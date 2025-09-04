#!/usr/bin/env python3
"""
Individual Component Testing for BrainVibe
Tests each part separately to identify issues
"""

import os
import sys
import json
import tempfile
import subprocess
import requests
import time
import shutil
from pathlib import Path
from datetime import datetime

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(message, success=True):
    """Print colored test result"""
    if success:
        print(f"{GREEN}✓{RESET} {message}")
    else:
        print(f"{RED}✗{RESET} {message}")

def print_section(title):
    """Print section header"""
    print(f"\n{BLUE}{'='*50}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'='*50}{RESET}\n")

class BrainVibeTestSuite:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.test_project_id = None
        self.test_dir = None
        self.errors = []
        
    def test_backend_health(self):
        """Test 1: Check if backend is running"""
        print_section("TEST 1: Backend Health Check")
        
        try:
            # Check if backend is running
            response = requests.get(f"{self.backend_url}/api/hello/", timeout=5)
            if response.status_code == 200:
                print_test("Backend is running")
                return True
            else:
                print_test(f"Backend returned status {response.status_code}", False)
                return False
        except requests.ConnectionError:
            print_test("Backend is not running! Start it with:", False)
            print(f"  {YELLOW}cd backend && python manage.py runserver{RESET}")
            return False
        except Exception as e:
            print_test(f"Error: {e}", False)
            return False
    
    def test_api_endpoints(self):
        """Test 2: Check API endpoints"""
        print_section("TEST 2: API Endpoints")
        
        tests_passed = True
        
        # Test GET projects
        try:
            response = requests.get(f"{self.backend_url}/api/projects/")
            if response.status_code == 200:
                print_test("GET /api/projects/ works")
            else:
                print_test(f"GET /api/projects/ failed: {response.status_code}", False)
                tests_passed = False
        except Exception as e:
            print_test(f"GET /api/projects/ error: {e}", False)
            tests_passed = False
        
        # Test POST project
        try:
            project_data = {
                "name": f"Test Project {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "Testing BrainVibe functionality",
                "github_url": "https://github.com/test/test"
            }
            response = requests.post(
                f"{self.backend_url}/api/projects/",
                json=project_data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code in [200, 201]:
                self.test_project_id = response.json().get('project_id')
                print_test(f"POST /api/projects/ works (ID: {self.test_project_id})")
            else:
                print_test(f"POST /api/projects/ failed: {response.status_code}", False)
                print(f"  Response: {response.text}")
                tests_passed = False
        except Exception as e:
            print_test(f"POST /api/projects/ error: {e}", False)
            tests_passed = False
        
        return tests_passed
    
    def test_cli_installation(self):
        """Test 3: Check CLI installation"""
        print_section("TEST 3: CLI Installation")
        
        try:
            result = subprocess.run(
                ["which", "brainvibe"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                cli_path = result.stdout.strip()
                print_test(f"CLI installed at: {cli_path}")
                return True
            else:
                print_test("CLI not found! Install it with:", False)
                print(f"  {YELLOW}cd cli && pip install -e .{RESET}")
                return False
        except Exception as e:
            print_test(f"Error checking CLI: {e}", False)
            return False
    
    def test_cli_functionality(self):
        """Test 4: Test CLI commands"""
        print_section("TEST 4: CLI Functionality")
        
        if not self.test_project_id:
            print_test("No project ID available (create project first)", False)
            return False
        
        # Create temporary test directory
        self.test_dir = tempfile.mkdtemp(prefix="brainvibe_test_")
        print(f"Testing in: {self.test_dir}")
        os.chdir(self.test_dir)
        
        tests_passed = True
        
        # Test init command
        try:
            result = subprocess.run(
                ["brainvibe", "init", "--project-id", self.test_project_id],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print_test("brainvibe init successful")
                
                # Verify files created
                if Path(".brainvibe/config.json").exists():
                    print_test("  - config.json created")
                else:
                    print_test("  - config.json missing", False)
                    tests_passed = False
                
                if Path(".brainvibeignore").exists():
                    print_test("  - .brainvibeignore created")
                else:
                    print_test("  - .brainvibeignore missing", False)
                    tests_passed = False
                
                if Path(".git").exists():
                    print_test("  - Git repository initialized")
                else:
                    print_test("  - Git not initialized", False)
                    tests_passed = False
            else:
                print_test(f"brainvibe init failed: {result.stderr}", False)
                tests_passed = False
        except Exception as e:
            print_test(f"Error running init: {e}", False)
            tests_passed = False
        
        return tests_passed
    
    def test_tracking(self):
        """Test 5: Test code tracking"""
        print_section("TEST 5: Code Tracking")
        
        if not self.test_dir:
            print_test("No test directory (run CLI test first)", False)
            return False
        
        os.chdir(self.test_dir)
        
        # Create sample code
        with open("test.py", "w") as f:
            f.write("""
import asyncio
import threading

async def process_data(data):
    # This demonstrates async/await
    await asyncio.sleep(1)
    return data * 2

def thread_worker():
    # This demonstrates threading
    print("Worker thread running")

if __name__ == "__main__":
    # Multi-threading example
    thread = threading.Thread(target=thread_worker)
    thread.start()
""")
        
        print_test("Sample code file created")
        
        # Test tracking
        try:
            result = subprocess.run(
                ["brainvibe", "track", "--one-shot"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print_test("Code tracking successful")
                
                # Check if topics were extracted (if API returns them)
                if self.test_project_id:
                    time.sleep(2)  # Give backend time to process
                    response = requests.get(
                        f"{self.backend_url}/api/projects/{self.test_project_id}/topics/"
                    )
                    if response.status_code == 200:
                        topics = response.json()
                        if topics:
                            print_test(f"  - {len(topics)} topics extracted")
                        else:
                            print_test("  - No topics (Gemini API key needed?)", False)
                    else:
                        print_test(f"  - Failed to fetch topics: {response.status_code}", False)
            else:
                print_test(f"Tracking failed: {result.stderr}", False)
                return False
        except subprocess.TimeoutExpired:
            print_test("Tracking timed out", False)
            return False
        except Exception as e:
            print_test(f"Error during tracking: {e}", False)
            return False
        
        return True
    
    def test_gemini_integration(self):
        """Test 6: Check Gemini API integration"""
        print_section("TEST 6: Gemini Integration")
        
        # Check if GEMINI_API_KEY is set
        if os.getenv("GEMINI_API_KEY"):
            print_test("GEMINI_API_KEY is set")
            
            # Test actual topic extraction
            if self.test_project_id:
                test_diff = """
                diff --git a/test.js b/test.js
                new file mode 100644
                +import React, { useState } from 'react';
                +const Component = () => {
                +  const [state, setState] = useState(0);
                +  return <div>{state}</div>;
                +};
                """
                
                try:
                    response = requests.post(
                        f"{self.backend_url}/api/projects/{self.test_project_id}/analyze-diff/",
                        json={
                            "diff_content": test_diff,
                            "repo_path": self.test_dir or "/tmp",
                            "change_id": f"test_{datetime.now().timestamp()}"
                        }
                    )
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("topics"):
                            print_test(f"Gemini extracted {len(result['topics'])} topics")
                        else:
                            print_test("Gemini returned no topics", False)
                    else:
                        print_test(f"Gemini analysis failed: {response.status_code}", False)
                except Exception as e:
                    print_test(f"Error testing Gemini: {e}", False)
        else:
            print_test("GEMINI_API_KEY not set!", False)
            print(f"  {YELLOW}Set it with: export GEMINI_API_KEY=your_key{RESET}")
            return False
        
        return True
    
    def cleanup(self):
        """Clean up test artifacts"""
        print_section("Cleanup")
        
        if self.test_dir and os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
                print_test(f"Cleaned up {self.test_dir}")
            except Exception as e:
                print_test(f"Failed to clean up: {e}", False)
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"\n{BLUE}{'='*50}{RESET}")
        print(f"{BLUE}    BRAINVIBE COMPONENT TEST SUITE{RESET}")
        print(f"{BLUE}{'='*50}{RESET}")
        
        # Track results
        results = {}
        
        # Run tests
        results['backend'] = self.test_backend_health()
        if results['backend']:
            results['api'] = self.test_api_endpoints()
        else:
            print(f"\n{RED}Skipping API tests - backend not running{RESET}")
            results['api'] = False
        
        results['cli_install'] = self.test_cli_installation()
        
        if results['cli_install'] and results['api']:
            results['cli_func'] = self.test_cli_functionality()
            if results['cli_func']:
                results['tracking'] = self.test_tracking()
            else:
                results['tracking'] = False
        else:
            print(f"\n{YELLOW}Skipping CLI functionality tests{RESET}")
            results['cli_func'] = False
            results['tracking'] = False
        
        if results['backend']:
            results['gemini'] = self.test_gemini_integration()
        else:
            results['gemini'] = False
        
        # Cleanup
        self.cleanup()
        
        # Print summary
        print_section("TEST SUMMARY")
        
        total = len(results)
        passed = sum(1 for v in results.values() if v)
        
        print(f"Results: {passed}/{total} tests passed\n")
        
        for test, passed in results.items():
            status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
            print(f"  {test:20} [{status}]")
        
        print()
        
        if passed == total:
            print(f"{GREEN}All tests passed! BrainVibe is working correctly.{RESET}")
        else:
            print(f"{YELLOW}Some tests failed. Check the output above for details.{RESET}")
            if not results['backend']:
                print(f"\n{YELLOW}Start the backend first:{RESET}")
                print(f"  cd backend && python manage.py runserver")
            if not results['cli_install']:
                print(f"\n{YELLOW}Install the CLI:{RESET}")
                print(f"  cd cli && pip install -e .")
            if not results['gemini']:
                print(f"\n{YELLOW}Set Gemini API key:{RESET}")
                print(f"  export GEMINI_API_KEY=your_key")
        
        return passed == total

if __name__ == "__main__":
    tester = BrainVibeTestSuite()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
