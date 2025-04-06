import * as fs from 'fs';
import * as path from 'path';
import chokidar from 'chokidar';
import { simpleGit } from 'simple-git';
import fetch from 'node-fetch';
import * as os from 'os';

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

  // Check if git is initialized
  if (!(await git.checkIsRepo())) {
    console.log('Initializing git repository...');
    await git.init();
  }

  // Track files
  const watcher = chokidar.watch(absolutePath, {
    ignored: [
      /(^|[\/\\])\../, // dotfiles
      '**/node_modules/**',
      '**/.git/**',
      '**/.brainvibe/**',
      '**/venv/**',
      '**/__pycache__/**'
    ],
    persistent: true
  });

  let pendingChanges = new Set<string>();
  let analysisTimer: NodeJS.Timeout | null = null;

  // Handle file changes
  watcher
    .on('add', async (filePath) => {
      const relativePath = path.relative(absolutePath, filePath);
      console.log(`File ${relativePath} has been added`);
      pendingChanges.add(relativePath);
      await git.add(filePath);
      scheduleAnalysis();
    })
    .on('change', async (filePath) => {
      const relativePath = path.relative(absolutePath, filePath);
      console.log(`File ${relativePath} has been changed`);
      pendingChanges.add(relativePath);
      await git.add(filePath);
      scheduleAnalysis();
    })
    .on('unlink', async (filePath) => {
      const relativePath = path.relative(absolutePath, filePath);
      console.log(`File ${relativePath} has been removed`);
      pendingChanges.add(relativePath);
      await git.rm(filePath);
      scheduleAnalysis();
    });

  // Schedule analysis after a short delay
  function scheduleAnalysis() {
    if (analysisTimer) {
      clearTimeout(analysisTimer);
    }

    analysisTimer = setTimeout(async () => {
      if (pendingChanges.size === 0) return;

      try {
        console.log('Analyzing changes...');

        // Create a temporary commit to get the diff
        const tempCommitMsg = `TEMP: BrainVibe analysis ${new Date().toISOString()}`;
        await git.commit(tempCommitMsg, { '--allow-empty': null });

        // Get all diffs from the repository
        const diff = await git.diff(['HEAD~1', 'HEAD']);

        // Reset the temporary commit
        await git.reset(['HEAD~1']);

        // Send the diff to the backend for analysis
        await analyzeDiff(config.project_id, diff, Array.from(pendingChanges));

        // Clear pending changes
        pendingChanges.clear();
      } catch (error) {
        console.error('Error analyzing changes:', error);
      }
    }, 3000);  // Wait 3 seconds after the last change
  }

  async function analyzeDiff(projectId: string, diffContent: string, changedFiles: string[]) {
    try {
      const apiUrl = config.api_url || 'http://localhost:8000/api';

      // For each changed file, send a separate analysis request
      for (const filePath of changedFiles) {
        // Skip binary files and files with extensions we want to ignore
        if (isBinaryFile(filePath) || shouldIgnoreFile(filePath)) {
          console.log(`Skipping analysis for ${filePath}`);
          continue;
        }

        console.log(`Analyzing: ${filePath}`);

        const response = await fetch(`${apiUrl}/project/${projectId}/analyze_code_change/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            file_path: filePath,
            diff_content: diffContent,
            change_source: 'brainvibe_cli'
          }),
        });

        if (!response.ok) {
          console.error(`Error analyzing ${filePath}: ${response.statusText}`);
          continue;
        }

        const result = await response.json();
        if (result.topics_extracted > 0) {
          console.log(`Found ${result.topics_extracted} topics in ${filePath}`);
          result.topics.forEach((topic: any) => {
            console.log(`  - ${topic.title}`);
          });
        } else {
          console.log(`No new topics found in ${filePath}`);
        }
      }
    } catch (error) {
      console.error('Error sending analysis to backend:', error);
    }
  }

  function isBinaryFile(filePath: string): boolean {
    const binaryExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip', '.exe', '.dll'];
    return binaryExtensions.some(ext => filePath.toLowerCase().endsWith(ext));
  }

  function shouldIgnoreFile(filePath: string): boolean {
    const ignoreExtensions = ['.md', '.txt', '.gitignore', '.env', '.lock'];
    return ignoreExtensions.some(ext => filePath.toLowerCase().endsWith(ext));
  }

  // Handle process termination
  process.on('SIGINT', () => {
    console.log('\nStopping tracking...');
    watcher.close();
    process.exit(0);
  });

  console.log('\nBrainVibe is now tracking your code changes...');
  console.log('Press Ctrl+C to stop tracking.\n');
} 