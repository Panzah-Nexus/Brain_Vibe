import * as fs from 'fs';
import * as path from 'path';
import chokidar from 'chokidar';
import { simpleGit } from 'simple-git';

export interface TrackOptions {
  path?: string;
}

export async function trackChanges(options: TrackOptions): Promise<void> {
  const projectPath = options.path || process.cwd();
  const absolutePath = path.resolve(projectPath);

  // Check if project is initialized
  if (!fs.existsSync(path.join(absolutePath, '.brainvibe'))) {
    throw new Error('Project not initialized. Run "brainvibe init" first.');
  }

  // Read config
  const config = JSON.parse(
    fs.readFileSync(path.join(absolutePath, '.brainvibe', 'config.json'), 'utf-8')
  );

  console.log(`Tracking changes in "${config.name}" at ${absolutePath}`);

  // Initialize git
  const git = simpleGit(absolutePath);

  // Watch for changes
  const watcher = chokidar.watch(absolutePath, {
    ignored: [
      /(^|[\/\\])\../, // dotfiles
      '**/node_modules/**',
      '**/.git/**',
      '**/.brainvibe/**'
    ],
    persistent: true
  });

  watcher
    .on('add', async (filePath) => {
      console.log(`File ${filePath} has been added`);
      await git.add(filePath);
    })
    .on('change', async (filePath) => {
      console.log(`File ${filePath} has been changed`);
      await git.add(filePath);
    })
    .on('unlink', async (filePath) => {
      console.log(`File ${filePath} has been removed`);
      await git.rm(filePath);
    });

  // Handle process termination
  process.on('SIGINT', () => {
    console.log('\nStopping tracking...');
    watcher.close();
    process.exit(0);
  });
} 