const { execSync } = require('child_process');

// Prepare the project
console.log('Preparing project...');
execSync('npm run prepare', { stdio: 'inherit' });

// Publish to npm
console.log('\nPublishing to npm...');
execSync('npm publish', { stdio: 'inherit' });

console.log('\nPackage has been published successfully.'); 