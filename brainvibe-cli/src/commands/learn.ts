import * as fs from 'fs';
import * as path from 'path';
import inquirer from 'inquirer';

export interface LearnOptions {
  path?: string;
}

export async function markLearned(topic: string, options: LearnOptions): Promise<void> {
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

  // Get or create graph data
  const graphPath = path.join(absolutePath, '.brainvibe', 'graph.json');
  let graph: Record<string, any> = {};
  if (fs.existsSync(graphPath)) {
    graph = JSON.parse(fs.readFileSync(graphPath, 'utf-8'));
  }

  // Get progress for topic
  const answers = await inquirer.prompt([
    {
      type: 'number',
      name: 'progress',
      message: `What percentage of "${topic}" have you learned?`,
      default: 100,
      validate: (value) => {
        if (value >= 0 && value <= 100) return true;
        return 'Please enter a number between 0 and 100';
      }
    }
  ]);

  // Update graph
  graph[topic] = {
    progress: answers.progress,
    lastUpdated: new Date().toISOString()
  };

  // Save graph
  fs.writeFileSync(graphPath, JSON.stringify(graph, null, 2));

  console.log(`\nUpdated learning progress for "${topic}" to ${answers.progress}%`);
} 