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