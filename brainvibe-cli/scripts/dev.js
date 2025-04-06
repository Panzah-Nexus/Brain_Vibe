const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Create a test project directory if it doesn't exist
const testDir = path.join(__dirname, '..', 'test-project');
if (!fs.existsSync(testDir)) {
  console.log('Creating test project directory...');
  fs.mkdirSync(testDir);
}

// Build and install the CLI tool
console.log('Building and installing CLI tool...');
execSync('npm run install-global', { stdio: 'inherit' });

// Change to test project directory
process.chdir(testDir);

// Initialize test project if not already initialized
if (!fs.existsSync(path.join(testDir, '.brainvibe'))) {
  console.log('\nInitializing test project...');
  execSync('brainvibe init -n test-project', { stdio: 'inherit' });
}

// Start tracking changes
console.log('\nStarting change tracking...');
execSync('brainvibe track', { stdio: 'inherit' }); 