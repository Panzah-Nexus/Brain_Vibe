import * as fs from 'fs';
import * as path from 'path';
import chokidar from 'chokidar';
import { simpleGit } from 'simple-git';
import fetch from 'node-fetch';
import * as os from 'os';

export interface TrackOptions {
  path?: string;
  interval?: number; // New option for commit interval in milliseconds
  ignoreFile?: string; // New option for custom ignore file
}

export async function trackChanges(options: TrackOptions): Promise<void> {
  const projectPath = options.path || process.cwd();
  const absolutePath = path.resolve(projectPath);
  // Default to 2 minutes (120000ms) if not specified
  const commitInterval = options.interval || 120000; 

  // Check if project is initialized
  if (!fs.existsSync(path.join(absolutePath, '.brainvibe'))) {
    throw new Error('Project not initialized. Run "brainvibe init" first.');
  }

  // Read config
  const config = JSON.parse(
    fs.readFileSync(path.join(absolutePath, '.brainvibe', 'config.json'), 'utf-8')
  );

  console.log(`Tracking changes in "${config.name}" at ${absolutePath}`);
  console.log(`Commit interval set to ${commitInterval / 1000} seconds`);

  // Initialize git
  const git = simpleGit(absolutePath);

  // Check if git is initialized
  if (!(await git.checkIsRepo())) {
    console.log('Initializing git repository...');
    await git.init();
  }

  // Get ignore patterns
  const ignorePatterns = getIgnorePatterns(absolutePath, options.ignoreFile);
  
  // Track files
  const watcher = chokidar.watch(absolutePath, {
    ignored: ignorePatterns,
    persistent: true
  });

  let pendingChanges = new Set<string>();
  let analysisTimer: NodeJS.Timeout | null = null;
  let commitTimer: NodeJS.Timeout | null = null;

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

  // Schedule analysis based on file save events (short delay)
  function scheduleAnalysis() {
    if (analysisTimer) {
      clearTimeout(analysisTimer);
    }

    // Only schedule periodic commits if we don't have one already
    if (!commitTimer) {
      schedulePeriodicCommit();
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

  // Schedule periodic commits based on the commitInterval
  function schedulePeriodicCommit() {
    commitTimer = setTimeout(async () => {
      if (pendingChanges.size > 0) {
        try {
          console.log('Performing scheduled analysis...');
          
          // Create a temporary commit to get the diff
          const tempCommitMsg = `TEMP: BrainVibe scheduled analysis ${new Date().toISOString()}`;
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
          console.error('Error performing scheduled analysis:', error);
        }
      }
      
      // Schedule the next periodic commit
      commitTimer = null;
      if (pendingChanges.size > 0) {
        schedulePeriodicCommit();
      }
    }, commitInterval);
  }

  async function analyzeDiff(projectId: string, diffContent: string, changedFiles: string[]) {
    try {
      const apiUrl = config.api_url || 'http://localhost:8000/api';

      // Filter out files that should be ignored for analysis
      const filesToAnalyze = changedFiles.filter(filePath => !shouldIgnoreForAnalysis(filePath));
      
      if (filesToAnalyze.length === 0) {
        console.log('No relevant files to analyze');
        return;
      }

      console.log(`Analyzing ${filesToAnalyze.length} out of ${changedFiles.length} changed files`);

      // For each changed file, send a separate analysis request
      for (const filePath of filesToAnalyze) {
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
    const binaryExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip', '.exe', '.dll', '.bin', '.so', '.dylib'];
    return binaryExtensions.some(ext => filePath.toLowerCase().endsWith(ext));
  }

  function shouldIgnoreForAnalysis(filePath: string): boolean {
    // Extended list of files to ignore for analysis
    const ignoreExtensions = [
      // Documentation files
      '.md', '.txt', '.pdf', '.doc', '.docx',
      // Config files
      '.gitignore', '.env', '.lock', '.toml', '.yml', '.yaml',
      // Package lock files
      'package-lock.json', 'yarn.lock', 'Gemfile.lock', 'poetry.lock',
      // Build artifacts
      '.min.js', '.min.css', '.map',
      // Log files
      '.log'
    ];
    
    // Check if file is in node_modules or similar directories
    const ignorePatterns = [
      'node_modules/', 'dist/', 'build/', 'target/',
      'vendor/', '.git/', '.cache/', '.brainvibe/'
    ];
    
    // Check extensions
    if (ignoreExtensions.some(ext => filePath.toLowerCase().endsWith(ext))) {
      return true;
    }
    
    // Check directory patterns
    return ignorePatterns.some(pattern => filePath.includes(pattern));
  }

  // Load custom ignore patterns from .brainvibeignore or specified file
  function getIgnorePatterns(projectPath: string, customIgnoreFile?: string): string[] | RegExp[] {
    const defaultIgnores = [
      /(^|[\/\\])\../, // dotfiles
      '**/node_modules/**',
      '**/.git/**',
      '**/.brainvibe/**',
      '**/venv/**',
      '**/__pycache__/**',
      '**/dist/**',
      '**/build/**',
      '**/coverage/**'
    ];
    
    // Check for custom ignore file
    const ignoreFile = customIgnoreFile 
      ? path.resolve(projectPath, customIgnoreFile)
      : path.join(projectPath, '.brainvibeignore');
    
    if (fs.existsSync(ignoreFile)) {
      try {
        const fileContent = fs.readFileSync(ignoreFile, 'utf-8');
        const customPatterns = fileContent
          .split('\n')
          .filter(line => line.trim() && !line.startsWith('#'))
          .map(line => `**/${line.trim()}/**`);
        
        return [...defaultIgnores, ...customPatterns];
      } catch (error) {
        console.warn(`Error reading ignore file: ${error}`);
      }
    }
    
    return defaultIgnores;
  }

  // Handle process termination
  process.on('SIGINT', () => {
    console.log('\nStopping tracking...');
    if (analysisTimer) clearTimeout(analysisTimer);
    if (commitTimer) clearTimeout(commitTimer);
    watcher.close();
    process.exit(0);
  });

  console.log('\nBrainVibe is now tracking your code changes...');
  console.log('Press Ctrl+C to stop tracking.\n');
} 