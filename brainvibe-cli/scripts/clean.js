const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Directories to clean by default (excluding node_modules)
const dirsToClean = [
  'dist',
  'coverage'
];

// Clean directories
dirsToClean.forEach(dir => {
  const dirPath = path.join(__dirname, '..', dir);
  if (fs.existsSync(dirPath)) {
    console.log(`Removing ${dir}...`);
    fs.rmSync(dirPath, { recursive: true, force: true });
  }
});

// Only clean node_modules if explicitly passed as an argument
if (process.argv.includes('--deep')) {
  const nodeModulesPath = path.join(__dirname, '..', 'node_modules');
  if (fs.existsSync(nodeModulesPath)) {
    console.log('Removing node_modules...');
    fs.rmSync(nodeModulesPath, { recursive: true, force: true });
  }

  // Clean package-lock.json
  const packageLockPath = path.join(__dirname, '..', 'package-lock.json');
  if (fs.existsSync(packageLockPath)) {
    console.log('Removing package-lock.json...');
    fs.unlinkSync(packageLockPath);
  }
}

console.log('\nCleanup complete.'); 