const { execSync } = require('child_process');

// Clean the project
console.log('Cleaning project...');
execSync('npm run clean', { stdio: 'inherit' });

// Install dependencies
console.log('\nInstalling dependencies...');
execSync('npm install', { stdio: 'inherit' });

// Run tests
console.log('\nRunning tests...');
execSync('npm test', { stdio: 'inherit' });

// Run linter
console.log('\nRunning linter...');
execSync('npm run lint', { stdio: 'inherit' });

// Format code
console.log('\nFormatting code...');
execSync('npm run format', { stdio: 'inherit' });

// Build project
console.log('\nBuilding project...');
execSync('npm run build', { stdio: 'inherit' });

console.log('\nProject is ready for publishing.'); 