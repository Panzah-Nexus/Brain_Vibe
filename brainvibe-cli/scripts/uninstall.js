const { execSync } = require('child_process');

// Unlink global installation
console.log('Unlinking global installation...');
execSync('npm unlink -g brainvibe-cli', { stdio: 'inherit' });

console.log('\nBrainVibe CLI has been uninstalled globally.'); 