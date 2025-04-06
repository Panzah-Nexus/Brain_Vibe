import { simpleGit } from 'simple-git';
import * as fs from 'fs';
import * as path from 'path';
import inquirer from 'inquirer';

export interface InitOptions {
  path?: string;
  name?: string;
}

export async function initProject(options: InitOptions): Promise<void> {
  const projectPath = options.path || process.cwd();
  const absolutePath = path.resolve(projectPath);

  // Check if project is already initialized
  if (fs.existsSync(path.join(absolutePath, '.brainvibe'))) {
    throw new Error('Project is already initialized');
  }

  // Get project name if not provided
  let projectName = options.name;
  if (!projectName) {
    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'name',
        message: 'Enter project name:',
        default: path.basename(absolutePath)
      }
    ]);
    projectName = answers.name;
  }

  // Create .brainvibe directory
  const brainvibeDir = path.join(absolutePath, '.brainvibe');
  fs.mkdirSync(brainvibeDir, { recursive: true });

  // Create config file
  const config = {
    name: projectName,
    path: absolutePath,
    createdAt: new Date().toISOString()
  };
  fs.writeFileSync(
    path.join(brainvibeDir, 'config.json'),
    JSON.stringify(config, null, 2)
  );

  // Initialize git if not already initialized
  const git = simpleGit(absolutePath);
  if (!fs.existsSync(path.join(absolutePath, '.git'))) {
    await git.init();
  }

  // Create .brainvibeignore file if it doesn't exist
  const ignoreFilePath = path.join(absolutePath, '.brainvibeignore');
  if (!fs.existsSync(ignoreFilePath)) {
    fs.writeFileSync(
      ignoreFilePath,
      `# BrainVibe Ignore File
# Patterns listed here will be ignored by the BrainVibe tracking system
# Format: One pattern per line, similar to .gitignore

# Dependencies
node_modules
package-lock.json
yarn.lock
bower_components
vendor
.venv
env
venv
pip-wheel-metadata

# Build directories
dist
build
out
target

# Cache directories
.cache
__pycache__

# Documentation
*.md
*.txt
LICENSE*
README*

# Configuration files
.env*
*.config.js
tsconfig.json
jest.config.js

# IDE files
.vscode
.idea
.DS_Store

# Logs
logs
*.log

# Binary files
*.jpg
*.jpeg
*.png
*.gif
*.pdf
*.zip
*.exe
*.dll
`
    );
    console.log('Created .brainvibeignore file');
  }

  // Create git hooks directory
  const hooksDir = path.join(absolutePath, '.git', 'hooks');
  fs.mkdirSync(hooksDir, { recursive: true });

  // Create post-commit hook
  const postCommitHook = `#!/bin/sh
node ${path.join(__dirname, '..', 'hooks', 'post-commit.js')}
`;
  fs.writeFileSync(path.join(hooksDir, 'post-commit'), postCommitHook);
  fs.chmodSync(path.join(hooksDir, 'post-commit'), '755');

  console.log(`Project "${projectName}" initialized at ${absolutePath}`);
} 