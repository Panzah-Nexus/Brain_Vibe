import * as fs from 'fs';
import * as path from 'path';
import { simpleGit } from 'simple-git';

export interface GraphOptions {
  path?: string;
}

export async function showGraph(options: GraphOptions): Promise<void> {
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

  // Initialize git
  const git = simpleGit(absolutePath);

  // Get commit history
  const log = await git.log();
  const commits = log.all;

  // Get learning graph data
  const graphPath = path.join(absolutePath, '.brainvibe', 'graph.json');
  let graph = {};
  if (fs.existsSync(graphPath)) {
    graph = JSON.parse(fs.readFileSync(graphPath, 'utf-8'));
  }

  console.log(`\nLearning Graph for "${config.name}"`);
  console.log('='.repeat(50));
  console.log('\nCommits:');
  commits.forEach((commit, index) => {
    console.log(`${index + 1}. ${commit.message} (${commit.date})`);
  });

  console.log('\nTopics:');
  Object.entries(graph).forEach(([topic, data]: [string, any]) => {
    if (topic !== 'commits') {
      console.log(`- ${topic}: ${data.progress}% complete`);
    }
  });
} 