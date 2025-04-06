const { execSync } = require('child_process');
const path = require('path');

// Build the project
console.log('Building project...');
execSync('npm run build', { stdio: 'inherit' });

// Install globally
console.log('\nInstalling globally...');
execSync('npm link', { stdio: 'inherit' });

console.log('\nBrainVibe CLI has been installed globally. You can now use it with the "brainvibe" command.'); 