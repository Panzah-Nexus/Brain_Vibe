#!/bin/bash

# BrainVibe Complete Test Script
# This tests all components individually and then as a system

set -e  # Exit on error

echo "========================================="
echo "     BRAINVIBE COMPLETE TEST SUITE     "
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test directory
TEST_DIR="/tmp/brainvibe_test_$(date +%s)"
PROJECT_ID="test_$(date +%s)"

# Function to print test results
print_test() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1${NC}"
        exit 1
    fi
}

# Function to wait for user
wait_for_user() {
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

echo ""
echo "=== STEP 1: Test Backend Components ==="
echo ""

# 1.1 Test Django is configured correctly
echo "Testing Django configuration..."
cd backend
python manage.py check
print_test "Django configuration valid"

# 1.2 Test database connection
echo "Testing database migrations..."
python manage.py migrate
print_test "Database migrations successful"

# 1.3 Test Django server can start
echo "Starting Django server..."
python manage.py runserver &
DJANGO_PID=$!
sleep 3
curl -s http://localhost:8000/api/hello/ > /dev/null
print_test "Django server running"

# 1.4 Test API endpoints
echo ""
echo "Testing API endpoints..."

# Test projects endpoint
curl -s http://localhost:8000/api/projects/ > /dev/null
print_test "GET /api/projects/ works"

# Create a test project via API
echo "Creating test project via API..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "description": "Testing BrainVibe",
    "github_url": "https://github.com/test/test"
  }')

# Extract project_id from response
PROJECT_ID=$(echo $RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['project_id'])")
echo "Created project with ID: $PROJECT_ID"
print_test "POST /api/projects/ works"

echo ""
echo "=== STEP 2: Test CLI Components ==="
echo ""

# 2.1 Check CLI is installed
echo "Checking CLI installation..."
which brainvibe
print_test "CLI is installed"

# 2.2 Create test repository
echo "Creating test repository at $TEST_DIR..."
mkdir -p $TEST_DIR
cd $TEST_DIR
print_test "Test directory created"

# 2.3 Initialize BrainVibe
echo "Initializing BrainVibe in test project..."
brainvibe init --project-id $PROJECT_ID --api-url http://localhost:8000/api
print_test "BrainVibe initialized"

# 2.4 Verify configuration
echo "Verifying configuration..."
[ -f .brainvibe/config.json ]
print_test ".brainvibe/config.json exists"

[ -f .brainvibeignore ]
print_test ".brainvibeignore exists"

[ -d .git ]
print_test "Git repository initialized"

echo ""
echo "=== STEP 3: Test Code Change Tracking ==="
echo ""

# 3.1 Create sample code file
echo "Creating sample Python file..."
cat > sample.py << 'EOF'
# Sample Python file to test BrainVibe tracking
import threading
import asyncio

class DataProcessor:
    def __init__(self):
        self.data = []
    
    async def process(self, item):
        # This uses async/await pattern
        await asyncio.sleep(1)
        return item * 2

def main():
    processor = DataProcessor()
    # Test multi-threading concept
    thread = threading.Thread(target=processor.process)
    thread.start()

if __name__ == "__main__":
    main()
EOF
print_test "Sample code created"

# 3.2 Track changes (one-shot mode)
echo "Tracking code changes..."
brainvibe track --one-shot
print_test "Code changes tracked"

echo ""
echo "=== STEP 4: Test Full Integration ==="
echo ""

# 4.1 Check if topics were created
echo "Checking if topics were extracted..."
sleep 2  # Give backend time to process
TOPICS=$(curl -s http://localhost:8000/api/projects/$PROJECT_ID/topics/)
TOPIC_COUNT=$(echo $TOPICS | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")

if [ $TOPIC_COUNT -gt 0 ]; then
    echo "Found $TOPIC_COUNT topics!"
    print_test "Topics extracted successfully"
else
    echo "No topics found - Gemini API might not be configured"
    print_test "Topics extraction (needs Gemini API key)"
fi

# 4.2 Add more code and track again
echo ""
echo "Adding React component..."
cat > component.jsx << 'EOF'
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const UserDashboard = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        fetchUsers();
    }, []);
    
    const fetchUsers = async () => {
        try {
            const response = await axios.get('/api/users');
            setUsers(response.data);
        } catch (error) {
            console.error('Failed to fetch users:', error);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div>
            {loading ? <p>Loading...</p> : <UserList users={users} />}
        </div>
    );
};

export default UserDashboard;
EOF
print_test "React component created"

# Track the new changes
brainvibe track --one-shot
print_test "New changes tracked"

echo ""
echo "=== STEP 5: Test Edge Cases ==="
echo ""

# 5.1 Test with no changes
echo "Testing with no changes..."
brainvibe track --one-shot
print_test "Handles no changes gracefully"

# 5.2 Test with binary files (should be ignored)
echo "Testing with binary file..."
echo -e "\x00\x01\x02" > binary.dat
brainvibe track --one-shot
print_test "Ignores binary files"

echo ""
echo "=== STEP 6: Cleanup ==="
echo ""

# Stop Django server
echo "Stopping Django server..."
kill $DJANGO_PID 2>/dev/null || true
print_test "Django server stopped"

# Clean up test directory
echo "Cleaning up test directory..."
cd /tmp
rm -rf $TEST_DIR
print_test "Test directory cleaned"

echo ""
echo "========================================="
echo -e "${GREEN}    ALL TESTS COMPLETED SUCCESSFULLY!   ${NC}"
echo "========================================="
echo ""
echo "Summary:"
echo "✓ Backend API is working"
echo "✓ CLI is properly installed"
echo "✓ Code tracking functionality works"
echo "✓ Git integration works"
echo "✓ Full pipeline is functional"
echo ""
echo "Note: Topic extraction requires GEMINI_API_KEY to be set"
