const { execSync } = require('child_process');

// Clean the project
console.log('Cleaning project...');
execSync('npm run clean', { stdio: 'inherit' });

// Note: We removed the "npm install" step that was causing the infinite loop
// The installation is already being handled by npm itself

// Skip tests and other steps during installation to fix dependency issues
console.log('\nSkipping tests, linting, and formatting during installation');

// Build project if package is already properly set up
try {
    console.log('\nTrying to build project...');
    execSync('npm run build', { stdio: 'inherit' });
    console.log('\nProject is ready for use.');
} catch (error) {
    console.log('\nSkipping build due to dependency issues.');
    console.log('You will need to run "npm run build" manually after fixing any dependency issues.');
} 