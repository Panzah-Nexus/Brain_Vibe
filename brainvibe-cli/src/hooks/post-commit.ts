import * as fs from 'fs';
import * as path from 'path';
import { simpleGit } from 'simple-git';

export async function main(): Promise<void> {
  const projectPath = process.cwd();
  const absolutePath = path.resolve(projectPath);

  // Check if project is initialized
  if (!fs.existsSync(path.join(absolutePath, '.brainvibe'))) {
    console.error('Project not initialized. Run "brainvibe init" first.');
    process.exit(1);
  }

  // Initialize git
  const git = simpleGit(absolutePath);

  // Get latest commit
  const log = await git.log({ maxCount: 1 });
  const commit = log.latest;

  if (!commit) {
    console.error('No commit found');
    process.exit(1);
  }

  // Get or create graph data
  const graphPath = path.join(absolutePath, '.brainvibe', 'graph.json');
  let graph: Record<string, any> = {};
  if (fs.existsSync(graphPath)) {
    graph = JSON.parse(fs.readFileSync(graphPath, 'utf-8'));
  }

  // Update graph with commit info
  const commitData = {
    hash: commit.hash,
    message: commit.message,
    date: commit.date,
    author: commit.author_name
  };

  // Add commit to graph
  if (!graph.commits) {
    graph.commits = [];
  }
  graph.commits.push(commitData);

  // Save graph
  fs.writeFileSync(graphPath, JSON.stringify(graph, null, 2));

  console.log(`\nUpdated learning graph with commit: ${commit.message}`);
}

if (require.main === module) {
  main().catch((error: unknown) => {
    if (error instanceof Error) {
      console.error('Error in post-commit hook:', error.message);
    } else {
      console.error('Error in post-commit hook:', String(error));
    }
    process.exit(1);
  });
} 