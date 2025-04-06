const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Compile TypeScript
execSync('tsc', { stdio: 'inherit' });

// Create the post-commit.js file
const hookContent = `#!/usr/bin/env node
require('${path.join(__dirname, '..', 'dist', 'hooks', 'post-commit.js')}');
`;

// Write the hook file
fs.writeFileSync(
  path.join(__dirname, '..', 'dist', 'hooks', 'post-commit.js'),
  hookContent
);

// Make it executable
fs.chmodSync(
  path.join(__dirname, '..', 'dist', 'hooks', 'post-commit.js'),
  '755'
); 